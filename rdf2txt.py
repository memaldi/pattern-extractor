from rdflib import Graph

RDF_FILE="query-buildings.rdf"
OUTPUT_FILE="objects.txt"

f = open(OUTPUT_FILE, 'w')
g = Graph()
g.parse(RDF_FILE)

for s, p, o in g:
    f.write(o + ',\n')

f.close()
g.close()
