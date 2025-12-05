import xml.etree.ElementTree as ET
# import pandas as pd


# fp = r"C:\Local Repo\ATEM Macro Edit\ATEM SS Animated_01.XML"
# fp = r'C:\Local Repo\ATEM-Animated-Macro-Generator\export_eo.xml'
fp = r'macro_export.xml'

def addMacroPool(fp):
    with open(fp, 'r') as f:
        allLines = f.read()
    tag = 'MacroPool'
    allLines = f'{" "*4}<{tag}>\n{allLines}\n{" "*4}</{tag}>'
    return allLines

# s = addMacroPool(fp)
with open(fp, 'r') as f:
    allLines = f.read()
s = allLines

tree = ET.ElementTree(ET.fromstring(s))
macros = tree.getroot()

for macro in macros:
    print(macro.tag, macro.attrib)
    for op in macro:
        print(op.tag, op.attrib)

