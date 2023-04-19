import os, string

class Utils:

    " Enleve tout les caracteres speciaux de la chaine value."
    @staticmethod
    def normalize(value):
        value = value.strip()
        value = "".join(x for x in value if x.isalnum() or x == " ")
        return value

    " Recupere le nom d'un fichier."
    @staticmethod
    def stringtofilename(value):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        basename = os.path.basename(value)
        cleaned_basename = ''.join(c for c in basename if c in valid_chars)
        return cleaned_basename