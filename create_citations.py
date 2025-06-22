from pyzotero import zotero
import json
import os, os.path

def safe_open_w(path):
    # Open "path" for writing, creating any 
    # parent directories as needed.
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')

def transform_citation(num, keys):
    loc = ""
    label = ""
    for key in keys:
        citationItems = [{"id": "http://zotero.org/groups/5899098/items/" + key,
                            "locator":loc,
                            "label": label} for key in keys]
        citation = [
        { "citationID":f"{keys[0]}-{str(num)}",
        "citationItems": citationItems,
        "properties":{"noteIndex":num}
        },
        [],
        []
        ]
    return citation

def get_all_subcollections(lib : zotero.Zotero, key):
    collections = lib.collections_sub(key)
    name = lib.collection(key)['data']['name']
    sub_keys = {key : {"name":name, "children":[]}}
    for collection in collections:
        item_key = collection['key']
        if item_key != key:
            sub_keys[key]["children"] += [get_all_subcollections(lib, item_key)]
    return sub_keys

def genealogy(node, node_data):
    parent_node = node_data[node]['parent']
    if not parent_node:
        return [node]
    else:
        return genealogy(parent_node, node_data) + [node]

def get_node_data(library):
    node_data = {}
    for item in library:
        key = item['key']
        name = item['data']['name']
        parent = item['data']['parentCollection']
        node_data[key]= {'name':name, 'parent':parent}
    return node_data

def format(node, node_data):
    return {'name':node_data[node]['name']}

def add_node(tree, node, node_data):
    kin = genealogy(node, node_data)
    for node0 in kin:
        if not(node0 in tree.keys()):
            tree[node0] = format(node0, node_data)
        tree = tree[node0]

def hierarchy(library):
    node_data = get_node_data(library)
    h_library = {}
    for node in node_data.keys():
        add_node(h_library, node, node_data)
    return h_library

def list_key(d, l):
    print(d.keys())
    for i in l:
        d = d[i]
    return d

def get_citations(collection, library : zotero.Zotero, lib_id):
    items = library.collection_items(lib_id)
    n = 0
    used = set({})
    collection['citations'] = []    
    citations = collection['citations']
    for i in range(len(items)):
        item = items[i]
        keys = []
        if item['data']['relations'] != {}:
            relation = item['data']['relations']['dc:relation']
            
            keys = [os.path.basename(relation)]
        cite = item['data']['key']
        if cite not in used:
            keys = [cite] + keys
            citations += [transform_citation(n,keys)]
            for key in keys:
                used.add(key)
            print(used)
            n += 1

def citation_scan(h_lib, library,):
    sub = [key for key in h_lib.keys() if key not in ['name','citatons']]
    for key in sub:
        if key not in ['name', 'citations']:
            item = h_lib[key]
            get_citations(item, library, key)
            citation_scan(item, library)

def rename(d):
    keys = list(d.keys())
    for key in keys:
        if key not in ['name', 'citations']:
            if 'name' in d[key].keys():
                rename(d[key])
                name = d[key].pop('name')
                d[name] = d.pop(key)

def zotero_connection():
    zot = zotero.Zotero(5899098,'group', 'yShnOPQKvuZUKdFZvToqOSD4')
    library = zot.all_collections()
    h_lib = hierarchy(library)
    citation_scan(h_lib, zot)
    rename(h_lib)
    h_lib_dump = json.dumps(h_lib, indent=4)
    with open('demo/citations.json', 'w') as f:
        f.write(h_lib_dump)
        f.truncate()
        

if __name__ == "__main__":
    zotero_connection()

