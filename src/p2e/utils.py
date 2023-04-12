def normalize(value):
    """ Enleve tout les caracteres speciaux de la chaine value """
    value = value.strip()
    value = "".join(x for x in value if x.isalnum() or x == " ")
    return value

def stringtofilename(value):
    """ Recupere le nom d'un fichier. On suppose que ce nom ne contient pas d'espace. """
    value = "".join(x for x in value if x not in "[]:*?/")
    value = value.replace(" ", "\\")
    return value.split("\\")[-1]