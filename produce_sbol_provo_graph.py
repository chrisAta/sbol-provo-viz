from rdflib import Graph, URIRef
from graphviz import Digraph

g = Graph()
g.parse('./design_build_test.xml', 'rdfxml')

dot = Digraph('design_build_test')

cur_sub = ''
cur_class = ''

edges = []
nodes = []
node_names = []
node_dict = {}

activity_roles = {}

shape_dict = {

    'Activity' : 'trapezium',
    'Plan' : 'polygon',
    'Agent' : 'diamond',
    'Association' : 'pentagon',
    'Usage' : 'box',

}

colour_dict = {

    '//sbols.org/v2#design' : 'blue',
    '//sbols.org/v2#build' : 'red',
    '//sbols.org/v2#test' : 'orange',
    '//sbols.org/v2#learn' : 'green'


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

            node_names += [s]
            node_dict[s] = s.split(':')[-1]

            if cur_class in shape_dict.keys():
                if cur_class == 'Association' or cur_class == 'Usage':
                    # dot.node(s.split(':')[-1], temp_label, shape = shape_dict[cur_class], fixedsize ='true' , fontsize = '10',  width = '0.5', height = '0.5') # Createt a new node in the Graphviz
                    nodes += [(s.split(':')[-1], temp_label, shape_dict[cur_class], 'true' , '10',  '0.5', '0.5')]

                else:
                    # dot.node(s.split(':')[-1], temp_label, shape = shape_dict[cur_class]) # Createt a new node in the Graphviz
                    nodes += [(s.split(':')[-1], temp_label, shape_dict[cur_class])]

                if cur_class == 'Usage':

                    for activity in g.subjects(URIRef('http://www.w3.org/ns/prov#qualifiedUsage'), URIRef(s)):
                        for role in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#hadRole')):
                            activity_roles[activity.split(':')[-1]] = role.split(':')[-1]


            else:
                dot.node(s.split(':')[-1], temp_label) # Create a new node in the Graphviz


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

for node in nodes:

    if len(node) == 3:
        if node[0] in activity_roles.keys():
            dot.node(node[0], node[1], shape = node[2], color = colour_dict[activity_roles[node[0]]])

        else:
            dot.node(node[0], node[1], shape = node[2])

    else:
        dot.node(node[0],node[1], shape = node[2], fixedsize = node[3], fontsize = node[4], width = node[5], height = node[6])


for edge in edges:

    if edge[0] not in node_names:

        print 'Added a new unknown node'

        dot.node(edge[0].split(':')[-1], '/'.join(edge[0].split('/')[-2:]))
        node_dict[edge[0]] = edge[0].split(':')[-1]

    if edge[1] not in node_names:

        print 'Added a new unknown node'

        node_dict[edge[1]] = edge[1].split(':')[-1]
        dot.node(edge[1].split(':')[-1], '/'.join(edge[1].split('/')[-2:]))


    dot.edge(node_dict[edge[0]], node_dict[edge[1]], str(edge[2]))


print dot.source

dot.render('design_build_test', view=True)
