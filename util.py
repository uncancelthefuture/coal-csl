from bs4 import BeautifulSoup
from glob import glob
import os

files = glob('coal-rjal/2-locale/terms/*.xml')

for filename in files:

    with open(filename, 'r+') as f:
        soup = BeautifulSoup(f,'xml')
        term = soup.term
        children = soup.findChildren(recursive=True)
        for child in children:
            if child.string != None:
                text = child.text
                text = text.strip()
                child.string.replace_with(text)
        f.seek(0)
        f.write(str(term))
        f.truncate()

files = glob('coal-rjal/3-macros/render/*.xml')

for filename in files:
    l = len('coal-rjal/3-macros/render/')
    new_filename = filename[:l] + "render-" + filename[l:-8] + ".xml"
    os.rename(filename, new_filename)
