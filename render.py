from bs4 import BeautifulSoup
from glob import glob
import re
from datetime import datetime
import pytz
from lxml import etree

def run():
    csl = BeautifulSoup('<style xmlns="http://purl.org/net/xbiblio/csl" class="note" version="1.1"></style>', 'xml')

    parts = glob('coal-rjal/*')
    parts.sort()

    for part in parts:
        part_type = re.sub('coal-rjal/','', part)
        part_name = re.sub('\d-','',part_type)
        part_tag = BeautifulSoup(f'<{part_name}></{part_name}>', 'xml')
        i = 0
        for filename in glob(f'coal-rjal/{part_type}/**/*.xml', recursive=True):
            with open(filename, 'r') as f:
                tag = BeautifulSoup(f.read(), "xml")
                if part_name == 'macros':
                    csl.style.append(tag)
                elif part_name == 'locale':
                    sub_tags = tag.find_all('term')
                    for sub_tag in sub_tags:
                        part_tag.find(part_name).insert(i, sub_tag)
                else:
                    part_tag.find(part_name).insert(i, tag)
                i += 1
        if part_name != "macros":
            csl.style.append(part_tag)
    csl.style.locale['xml:lang'] = "en"
    terms = csl.find_all('term')
    csl.locale.append(BeautifulSoup('<terms></terms>', 'xml'))
    for term in terms:
        csl.style.terms.append(term)
    csl.info.append(BeautifulSoup(f'<updated>{datetime.now(pytz.utc).isoformat()}</updated>', 'xml'))

    with open('demo/coal-rjal.csl', 'w') as f:
        f.write(csl.prettify().replace('<terms></terms>',''))
        f.truncate()
    tree = etree.parse('demo/coal-rjal.csl')
    root = tree.getroot()
    for elem in root.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
    tree.write('demo/coal-rjal.csl')

if __name__ == "__main__":
    run()