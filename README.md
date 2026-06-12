Étapes du flot de conception
============================

# 1. Ajouter la librairie Liberty

```python
# quelque part pendant l'initialisation
from coriolis.plugins import libertyParser
libertyParser.initLibertyLib("/path/to/liberty.lib")
```

Cette ligne permet de charger le fichier `liberty.lib` et d'ajouter les informations qu'il contient à Hurricane.

# 2. Modification du script de synthèse

Voici le script généré par Coriolis et modifié pour convenir au flot de conception, surtout pour que les noms de nets et
de cellules correspondent.

```ys
read_verilog -sv ./picorv32.v
hierarchy -check -top picorv32
synth            -top picorv32

# flatten
# On veut pouvoir garder la hiérarchie pour pouvoir faire un ODC partiel. Sinon, impossible de choisir quelle zone du
# circuit sera touchée par le parcours d'ODC

hierarchy -top picorv32
memory
dfflibmap -liberty /home/sherlock/coriolis-2.x/release/install/lib/python3.13/site-packages/pdks/gf180mcu/mcu9t5v0.lib
abc       -liberty /home/sherlock/coriolis-2.x/release/install/lib/python3.13/site-packages/pdks/gf180mcu/mcu9t5v0.lib
stat
clean

# On ajoute les attributs de conservation de noms à tous les nets et les cellules.
setattr -set keep 1 w:*
setattr -set keep 1 a:src

# L'option -attr permet de conserver les attributs/paramètres dans le BLIF
# L'option -param est cruciale si vos cellules ont des paramètres de simulation
write_blif -attr -param -iname picorv32.blif

# L'option -norename empêche Yosys de renommer les nets internes différemment du BLIF
# L'option -noexpr force Yosys à écrire des assignations structurelles (portes) plutôt que des expressions
write_verilog -norename -noexpr picorv32_circuit.v
```

# 3. Simulation

Il faut simuler le circuit avec le fichier `picorv32_circuit.v` pour faire la simulation post-synthèse.

## Code du Liberty to Json

Le code suivant permet de créer un fichier `lib_verilog.v` qui contient la description des cellules de base du PDK
chargé dans Coriolis.

```python
# Quelque part dans le doDesign.py
import re

from coriolis.CRL import getLibertyGroupFromCell
from coriolis.Hurricane import DataBase

db = DataBase.getDB()
root = db.getRootLibrary()

with open("lib_verilog.v", "w") as f:
    for lib in root.getLibraries():
        print("LIB :", lib.getName())
        for cell in lib.getCells():
            print(cell.getName())
            grp = getLibertyGroupFromCell(cell) # cell = Hurricane.Cell
            if grp is None:
                continue
            pins = grp.getGroups("pin.*")
            f.write(f"module {cell.getName()} (\n")
            first = True
            outputs = []
            external = set()
            for pin in pins:
                pin_name = re.search(r"\((.*)\)", pin.getGroupName()).group(1)
                external.add(pin_name)
                pin_direction = pin.getAttribute("direction").getValue()
                if pin_direction == "internal":
                    continue
                if not first:
                    f.write(",\n")
                else:
                    first = False
                f.write(f"    {pin_direction} wire {pin_name}")
                if pin_direction == "output":
                    outputs.append((pin_name, pin))
            f.write("\n")
            f.write(");\n")
            ff_grp = grp.getGroups("ff\\(.*")
            if len(ff_grp) >= 1:  # Attention, peut être ff et steering à la fois !!!! (reset...)
                ff_grp = ff_grp[0]
                match = re.search(r"\((\w*),?(\w*).*\)", ff_grp.getGroupName())
                out = None
                inv_out = None
                if match:
                    out, inv_out = match.groups()
                if out not in external:
                    f.write(f"    reg {out};\n")
                if inv_out not in external:
                    f.write(f"    reg {inv_out};\n")
                next_state = ff_grp.getAttribute("next_state").getValue().replace('"', "")
                clocked_on = ff_grp.getAttribute("clocked_on").getValue().replace('"', "")
                clean_clk = clocked_on.replace("(", "")
                clean_clk = clean_clk.replace(")", "")
                edge = "posedge" if "!" not in clean_clk else "negedge"
                clean_clk = clean_clk.replace("!", "")
                clear = ff_grp.getAttribute("clear")
                preset = ff_grp.getAttribute("preset")
                if clear is None:
                    f.write(f"    always @({edge} {clean_clk}) begin\n")
                    f.write(f"        {out} <= {next_state};\n")
                    f.write(f"        {inv_out} <= !({next_state});\n")
                else:
                    clear = clear.getValue().replace('"', "")
                    clean_clear = clear.replace("(", "")
                    clean_clear = clean_clear.replace(")", "")
                    clear_edge = "posedge" if "!" not in clean_clear else "negedge"
                    clean_clear = clean_clear.replace("!", "")
                    # preset = preset.getValue().replace('"', "")
                    # clean_preset = preset.replace("(", "")
                    # clean_preset = clean_preset.replace(")", "")
                    # preset_edge = "posedge" if "!" not in clean_preset else "negedge"
                    # # TODO: PRESET stuff
                    # clean_preset = clean_preset.replace("!", "")
                    f.write(f"    always @({edge} {clean_clk} or {clear_edge} {clean_clear}) begin\n")
                    f.write(f"        if ({clear}) begin\n")
                    f.write(f"            {out} <= 1'b0;\n")
                    f.write(f"            {inv_out} <= 1'b1;\n")
                    f.write( "        end else begin\n")
                    f.write(f"            {out} <= {next_state};\n")
                    f.write(f"            {inv_out} <= !({next_state});\n")
                    f.write( "        end\n")
                f.write( "    end\n")

            latch_grp = grp.getGroups("latch\\(.*")
            if len(latch_grp) >= 1:  # Attention, peut être ff et steering à la fois !!!! (reset...)
                latch_grp = latch_grp[0]
                match = re.search(r"\((\w*),?(\w*).*\)", latch_grp.getGroupName())
                out = None
                inv_out = None
                if match:
                    out, inv_out = match.groups()
                if out not in external:
                    f.write(f"    reg {out};\n")
                if inv_out not in external:
                    f.write(f"    reg {inv_out};\n")
                data_in = latch_grp.getAttribute("data_in").getValue().replace('"', "")
                enable = latch_grp.getAttribute("enable").getValue().replace('"', "")
                preset = latch_grp.getAttribute("preset")
                f.write( "    always @* begin\n")
                if preset is None:
                    f.write(f"        if ({enable}) begin\n")
                else:
                    preset = preset.getValue().replace('"', "")
                    f.write(f"        if ({preset}) begin\n")
                    f.write(f"            {out} = 1'b1;\n")
                    f.write(f"            {inv_out} = 1'b0;\n")
                    f.write(f"        end else if ({enable}) begin\n")
                f.write(f"            {out} = {data_in};\n")
                f.write(f"            {inv_out} = !({data_in});\n")
                f.write( "        end\n")
                f.write( "    end\n")

            for pin_name, pin in outputs:
                pin_function = pin.getAttribute("function")
                if pin_function is None:
                    continue
                pin_function = pin_function.getValue().replace('"', "")
                three_state = pin.getAttribute("three_state")
                if three_state is None:
                    f.write(f"    assign {pin_name} = {pin_function};\n")
                else:
                    three_state = three_state.getValue().replace('"', "")
                    f.write(f"    assign {pin_name} = {three_state} ? 1'bZ : {pin_function};\n")
            f.write("endmodule\n")
            f.write("\n")
```

C'est pas joli et il faut refactor ce code. Aussi, toutes les cellules ne sont pas compatibles pour le moment.

Il est possible de simuler avec le verilog fourni par les pdk, mais j'ai rencontré des problèmes qui m'empêchaient de
simuler correctement les circuits.

# 3. Lancer la recherche d'ODC

La dernière version du parcours d'observabilité est disponible sur la branche [NetXPlug-correspondance](https://github.com/etyloppihacilem/coriolis/tree/NetXPlug-correspondance).

## Calcul d'ODC de base

```python
# quelque part dans le doDesign.py
from coriolis import CRL

cell = CRL.Blif.load("picorv32") # le nom du top module à charger
# va charger picorv32.blif

from coriolis.plugins.odc.odc import odc

odc_util = odc(cell)

odc_util.computeODC()
odc_util.save_to_file(filename=f"{cell_name}.odc")
```

## Selection

Une CLI rudimentaire a été mise en place afin de faciliter la sélection des zones de cirtuit à explorer dans les modèles
hiérarchiques.

```
Commandes:
  run [output_name] : run odc on top level circuit. Will write in file output_name_odc.json
  select nb : selects circuit nb for odc.
  reset : resets selection.
  list : list instances in current circuit.
  help : print this message.
  exit : exit the selector.
  back : go back one level
  open nb : open circuit nb.
```

Pour entrer dans une cellules et voir ses sous cellules, il faut utiliser la commandes `open` avec l'index de la cellule
affiché. Pour remonter d'un niveau, il est possible d'utiliser la commande `back`.

La commande `select` permet de selectionner les bascules qui se trouvent dans un sous circuit. Elle peut être utilisée
sur plusieurs sous circuits, et la selection peut être annulée avec la commande `reset`.

L'utilisateur peut enfin lancer la recherche d'observabilité avec la commande `run`, suivie d'un nom de fichier de
sortie. Si une selection a été faite, seulement les bascules selectionées auront leur observabilité calculée. Sinon,
toutes les bascules du circuit seront explorées.

```python
# quelque part dans le doDesign.py
from coriolis import CRL

cell = CRL.Blif.load("picorv32") # le nom du top module à charger
# va charger picorv32.blif

from coriolis.plugins.odc.odc import ODCselector

ODCselector(cell)
```

## Commandes pour automatiser la selection

Il est possible de programmer une suite de commandes et de les exécuter sans intervention de l'utilisateur.

Il faudrait rajouter un système de sélection par regex plutôt qu'index, dans les cas où une nouvelle synthèse change
l'ordre des sous-circuits.

```python
cell = CRL.Blif.load("picorv32") # le nom du top module à charger
# va charger picorv32.blif

from coriolis.plugins.odc.odc import ODCselector

commands = [
    "open 1",
    "select 0",
    "run top_nouveau",
    "nets top_nouveau",
    "exit"
]
ODCselector(cell, commands=commands)
```

# 4. Extraire les motifs d'activité et construire l'arbre binaire

```
# python3 main.py --help

usage: main.py [-h] [-s] [--clk_signal CLK_SIGNAL] [--reset_signal RESET_SIGNAL] [-o OUTPUT] [-t TREE] odc_file simulation [simulation ...]

Extrait et organise les motifs d'activité

positional arguments:
  odc_file              Le fichier JSON qui contient les information d'observabilité
  simulation            Les fichiers .vcd de sortie de simulation à analyser

options:
  -h, --help            show this help message and exit
  -s, --sim_output      Crée un fichier JSON qui contient le contenu parsé des vcd (default: False)
  --clk_signal CLK_SIGNAL
                        Le nom du signal d'horloge dans les simulations (default: clk)
  --reset_signal RESET_SIGNAL
                        Le nom du signal de reset dans les simulations (default: resetn)
  -o, --output OUTPUT   Le fichier JSON de sortie où les motifs seront écrits (default: pattern.json)
  -t, --tree TREE       Le fichier JSON de sortie où les motifs seront écrits (default: None)
```


```bash
python3 main.py -o motifs_dactivite.json -t arbre.json picorv32_complete_odc.json t.vcd
```

- `motifs_dactivite.json` : Le fichier de sortie où seront écrits les motifs d'activité.
- `arbre.json` : Le fichier de sortie où sera écrit l'arbre binaire de Clock Gating.
- `picorv32_complete_odc.json` : Le fichier où sont les informations des fonctions d'observabilité du circuit.
- `t.vcd` : Le fichier de sortie de simulation où l'utilisation doit être représentative. On peut mettre plusieurs
fichiers de simulation pour avoir des motifs plus variés.

Si le signal de clock ou le signal de reset ne s'appellent pas comme les valeurs par défaut, on peut utiliser les
arguments pour changer la recherche.
