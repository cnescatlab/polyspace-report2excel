#!/usr/bin/env python3

""" Nom du module: HTMLReader
 Description: Ce module permet la lecture d'un HTML et l'extraction des
    tableaux qu'il contient.
 Methodes et classes publiques:
        - HTMLReader
            __init__(filename, version=18)
            get_all_tables()
"""

# __________________________ IMPORT __________________________
from html2text import HTML2Text

# ________________________ CONSTANTES ________________________

CHAR_BEGIN_CHAPTER = "Chapter"
CHAR_BEGIN_TABLE = "Table"
CHAR_SECTION = "## "
SEPARATOR_CELL = "|"
SEPARATOR_HEADER_LINE = "---|---"
SEPARATOR_SUB_CELL = "---"
PIPE = "|"
PIPE_ESCAPED = "PIPE"


# __________________ Definition de classes ___________________
class HTMLReader(object):

    """ Nom de la classe: HTMLReader
        Description: Cette classe lit un fichier HTML et permet
        l'extraction des tableaux qu'il contient """

    def __init__(self, filename, version=18):
        self.__filename = filename
        self._file = open(filename, "r")
        self.__version = version
        self._lines = None
        # Structure de cette variable definie dans la doctstring de get_all_tables
        self.__tables = dict()
        print("Reading report for polyspace 20" + str(version))

    def _read_lines(self):
        """ Converti un fichier HTML en MarkDown pour le rendre plus lisible """

        # Prise en compte des specificites de chaque version de polyspace
        # Une premiere conversion en Markdown est faite, le caractere | peux poser quelques soucis dans l'interpretation
        if self.__version == 18:
            self._lines = "".join(self._file.readlines()) \
                .replace(PIPE, PIPE_ESCAPED) \
                .replace("<td><p>", "<td>").replace("</p></td>", "</td>")
        else:
            self._lines = "".join(self._file.readlines()) \
                .replace(PIPE, PIPE_ESCAPED)

        read_html = HTML2Text()
        read_html.ignore_links = True
        read_html.ignore_tables = False
        read_html.pad_tables = True if self.__version == 18 else False
        # Evite les retour a la ligne trop frequent
        read_html.body_width = 100000
        self._lines = read_html.handle(self._lines).split("\n")

    def _detect_begin_table(self, line):
        """ Verifie dans le markdown si on trouve le debut d'un tableau """
        line += 1
        # Recherche ligne vide suivie d'une ligne non vide
        while line + 1 < len(self._lines) \
                and self._lines[line].strip() \
                and not self._lines[line + 1].strip():
            line += 1

        # On considere un debut de tableau si on trouve les headers de celui-ci
        is_begin_table = bool(line + 2 < len(self._lines)
                              and SEPARATOR_HEADER_LINE in self._lines[line + 2])
        return is_begin_table

    @staticmethod
    def __split_line(line):
        return line.split(SEPARATOR_CELL)

    @staticmethod
    def __remove_subcell(append_to_table):
        """ Supprime une sous-cellule d'un tableau (dans le code markdown)"""
        line = append_to_table.split(SEPARATOR_CELL)
        line[-1] = line[-1].replace(SEPARATOR_SUB_CELL, "")
        line[-2] = line[-1]
        line.pop()
        return "|".join(line)

    def __is_not_begin_chapter(self, line):
        # IMPROVEMENT: Une expression reguliere pourrait ameliorer la precision de la recherche
        return CHAR_BEGIN_CHAPTER not in self._lines[line]

    def __find_chapter(self, line):
        while line < len(self._lines) and self.__is_not_begin_chapter(line):
            line += 1
        return line

    def __next_chapter_or_table(self, line, current_section):
        while line < len(self._lines) \
                and not self._detect_begin_table(line) \
                and self.__is_not_begin_chapter(line):
            if self._lines[line].startswith(CHAR_SECTION):
                current_section = self._lines[line][len(CHAR_SECTION):]
            line += 1
        return line, current_section

    def __read_row(self, line, number_of_cols):
        append_to_table = self._lines[line]

        # On peux avoir des retours a la ligne dans une cellule, d'ou la boucle
        while line + 1 < len(self._lines) and len(
                self.__split_line(append_to_table)) < number_of_cols:

            line += 1
            append_to_table += "\n" + self._lines[line]

            # En terme de syntaxe HTML on a parfois deux celules en une, dans le rendu
            # cela ne se traduit par un simple retour a la ligne
            if SEPARATOR_SUB_CELL in append_to_table:
                append_to_table = self.__remove_subcell(append_to_table)
                self._lines[line + 1] += "|"

        # Sous cellule trouve sur la derniere cellule de la ligne d'un tableau
        if self._lines[line + 1].strip() == SEPARATOR_SUB_CELL:
            # Dans ce cas, tant qu'on trouve pas la ligne suivante d'un tableau on considere
            # le contenu comme etant de la cellule (il peux y avoir des retours a la ligne
            # dans cette cellule)
            while line + 1 < len(self._lines) \
                    and self._lines[line + 1].strip() \
                    and SEPARATOR_CELL not in self._lines[line + 1]:
                line += 1
                append_to_table += "\n" + self._lines[line]
                if SEPARATOR_SUB_CELL in append_to_table:
                    append_to_table = self.__remove_subcell(append_to_table)
        return line, append_to_table

    def __convert_to_output(self, datas):
        # On replace les caracteres | qui posaient probleme
        datas = self.__split_line(datas)
        datas = [d.replace(PIPE_ESCAPED, PIPE) for d in datas]
        return datas

    def __get_header_line(self, line):
        # La premiere ligne donnes les entetes, parfois il y a des retours a la ligne dans ces entetes
        header_line = self._lines[line]
        while line < len(self._lines) \
                and SEPARATOR_HEADER_LINE not in self._lines[line]:
            line += 1
            if SEPARATOR_HEADER_LINE not in self._lines[line]:
                header_line += self._lines[line]
        line += 1
        return line, header_line

    def _detect_end_table(self, line):
        return not(self.__version != 14 and self._lines[line + 1].strip() or self._lines[line].strip())

    def __extract_table(self, line, table, number_of_cols):
        # Un tableau se termine par 2 lignes vide (une seule dans polyspace 14...)
        while line < len(self._lines) \
                and not self._detect_end_table(line):
            (line, append_to_table) = self.__read_row(line, number_of_cols)
            table["table"].append(self.__convert_to_output(append_to_table))
            line += 1
        return line

    def __save_table(self, line, chapter, current_section):

        number_of_cols = 0
        header_line = ""

        # Si on trouve un tableau
        if line < len(self._lines) and self._detect_begin_table(line):
            # Initialisation de la sauvegarde
            line += 1
            table = {
                "name": self._lines[line],
                "section": current_section,
                "table": []
            }

            line += 1

            (line, header_line) = self.__get_header_line(line)

            # On determine le nombre de colones du tableau, utile pour les cellules avec retour a la ligne
            number_of_cols = len(self.__split_line(header_line))
            table["table"].append(self.__split_line(header_line))

            # Extraction du contenu tableau
            line = self.__extract_table(line, table, number_of_cols)

            # On sauvegarde tout...
            self.__tables[chapter].append(table)
        return line

    def __read_tables(self):
        """ Lit les tableaux d'un fichier HTML"""
        line = 0

        # Initialise en debut de boucle
        # Declaration selon le RNC: PY.DATA.Declaration
        chapter = None
        current_section = None

        while line < len(self._lines):
            # ETAPE 1: Recherche de chapitre
            line = self.__find_chapter(line)

            # Chapitre trouve
            if line < len(self._lines):
                # Enregistrement des infos generales sur le chapitre et initialisations.
                chapter = self._lines[line]
                self.__tables[chapter] = []
                current_section = None
                line += 1

                # Tant qu'on ne change pas de chapitre ou que l'on atteint pas la fin du fichier...
                while line < len(self._lines) and self.__is_not_begin_chapter(line):
                    # On cherche la fin du chapitre ou un tableau
                    (line, current_section) = self.__next_chapter_or_table(line, current_section)
                    line = self.__save_table(line, chapter, current_section)

    def get_all_tables(self):
        """
                Nom de la methode: get_all_tables
                Description: Retourne toutes les tableaux d'un fichier HTML classe par chapitre
                La variable est sous la structure suivante:
                tables[nom_du_chapitre] =
                    [
                        dict(
                            "name" : "Nom du premier tableau"
                            "table" : [[A1, A2], [B1, B2], [C1, C2]]
                        ),
                        dict(
                            "name" : "Nom du second tableau"
                            "table" : [[A1, A2], [B1, B2], [C1, C2]]
                        ),
                        ...
                    ]
            """
        if self._lines is None:
            self._read_lines()
        if len(self.__tables.keys()) == 0:
            self.__read_tables()
        return self.__tables

    def close(self):
        self._file.close()
