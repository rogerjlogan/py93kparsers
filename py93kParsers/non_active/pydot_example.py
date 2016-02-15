#!/usr/bin/env python
import pydot

# pydot.Edge('node_d', 'node_a', label="and back we go again", labelfontcolor="#009933", fontsize="10.0", color="blue")
graph = pydot.Dot(graph_type='digraph', font='verdana')

# graph.set_edge_defaults(color='blue',arrowhead='vee',weight='0')
graph.add_edge(pydot.Edge('Eric Loo', 'person', label='is a'))
graph.add_edge(pydot.Edge('Eric Loo', 'handsome', label='outlook'))

graph.add_edge(pydot.Edge('Mei', 'girl', label='is a'))
graph.add_edge(pydot.Edge('Mei', 'pretty', label='outlook'))

graph.write('test.dot',prog='dot')

