""" Nom du module: exportcsv
 Description: Ce module permet l'ecriture vers un fichier csv.
 Methodes et classes publiques:
        - exportxlsx
            __init__(filename)
            add_sheet(name, data, section="None")
            create_synthese(is_misra = False)
            export()
"""

# __________________________ IMPORT __________________________
import csv,os,shutil
from p2e.utils import Utils

# __________________ Definition de classes ___________________
class Exportcsv(object):
    """ Nom de la classe: Exportcsv
     Description: Permet l'export d'un ensemble de donnees dans un fichier csv"""

    def __init__(self, filename):
        self.sheets = dict()
        self.filename = filename
        if os.path.exists(self.filename):
            shutil.rmtree(self.filename)
        os.mkdir(self.filename)
        self.output = os.path.abspath(self.filename)
        
    @staticmethod
    def get_writer(path):
        return csv.writer(path,delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def add_sheet(self, name, data, section=None):
        """
                add_sheet
                Permet d'ajouter un feuille au fichier excel de sortie

                :param name: Nom que l'on souhaite donner a la feuille,
                    => si deja utilise, les donnees sont ajoutees a la fin
                :param data: Donnees a ajouter (liste a deux dimensions)
                    => La premiere ligne est consideree comme entete.
                :param section=None, si definie, une colone est ajoute sur chaque ligne, la valeur
                    de cette colonne est remplie avec  le contenu de "section", cela est utile
                    lorsque l'on ecrit plusieurs fois dans la meme feuille (pour distinguer "qui"
                    a ecrit).
            """
        # Si on a aucune donnee ou que le fichier est fermee, on stoppe l'execution
        if not data:
            return

        # On ajoute une colonne si besoin.
        if section is not None:
            data = [["#"] + data[0]] + [[section] + d for d in data[1:]]

        try:
            csv_path = os.path.join(self.output, Utils.normalize(name)+".csv")
        except FileNotFoundError:
            print("The specified output directory does not exist.")

        # On essaye de creer la feuille, si celle-ci existe deja l'exception DuplicateWorksheetName sera levee
        if not os.path.exists(csv_path):
            sheet = open(csv_path, "w", newline = "")
            # On garde les donnees en memoire, utile si on cherche a faire une synthese plus tard

            self.sheets[Utils.stringtofilename(name)] = [None, len(data), data, name]
            firstline = 0
        else:
            sheet = open(csv_path, "a", newline = "")
            firstline = self.sheets[Utils.stringtofilename(name)][1]
            data = data[1:]
            self.sheets[Utils.stringtofilename(name)][2] += data

        csv_writer = self.get_writer(sheet)

        # Ajout des donnees
        for line in range(firstline, firstline + len(data)):
            i = line - firstline
            data[i] = [d.strip() for d in data[i]]
            if data[i][-1] == '\n':
                del(data[i][-1])

            csv_writer.writerow(data[i])
        sheet.close()

    def create_synthese(self, is_misra=False):
        """ Permet la creation d'une feuille de synthese
        regroupant les donnees des autres feuilles """
        csv_path = os.path.join(self.output, "Synthese.csv")
        synth_sheet = open(csv_path, "w", newline = "")
        csv_writer = self.get_writer(synth_sheet)
        line = 0

        for sheet in self.sheets.values():
            if is_misra and "by file" not in sheet[3].lower() and sheet[3].strip() or not is_misra:
                if line == 0:
                    csv_writer.writerow(['file'] + sheet[2][0])
                    line = 1
                for row in sheet[2][1:]:
                    row = [d.strip() for d in row]
                    csv_writer.writerow([Utils.stringtofilename(sheet[3])] + row)
        synth_sheet.close()



    def export(self):
        """
            export
            Finalise l'ecriture et ferme le fichier.
            Doit etre appele avant la fin de l'execution (comme un close() sur un fichier)
        """
        self.output = None
