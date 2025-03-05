from bs4 import BeautifulSoup
from glob import glob

def run():
    csl = BeautifulSoup('<style xmlns="http://purl.org/net/xbiblio/csl" class="note" version="1.1"></style>', 'xml')

    parts = glob('coal-rjal/*')

    for part in parts:
        part_type = part.replace('coal-rjal/','')
        part_tag = BeautifulSoup(f'<{part_type}></{part_type}>', 'xml')
        i = 0
        for filename in glob(f'coal-rjal/{part_type}/**/*.xml', recursive=True):
            with open(filename, 'r') as f:
                tag = BeautifulSoup(f.read(), "xml")
                if part_type == 'macros':
                    csl.style.append(tag)
                else:
                    part_tag.find(part_type).insert(i, tag)
                i += 1
        if part_type != "macros":
            csl.style.append(part_tag)
    csl.style.locale['xml:lang'] = "en"
    csl.style.citation["et-al-min"]="4" 
    csl.style.citation["et-al-use"]="1"
    terms = csl.find_all('term')
    csl.locale.append(BeautifulSoup('<terms></terms>', 'xml'))
    for term in terms:
        csl.style.terms.append(term)

    with open('demo/coal-rjal.csl', 'w') as f:
        f.write(str(csl).replace('</terms><terms>','').replace('<terms/>',''))
        f.truncate()

if __name__ == "__main__":
    run()