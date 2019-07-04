import os,sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
print(sys.path)

from exportcsv import Exportcsv

def test_export():
    exporter = Exportcsv("TESTCSV")
    data = [["A1", "A2", "A3"], ["B1", "B2", "B3"]]
    exporter.add_sheet("EXPORT", data)
    assert(os.path.exists("TESTCSV/EXPORT.csv"))

    export = open("TESTCSV/EXPORT.csv");
    csv = [line.replace("\n", "").split(";") for line in export.readlines()]
    assert(data == csv)