from .args import Config
import re

def get_GUID(text: str) -> str:
    search = re.search(r'"entityGuid":"(.+?)"', text)
    if not search:
        raise Exception(f"GUID OF NAME NOT FOUND")
        
    return search.groups()[0]

def get_school_names(text: str) -> str:
    reg = re.finditer(r"<a class=\"search-result__link\" href=\"(.+?)\">", text)
    return [x.groups()[0].split("/")[-2] for x in reg]

config: Config = None

HELP = \
"""
Cry About It - The college admission prediction tool.

-h --help 
    Brings up this page.

-n --name school1 school2 ...
    Downloads the data of the schools listed.
-f --file schools.txt
    Downloads the data from the schools listed in the file separated by newlines.

-o --output out/
    Directory to write files in. The default is the root directory

-l --load obj.pkl
    Loads pre-trained models from disk.

-p --predict
    Predicts acceptance / rejection given GPA and SAT/ACT scores
-g --gpa GPA
    GPA parameter
-a --act ACT
    ACT score parameter
-s --sat SAT
    SAT score parameter
-i --instate [yes | no]
    In state or not
-m --major MAJOR
    selects major name
"""