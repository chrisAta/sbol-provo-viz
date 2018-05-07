# This script parses an SBOL file and produces a Provenance Graph for it using Graphviz
# This is specifically for the PROV-O model

from rdflib import Graph, URIRef
from graphviz import Digraph

g = Graph()
# g.parse('./design_build_test.xml', 'rdfxml')
g.parse('./full_life_cycle.xml', 'rdfxml')
# g.parse('./sbol2.xml', 'rdfxml')

dot = Digraph('design_build_test')

cur_sub = ''
cur_class = ''

edges = [] # All the relevant edges
nodes = [] # All the nodes that get created
node_names = [] # The names of all the nods that get created
node_dict = {} # Dict that stores the parameters needed for the creation of a specific node

activity_asc_roles = {} # Dict that links an activity to its association's role
activity_usg_roles = {} # Dict that links an activity to its usage's role
activity_entity = {} # Dict that links an activity to its usage's entity

activity_agent = {} # Dict that links an activity to its association's agent
activity_plan = {} # Dict that links an activity to its association's plan


shape_dict = { # Shape Dict

    'Activity' : 'hexagon',
    'Plan' : 'polygon',
    'Agent' : 'diamond',
    'Association' : 'pentagon',
    'Usage' : 'box'

}

colour_dict = { # Colour Dict

    '//sbols.org/v2#design' : 'blue',
    '//sbols.org/v2#build' : 'red',
    '//sbols.org/v2#test' : 'orange',
    '//sbols.org/v2#learn' : 'green',
    'ComponentDefinition': 'darkseagreen',
    'ModuleDefinition': 'darkseagreen',
    'Implementation': 'darkseagreen1',
    'Test': 'darkseagreen2',
    'Attachment': 'darkseagreen2',
    'Model': 'darkseagreen3'

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

        for value in g.objects(URIRef(s), URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')): # Find out the type of the new subject

            cur_class = value.split('#')[-1] # Track the current class

            # Different labels depending on the class
            if cur_class == 'Agent':

                temp_label = s.split('/')[-1]

            elif cur_class == 'Implementation' or cur_class == 'ComponentDefinition' or cur_class == 'ModuleDefinition' or cur_class == 'Test' or cur_class == 'Model' or cur_class == 'Activity' or cur_class =='Plan':

                for displayId in g.objects(URIRef(s), URIRef('http://sbols.org/v2#displayId')):
                    temp_label =  displayId

            node_names += [s]

            node_dict[s] = s.split(':')[-1]

            if cur_class in shape_dict.keys() or cur_class in colour_dict:

                if cur_class == 'Agent':
                    nodes += [(s.split('/')[-1], temp_label, shape_dict[cur_class])]

                elif cur_class == 'Plan':
                    nodes += [(s.split(':')[-1], temp_label, shape_dict[cur_class])]

                elif cur_class == 'ComponentDefinition' or cur_class == 'ModuleDefinition' or cur_class == 'Implementation' or cur_class == 'Test' or cur_class == 'Model':
                    nodes += [(s.split(':')[-1], temp_label, colour_dict[cur_class], 'entity')]

                elif cur_class != 'Usage' and cur_class != 'Association' and cur_class != 'Attachment':
                    # print temp_label
                    nodes += [(s.split(':')[-1], temp_label, shape_dict[cur_class])]

                if cur_class == 'Association':

                    for activity in g.subjects(URIRef('http://www.w3.org/ns/prov#qualifiedAssociation'), URIRef(s)): # Get the role of the activity a Usage is linked to

                        for role in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#hadRole')):
                            activity_asc_roles[activity.split(':')[-1]] = role.split(':')[-1]

                        for agent in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#agent')):
                            activity_agent[activity.split(':')[-1]] = agent.split('/')[-1]

                        for plan in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#hadPlan')):
                            activity_plan[activity.split(':')[-1]] = plan.split(':')[-1]


                elif cur_class == 'Usage':

                    for activity in g.subjects(URIRef('http://www.w3.org/ns/prov#qualifiedUsage'), URIRef(s)):

                        for entity in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#entity')):

                            if activity.split(':')[-1] in activity_entity.keys():
                                activity_entity[activity.split(':')[-1]] += [entity.split(':')[-1]]

                            else:

                                activity_entity[activity.split(':')[-1]] = [entity.split(':')[-1]]

                        for role in g.objects(URIRef(s), URIRef('http://www.w3.org/ns/prov#hadRole')):

                            if activity.split(':')[-1] in activity_usg_roles.keys():
                                activity_usg_roles[activity.split(':')[-1]] += ['role_' + role.split('/')[-1].split('#')[-1]]

                            else:
                                activity_usg_roles[activity.split(':')[-1]] = ['role_' + role.split('/')[-1].split('#')[-1]]



    if p == 'http://www.w3.org/ns/prov#wasDerivedFrom':

        for value in g.objects(URIRef(o), URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')):

            cur_class = value.split('#')[-1]

            if cur_class == 'Attachment':
                nodes += [(o.split(':')[-1], o.split('/')[-2], colour_dict[cur_class], 'entity')]

        edges += [(s.split(':')[-1], o.split(':')[-1], 'wasDerivedFrom')]

    elif p == 'http://www.w3.org/ns/prov#wasGeneratedBy':
        edges += [(s.split(':')[-1], o.split(':')[-1], 'wasGeneratedBy')]


for activity in activity_usg_roles.keys(): # Create edges from activity to its usage's entity

    for i in range(0, len(activity_entity[activity])):
        edges += [(activity, activity_entity[activity][i], activity_usg_roles[activity][i])]

for activity in activity_agent.keys(): # Create edges from activity to its association's agent
    edges += [(activity, activity_agent[activity], 'agent')]

for activity in activity_plan.keys(): # Create edges from activity to its association's plan
    edges += [(activity, activity_plan[activity], 'plan')]




print nodes

for node in nodes: # Create the nodes

    if node[0] in activity_asc_roles.keys(): # If it's an Activity, colour it based on its Association's role
        dot.node(node[0], node[1], shape = node[2], style='filled', fillcolor = colour_dict[activity_asc_roles[node[0]]])

    elif len(node) == 4:
        dot.node(node[0], node[1], style='filled', fillcolor = node[2])

    else:
        dot.node(node[0], node[1], shape = node[2])

for edge in edges: # Create the edges

    if edge[0] not in node_names:
        print edge[0]
        node_names += [edge[0]]
        dot.node(edge[0].split(':')[-1], '/'.join(edge[0].split('/')[-2:]))
        node_dict[edge[0]] = edge[0].split(':')[-1]

    if edge[1] not in node_names:
        print edge[1]
        node_names += [edge[1]]
        node_dict[edge[1]] = edge[1].split(':')[-1]
        dot.node(edge[1].split(':')[-1], '/'.join(edge[1].split('/')[-2:]))

    dot.edge(node_dict[edge[0]], node_dict[edge[1]], str(edge[2]))

print dot.source

# dot.render('design_build_test', view=True) # Create the graph image
dot.render('full_life_cycle', view=True) # Create the graph image
# dot.render('sbol2', view=True) # Create the graph image
