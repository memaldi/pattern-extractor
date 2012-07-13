import re
import rdflib
from rdflib import Graph
from rdflib import plugin

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

PATTERN_FILE='wordFreq_concepts_friday.csv'
SENTENCES_FILE='objects.txt'
#ONTOLOGY='ontologies/ontosem.owl'
ONTOLOGY='ontologies/pattern-ext.rdf'

input_f = open(PATTERN_FILE)
pattern_dict = {}
pattern_list = []
g = Graph()
g.parse(ONTOLOGY)

line_count = 0
classes_dict = {}

for line in input_f:
    if (line_count != 0):
        line_list = line.split(',')
        word = line_list[0]
        upper_pattern = line_list[3]
        upper_pattern = upper_pattern.split(' ')[0]
        if (upper_pattern is not '') and (upper_pattern is not '-'):
            superclass_list = []
            pattern_dict[word.lower()] = upper_pattern
            query = '''SELECT ?superClasses WHERE { <http://morpheus.cs.umbc.edu/aks1/ontosem.owl#''' + upper_pattern.lower() + '''> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?superClasses .
}'''
            end = False
            qres = g.query(query)
            while(not end):
                if (len(qres.result) > 0):
                    superclass = qres.result[0][0]
                    superclass_list.append(superclass)
                    query = '''SELECT ?superClasses WHERE { <''' + superclass + '''> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?superClasses .
}'''
                    qres = g.query(query)
                else:
                    end = True
            classes_dict[upper_pattern] = superclass_list
    line_count = line_count + 1

#print pattern_dict.keys()
input_f.close()

sentences_f = open(SENTENCES_FILE)
output_string = ''

for line in sentences_f:
    pattern=line
    sentence_words = line.split(' ')
    if line != ',\n':
        new_line = line
        for word in sentence_words:
            word = word.replace('\n', '')
            word = word.replace(',', '')
            #print word
            word_c = word.lower()
            m = re.search('\w+[0-9]+', word_c)
            if m != None:
                new_line = new_line.replace(word, '<b>[Code]</b>')
                new_line = new_line + '<br/><b>[' + word + '] a ' + 'Code' + '</b></br>'
                pattern = pattern.replace(word, '<b>[Code]</b>')
                superclass_list = []
                upper_pattern = 'Code'
                pattern_dict[word.lower()] = upper_pattern
                query = '''SELECT ?superClasses WHERE { <http://morpheus.cs.umbc.edu/aks1/ontosem.owl#''' + upper_pattern.lower() + '''> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?superClasses .
}'''
                end = False
                qres = g.query(query)
                while(not end):
                    if (len(qres.result) > 0):
                        superclass = qres.result[0][0]
                        superclass_list.append(superclass)
                        query = '''SELECT ?superClasses WHERE { <'''+superclass+'''> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?superClasses .
}'''
                        qres = g.query(query)
                    else:
                        end = True
                superclass_str = ''
                for superclass, i in zip(superclass_list, range(0, len(superclass_list))):
                    delimiter = '|'
                    for count in range(0,len(superclass_list)-i):
                        delimiter = delimiter + '--'
                    superclass_str = superclass_str + delimiter + str(superclass) + '</br>'
                    new_line = new_line + '</br>' + superclass_str + '</br>'
            elif word_c.lower() in pattern_dict.keys():
                #print word
                #new_line = line.replace(word, '<b>['+pattern_dict[word]+']</b>')
                #print new_line
                #new_line = new_line.replace(word, '<b>['+pattern_dict[word.lower()]+']</b>')
                #new_line = new_line + '<br/><b>[' + word + '] a ' + pattern_dict[word.lower()] + '</b></br>'
                end_str = ''
                if pattern_dict[word.lower()] in classes_dict.keys():
                    superclass_str = ''
                    for item, i in zip(classes_dict[pattern_dict[word.lower()]], range(0,len(classes_dict[pattern_dict[word.lower()]]))):
                        delimiter = '|'
                        for count in range(0,len(classes_dict[pattern_dict[word.lower()]])-i):
                            delimiter = delimiter + '--'
                        superclass_str = superclass_str + delimiter + str(item) + '</br>'
                        superclass = item
                    #new_line = new_line + '</br>' + str(classes_dict[pattern_dict[word]]) + '</br>'
                    end_str = end_str + '</br>' + superclass_str + '</br>'
                pattern = pattern.replace(word, '<b>['+superclass+']</b>')
                new_line = new_line.replace(word, '<b>['+superclass+']</b>')
                new_line = new_line + '<br/><b>[' + word + '] a ' + pattern_dict[word.lower()] + '</b></br>'
                new_line = new_line + end_str
        output_string = output_string + new_line[0:len(new_line)-2] + '</br></br>'
        pattern_list.append(pattern)

print 'There are ' + str(len(pattern_list)) + ' different patterns.'
sentences_f.close()
html_file = open('output.html', 'w')
html_file.write(output_string)
html_file.close()
