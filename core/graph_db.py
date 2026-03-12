from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"  # change to your real password

driver = GraphDatabase.driver(uri, auth=(username, password))


def link_entities(entity_a, entity_b):
   with driver.session() as session:
       session.run(
           """
           MERGE (a:Entity {id: $a})
           MERGE (b:Entity {id: $b})
           MERGE (a)-[:CONNECTED_TO]->(b)
           """,
           a=entity_a,
           b=entity_b
       )


def compute_graph_risk(entity):
   with driver.session() as session:
       result = session.run(
           """
           MATCH (e:Entity {id:$entity})-[:CONNECTED_TO]->(n)
           RETURN count(n) AS neighbors
           """,
           entity=entity
       )

       record = result.single()

       if record:
           return record["neighbors"]

       return 0