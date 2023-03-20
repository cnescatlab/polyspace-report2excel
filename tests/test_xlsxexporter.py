import os,sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
print(sys.path)

from exportxlsx import Exportxlsx

def test_export():
    exporter = Exportxlsx("TESTXLSX")
    data = [["A1", "A2", "A3"], ["B1", "B2", "B3"]]
    exporter.add_sheet("EXPORT", data)
    exporter.export()
    assert(os.path.exists("TESTXLSX.xlsx"))
