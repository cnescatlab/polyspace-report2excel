
""" Nom du script: export-all
 Description: Ce script permet d'exporter un rapport Polyspace (html) vers un fichier excel
    L'utilisation est detaillée via `python export-all.py --help`
"""

# __________________________ IMPORT __________________________
import sys
import os

from p2e.exportcsv import Exportcsv
from p2e.exportxlsx import Exportxlsx
from p2e.HTMLReader import HTMLReader


def main():
    # ________________________ CONSTANTES ________________________
    ALL = "ALL"


    # ________________________ VARIABLES _________________________
    misra = False
    runtime = False
    polyversion = 18
    input_file = None
    output_folder = None
    reader = None
    tables = None


    # ____________________ LECTURE ARGUMENTS ______________________
    if len(sys.argv) < 3 or "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: p2e input.html output-folder/")
        print("")
        print("If you didn't download the package but cloned the repository,")
        print("Usage: python main.py input.html ouput-folder/")
        print("")
        print("Export all tables by default.")
        print("  use --misra to export only misra report")
        print("  use --runtime to export only runtime report, ignored if --misra")
        print("  use -y to skip overwriting warning")
        print("Designed for Polyspace 2018, use --poly14 to read report from Polyspace 2014")
        exit()
    else:
        if "--poly14" in sys.argv:
            polyversion = 14
        if "--misra" in sys.argv:
            misra = True
        elif "--runtime" in sys.argv:
            runtime = True

    input_file = sys.argv[1]
    output_folder = sys.argv[2]


    # ______________________ SCRIPT D'EXPORT ______________________
    try:
        os.mkdir(output_folder)
    except OSError:
        if "-y" not in sys.argv:
            print("This folder already exist or you do not have permission to write here.")
            print("Continue ? (will overwrite existing files) [y/N]")
            try:
                force_exec = input().lower()
                if force_exec not in ["y", "yes", "o", "oui"]:
                    print("Operation cancelled")
                    exit()
            except KeyboardInterrupt:
                exit()

    # Lecture du rapport Polyspace
    if ".rtf" in input_file:
        from p2e.RTFReader import RTFReader
        if not (misra or runtime):
            print("With  rtf file you should precise if you want to read MISRA or Runtime!")
            exit()
        reader = RTFReader(input_file, version=polyversion)
    else:
        reader = HTMLReader(input_file, version=polyversion)

    tables = reader.get_all_tables()
    reader.close()

    # Cas ou l'on souhaite seulement les rapports misra ou de runtime
    if misra or runtime:
        to_export = dict()
        if misra:
            for chapter in tables.keys():
                # On isole le chapitre misra
                if "misra" in chapter.lower():
                    to_export[chapter] = tables[chapter]
        elif runtime:
            for chapter in tables.keys():
                # On isole le chapitre run-time
                if "run-time" in chapter.lower() and "result" in chapter.lower():
                    to_export[chapter] = tables[chapter]
        tables = to_export

    for chapter in tables.keys():
        # ouverture du fichier de sortie (un fichier par chapitre)
        if not "--csv" in sys.argv:
            output = Exportxlsx(output_folder + "\\" + Exportxlsx.normalize(chapter))
        else:
            output = Exportcsv(output_folder + "\\" + Exportcsv.normalize(chapter))

        # Export de toute les tables dans les excel
        for table in tables[chapter]:
            output.add_sheet(
                Exportxlsx.stringtofilename(table['name'])[-31:],
                table['table'],
                table["section"]
            )

        # Dans le cas d'un rapport de run time ou misra
        # on ajoute un feuille de synthese
        if misra or runtime:
            output.create_synthese(misra)
        output.export()
