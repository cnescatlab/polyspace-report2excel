
""" Nom du script: export-all
 Description: Ce script permet d'exporter un rapport Polyspace (html) vers un fichier excel
    L'utilisation est detaillée via `python export-all.py --help`
"""

# __________________________ IMPORT __________________________
import sys
import os
import argparse

from p2e.exportcsv import Exportcsv
from p2e.exportxlsx import Exportxlsx
from p2e.HTMLReader import HTMLReader

def handling_warning(args):
    if os.path.exists(args.output_folder):
            print(f"WARNING: Output files in {args.output_folder} will be overwritten.")
            user_input = input("Do you want to continue? [y/n] ")
            if user_input.lower() != "y":
                print("Exiting. Operation cancelled.")
                sys.exit(0)
            else:
                create_folder(args)
    else:
        create_folder(args)

def create_folder(args):
    print(f"Output folder {args.output_folder} does not exist. Creating it.")
    try:
        os.makedirs(args.output_folder, exist_ok=True)
    except PermissionError:
        print(f"Permission denied. Exiting.")
        print(f"You do not have permission to create the output folder {args.output_folder}.")
        print(f"Try running the script with sudo or as administrator.")
        print("Exiting. Operation cancelled.")
        sys.exit(1)

def handle_arguments():
    parser = argparse.ArgumentParser(description="Export tables from Polyspace HTML report")
    parser.add_argument("input_file", help="input HTML file path")
    parser.add_argument("output_folder", help="output folder path")
    parser.add_argument("--misra", action="store_true", help="export only misra report")
    parser.add_argument("--runtime", action="store_true", help="export only runtime report, ignored if --misra")
    parser.add_argument("-y", "--yes", action="store_true", help="skip overwriting warning")
    parser.add_argument("--poly14", action="store_true", help="read report from Polyspace 2014")
    parser.add_argument("--csv", action="store_true", help="export data in CSV instead of xlsx")
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} does not exist.")
        sys.exit(1)

    if not args.yes:
        handling_warning(args)
    else:
        create_folder(args)
    return args

def main():
    # ________________________ CONSTANTES ________________________
    ALL = "ALL"


    # ________________________ VARIABLES _________________________
    reader = None
    tables = None

    # Assigning arguments to variables
    args = handle_arguments()
    input_file = args.input_file
    output_folder = args.output_folder
    polyversion = 18 if not args.poly14 else 14
    misra = args.misra
    runtime = args.runtime
    csv = args.csv

    # ______________________ SCRIPT D'EXPORT ______________________
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
        if not csv:
            output = Exportxlsx(os.path.join(output_folder, Exportxlsx.normalize(chapter)))
        else:
            output = Exportcsv(os.path.join(output_folder, Exportcsv.normalize(chapter)))

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

if __name__ == "__main__":
    main()