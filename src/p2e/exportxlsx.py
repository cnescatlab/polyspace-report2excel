""" Nom du module: exportxlsx
 Description: Ce module permet l'ecriture vers un fichier excel.
 Methodes et classes publiques:
        - exportxlsx
            __init__(filename)
            normalize(value)
            stringtofilename(value)
            add_sheet(name, data, section="None")
            create_synthese(is_misra = False)
            export()
"""

# __________________________ IMPORT __________________________
import xlsxwriter as xwriter


# __________________ Definition de classes ___________________
class Exportxlsx(object):
    """ Nom de la classe: Exportxlsx
     Description: Permet l'export d'un ensemble de donnees dans un fichier excel"""

    @staticmethod
    def normalize(value):
        """ Enleve tout les caracteres speciaux de la chaine value """
        value = value.strip()
        value = "".join(x for x in value if x.isalnum() or x == " ")
        return value

    @staticmethod
    def stringtofilename(value):
        """ Recupere le nom d'un fichier. On suppose que ce nom ne contient pas d'espace. """
        value = "".join(x for x in value if x not in "[]:*?/")
        value = value.replace(" ", "\\")
        return value.split("\\")[-1]

    def __init__(self, filename):
        self.sheets = dict()
        self.filename = filename
        self.output = xwriter.Workbook(self.filename + ".xlsx")



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
        if self.output is None:
            raise Exception("Output file is closed")

        # On ajoute une colonne si besoin.
        if section is not None:
            data = [["#"] + data[0]] + [[section] + d for d in data[1:]]

        # On essaye de creer la feuille, si celle-ci existe deja l'exception DuplicateWorksheetName sera levee
        try:
            sheet = self.output.add_worksheet(self.stringtofilename(name))
            # On garde les donnees en memoire, utile si on cherche a faire une synthese plus tard
            self.sheets[self.stringtofilename(name)] = [sheet, len(data), data, name]
            firstline = 0
        except xwriter.exceptions.DuplicateWorksheetName:
            sheet = self.sheets[self.stringtofilename(name)][0]
            firstline = self.sheets[self.stringtofilename(name)][1]
            data = data[1:]
            self.sheets[self.stringtofilename(name)][2] += data

        # Cette variable determine la longueur maximale d'une case, cela est utilise pour mettre en forme les cellules
        # dans excel
        col_width = [0 for i in range(len(data[0]))]
        bold = self.output.add_format({'bold': True})

        # Ajout des donnees
        for line in range(firstline, firstline + len(data)):
            i = line - firstline
            data[i] = [d.strip() for d in data[i]]

            sheet.write_row(line, 0, data[i], cell_format=(bold if line == 0 else None))

            # Calcul de la taille des colonnes
            try:
                col_width = [max(col_width[j], len(data[i][j]) + 1) for j in range(len(col_width))]
            except IndexError:
                print("Error while formating cells")
                for d in data:
                    print(d)
        # Formatage des colonnes
        for i in range(len(col_width)):
            sheet.set_column(i, i, col_width[i])

    def create_synthese(self, is_misra=False):
        """ Permet la creation d'une feuille de synthese
        regroupant les donnees des autres feuilles """
        synth_sheet = self.output.add_worksheet("Synthese")
        line = 0
        bold = self.output.add_format({'bold': True})

        for sheet in self.sheets.values():
            if is_misra and "by file" not in sheet[3].lower() and sheet[3].strip() or not is_misra:
                if line == 0:
                    synth_sheet.write_row(line, 0, ['file'] + sheet[2][0], cell_format=bold)
                    line = 1
                for row in sheet[2][1:]:
                    row = [d.strip() for d in row]
                    synth_sheet.write_row(line, 0, [self.stringtofilename(sheet[3])] + row)
                    line += 1



    def export(self):
        """
            export
            Finalise l'ecriture et ferme le fichier.
            Doit etre appele avant la fin de l'execution (comme un close() sur un fichier)
        """
        self.output.close()
        self.output = None
