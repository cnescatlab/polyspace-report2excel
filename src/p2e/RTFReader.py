#!/usr/bin/env python3

""" Nom du module: RTFReader
 Description: Ce module permet la lecture d'un RTF et l'extraction des
    tableaux qu'il contient.
 Methodes et classes publiques:
        - HTMLReader
            __init__(filename, version=18)
            get_all_tables()
"""

# __________________________ IMPORT __________________________
from p2e import HTMLReader
from striprtf.striprtf import rtf_to_text

# ________________________ CONSTANTES ________________________

HTMLReader.CHAR_BEGIN_CHAPTER = "Chapter"
HTMLReader.CHAR_BEGIN_TABLE = "Table"
HTMLReader.CHAR_SECTION = "## "
HTMLReader.SEPARATOR_CELL = "|"
HTMLReader.SEPARATOR_HEADER_LINE = "|"
HTMLReader.SEPARATOR_SUB_CELL = "NO_SUBCELL_POSSIBLE"
HTMLReader.PIPE = "|"
HTMLReader.PIPE_ESCAPED = "PIPE"


# __________________ Definition de classes ___________________
class RTFReader(HTMLReader.HTMLReader):
    def __init__(self, filename, version=None):
        super().__init__(filename, version=version)

    def _read_lines(self):
        lines = ""
        for line in self._file.readlines():
            lines = lines + line + "\n"





        lines = lines.replace(HTMLReader.PIPE, HTMLReader.PIPE_ESCAPED)

        self._lines = rtf_to_text(lines).split("\n")




    def _detect_end_table(self, line):
        return not self._lines[line].strip()

    def _detect_begin_table(self, line):
        return line+1<len(self._lines) and HTMLReader.CHAR_BEGIN_TABLE in self._lines[line+1]