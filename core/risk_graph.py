from collections import defaultdict

# simple in-memory graph (can later move to Redis / Neo4j)
entity_graph = defaultdict(set)


def link_entities(a, b):
   """
   Create bidirectional relationship between two entities
   """
   entity_graph[a].add(b)
   entity_graph[b].add(a)


def risk_neighbors(entity):
   """
   Return connected entities
   """
   return list(entity_graph.get(entity, []))


def compute_graph_risk(entity):
   """
   Simple risk signal based on connections
   """
   neighbors = entity_graph.get(entity, [])
   return len(neighbors)