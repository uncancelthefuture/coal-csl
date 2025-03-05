var styleID = "coal-rjal";

// Get the citations that we are supposed to render, in the CSL-json format
var xhr = new XMLHttpRequest();
var citations;
var citations0 = {};
var dummy = 1;
const levelregex = /[\d+\.{1}]+/;

xhr.open('GET', 'citations.json', false);
xhr.send(null);
var citations = JSON.parse(xhr.responseText);

var headings = [];

 function t(x){
    if(x === 'citations'){
        return false;
    };
    return true;
};

function p(object, key){
    headings = headings.concat([key])
    citations0[key] = object[key]['citations'];
};

function recursive(object, key_condition, process) {
    for (var key of Object.keys(object)) {
        if(key_condition(key)){
            process(object, key);
            recursive(object[key],key_condition, process);
        };
    };
}

recursive(citations, t, p);

function getlevel(s){
    match_s = s.match(levelregex)|| ['0'];
    return match_s[0].split(".")
};

headings.sort(function(a, b){
    var match_a = getlevel(a)
    var match_b = getlevel(b)
    var la = match_a.length
    var lb = match_b.length
    var l = Math.min(la, lb);
    for(var i = 0, l = match_a.length; i < l; i+=1){
        var var_a = parseInt(match_a[i]);
        var var_b = parseInt(match_b[i]);
        if (var_a - var_b != 0){
            return var_a - var_b;
        }
    }
    // a before b if negative
    // b before a if positive
    return la-lb;
});

citediv = document.getElementById('cite-div')
xhr.open('GET', styleID + '.csl', false);
xhr.send(null);

var style = xhr.responseText;
var itemsArray = [];
xhr.open('GET', 'items.json', false);
xhr.send(null);

citations = citations0 

itemsArray = itemsArray.concat(JSON.parse(xhr.responseText));
var items = {};
for (item of itemsArray) {
    items[item.id] = item;
};
console.log(citations0)


// Initialize a system object, which contains two methods needed by the
// engine.
citeprocSys = {
    // Given a language tag in RFC-4646 form, this method retrieves the
    // locale definition file.  This method must return a valid *serialized*
    // CSL locale. (In other words, an blob of XML as an unparsed string.  The
    // processor will fail on a native XML object or buffer).
    retrieveLocale: function (lang) {
        xhr.open('GET', 'locales-' + lang + '.xml', false);
        xhr.send(null);
        return xhr.responseText;
    },

    // Given an identifier, this retrieves one citation item.  This method
    // must return a valid CSL-JSON object.
    retrieveItem: function (id) {
        return items[id];
    }
};

// Given the identifier of a CSL style, this function instantiates a CSL.Engine
// object that can render citations in that style.
function getProcessor() {
    // Instantiate and return the engine
    var citeproc = new CSL.Engine(citeprocSys, style);
    return citeproc;
};

function runOneStep(idx, name) {
    var citeDiv = document.getElementById(name);
    var citationParams = citations[name][idx];
    if(!(citationParams[0].citationItems[0].id in items)){
        return runRenderBib(idx + 1, name);
    }

    var citationStrings = citeproc.processCitationCluster(citationParams[0], [], [])[1];
    for (var citeInfo of citationStrings) {
        // Prepare node
        var newNode = document.createElement("div");
        newNode.setAttribute("id", "n" + citeInfo[2]);
        newNode.setAttribute("class", "hanging");
        newNode.innerHTML = citeInfo[1];
        // Try for old node
        var oldNode = document.getElementById("node-" + citeInfo[2]);
        if (oldNode) {
            citeDiv.replaceChild(newNode, oldNode);
        } else {
            citeDiv.appendChild(newNode);
        }
    }
    runRenderBib(idx + 1, name);
};

function runRenderBib(idx, name) {
    if (idx === citations[name].length) {
        return 0;
    } else {
        runOneStep(idx, name);
    }
};

var citeproc = getProcessor();

for (var i in headings) {
    divname = headings[i]
    var node = document.createElement('div');
    node.setAttribute('id', divname);
    citediv.appendChild(node);
    var level = getlevel(divname);
    level = (level.length + 1).toString();
    headernode = document.createElement("h"+level);
    headernode.innerHTML = divname
    node.appendChild(headernode);
    runRenderBib(0, divname);
};
