from rdflib import Graph, URIRef
from graphviz import Digraph

g = Graph()
g.parse('./design_build_test.xml', 'rdfxml')

dot = Digraph('design_build_test')

cur_sub = ''
cur_class = ''

edges = []
nodes = []
node_dict = {}

shape_dict = {

'Activity' : 'box',
'Plan' : 'polygon',
'Agent' : 'diamond',
'Association' : 'pentagon',
'Usage' : 'trapezium',

}


for (s, p, o) in sorted(g):

    # Chomp the nodes strings
    s = s.strip()
    p = p.strip()
    o = o.strip()

    # print '%s %s %s' % (s, p ,o)

    # If new subject
    if (cur_sub != s):

        cur_sub = s

        for value in g.objects(URIRef(s), URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')):

            cur_class = value.split('#')[-1] #Track the current class

            print 'Creating a ' + cur_class + ' node.'

            if cur_class == 'Agent' or cur_class =='Plan':
                temp_label = s.split('/')[-1]

            elif cur_class == 'Implementation' or cur_class == 'Activity' or cur_class == 'Association' or cur_class == 'Usage' or cur_class == 'Test':
                temp_label = '/'.join(s.split('/')[-2:])

            else:
                temp_label = s

            nodes += [s]
            node_dict[s] = s.split(':')[-1]

            if cur_class in shape_dict.keys():
                dot.node(s.split(':')[-1], temp_label, shape = shape_dict[cur_class]) # Createt a new node in the Graphviz

            else:
                dot.node(s.split(':')[-1], temp_label) # Createt a new node in the Graphviz


    if p == 'http://www.w3.org/ns/prov#wasDerivedFrom':
        edges += [(s, o, 'wasDerivedFrom')]

    elif p == 'http://www.w3.org/ns/prov#wasGeneratedBy':
        edges += [(s, o, 'wasGeneratedBy')]

    elif p == 'http://www.w3.org/ns/prov#qualifiedUsage':
        edges += [(s, o, 'qualifiedUsage')]

    elif p == 'http://www.w3.org/ns/prov#qualifiedAssociation':
        edges += [(s, o, 'qualifiedAssociation')]

    elif p == 'http://www.w3.org/ns/prov#entity':
        edges += [(s, o, 'entity')]

    elif p == 'http://www.w3.org/ns/prov#hadRole':
        edges += [(s, o, 'hadRole')]

    elif p == 'http://www.w3.org/ns/prov#agent':
        edges += [(s, o, 'agent')]

    elif p == 'http://www.w3.org/ns/prov#hadPlan':
        edges += [(s, o, 'hadPlan')]

for edge in edges:

    if edge[0] not in nodes:

        print 'Added a new unknown node'

        dot.node(edge[0].split(':')[-1], '/'.join(edge[0].split('/')[-2:]))
        node_dict[edge[0]] = edge[0].split(':')[-1]

    if edge[1] not in nodes:

        print 'Added a new unknown node'

        node_dict[edge[1]] = edge[1].split(':')[-1]
        dot.node(edge[1].split(':')[-1], '/'.join(edge[1].split('/')[-2:]))


    dot.edge(node_dict[edge[0]], node_dict[edge[1]], str(edge[2]))


print dot.source

dot.render('design_build_test', view=True)
