# AURA-KG Retrieval Team Interface Contract (V1)

**Owner**: Tejus (NLP & Graph Construction Lead)  
**Consumer**: Aniketh (LLM & Retrieval Lead)  
**Target Graph DB**: Neo4j 5.x  
**Last Updated**: 2026-07-22  

---

## 1. Overview

This document specifies the official Cypher query interface and standard JSON response formats for the **Retrieval & LLM Subsystem**. The queries below enable semantic entity lookup, sub-graph neighborhood traversal, project breakdown, tool stack discovery, and team hierarchy resolution.

---

## 2. Graph Schema Summary

### Node Labels & Primary Keys
- `Person` (`person_id`)
- `Role` (`role_id`)
- `Project` (`project_id`)
- `Domain` (`domain_id`)
- `Tool` (`tool_id`)
- `Feature` (`feature_id`)
- `Phase` (`phase_id`)
- `Milestone` (`milestone_id`)
- `Dataset` (`dataset_id`)
- `Outcome` (`outcome_id`)
- `Deliverable` (`deliverable_id`)

### Relationship Types
`ASSIGNED_TO`, `DEPENDS_ON`, `USES_TOOL`, `SERVES_PURPOSE`, `HAS_FEATURE`, `HAS_PHASE`, `HAS_DEADLINE`, `BELONGS_TO_DOMAIN`, `HAS_DELIVERABLE`, `USED_IN`, `GAINED`

---

## 3. Retrieval Query Specifications

### Query 1: Find Node by Name
**Purpose**: Case-insensitive fuzzy/exact search for any entity by name or title across all node labels.

#### Cypher Query
```cypher
MATCH (n)
WHERE toLower(n.name) CONTAINS toLower($query_name) 
   OR toLower(n.title) CONTAINS toLower($query_name)
RETURN 
    labels(n)[0] AS node_type,
    n.person_id AS person_id,
    n.project_id AS project_id,
    n.tool_id AS tool_id,
    n.name AS name,
    n.title AS title,
    properties(n) AS attributes
LIMIT 10;
```

#### Example Input Parameters
```json
{
  "query_name": "Neo4j"
}
```

#### Example Response JSON
```json
{
  "results": [
    {
      "node_type": "Tool",
      "tool_id": "tool_neo4j",
      "name": "Neo4j",
      "attributes": {
        "tool_id": "tool_neo4j",
        "name": "Neo4j",
        "category": "Graph Database"
      }
    }
  ]
}
```

---

### Query 2: Find Neighbors (1-Hop & 2-Hop Context)
**Purpose**: Traverses immediate (1-hop) and extended (2-hop) graph neighbors around a given entity to build prompt context for the LLM.

#### Cypher Query
```cypher
MATCH (source)
WHERE source.person_id = $node_id 
   OR source.project_id = $node_id 
   OR source.tool_id = $node_id 
   OR source.feature_id = $node_id
MATCH (source)-[r1]-(neighbor1)
OPTIONAL MATCH (neighbor1)-[r2]-(neighbor2)
WHERE neighbor2 <> source
RETURN 
    labels(source)[0] AS source_label,
    source.name AS source_name,
    type(r1) AS rel1_type,
    labels(neighbor1)[0] AS target1_label,
    neighbor1.name AS target1_name,
    type(r2) AS rel2_type,
    labels(neighbor2)[0] AS target2_label,
    neighbor2.name AS target2_name
LIMIT 50;
```

#### Example Input Parameters
```json
{
  "node_id": "project_aura_kg"
}
```

#### Example Response JSON
```json
{
  "source": "AURA-KG",
  "neighbors": [
    {
      "relationship": "USES_TOOL",
      "target_type": "Tool",
      "target_name": "Neo4j",
      "second_hop": [
        {
          "relationship": "SERVES_PURPOSE",
          "target_type": "Feature",
          "target_name": "Knowledge Graph Storage"
        }
      ]
    }
  ]
}
```

---

### Query 3: Find All Project Features
**Purpose**: Retrieves all features associated with a given project along with their status and purpose-serving tools.

#### Cypher Query
```cypher
MATCH (p:Project)-[:HAS_FEATURE]->(f:Feature)
WHERE toLower(p.name) = toLower($project_name) OR p.project_id = $project_id
OPTIONAL MATCH (t:Tool)-[:SERVES_PURPOSE]->(f)
RETURN 
    p.name AS project_name,
    f.feature_id AS feature_id,
    f.description AS feature_description,
    f.status AS feature_status,
    collect(DISTINCT t.name) AS supporting_tools;
```

#### Example Input Parameters
```json
{
  "project_name": "AURA-KG",
  "project_id": "project_aura_kg"
}
```

#### Example Response JSON
```json
{
  "project": "AURA-KG",
  "features": [
    {
      "feature_id": "feature_knowledge_graph_storage",
      "description": "Knowledge Graph Storage",
      "status": "Planned",
      "supporting_tools": ["Neo4j", "Docker"]
    },
    {
      "feature_id": "feature_graph_query_engine",
      "description": "Graph Query Engine",
      "status": "Planned",
      "supporting_tools": ["Neo4j"]
    }
  ]
}
```

---

### Query 4: Find All Tools Used by a Project
**Purpose**: Retrieves all tools, categories, and feature mappings used in a specific project.

#### Cypher Query
```cypher
MATCH (p:Project)-[:USES_TOOL]->(t:Tool)
WHERE toLower(p.name) = toLower($project_name) OR p.project_id = $project_id
OPTIONAL MATCH (t)-[:SERVES_PURPOSE]->(f:Feature)
RETURN 
    p.name AS project_name,
    t.tool_id AS tool_id,
    t.name AS tool_name,
    t.category AS tool_category,
    collect(DISTINCT f.description) AS served_features;
```

#### Example Input Parameters
```json
{
  "project_name": "AURA-KG"
}
```

#### Example Response JSON
```json
{
  "project_name": "AURA-KG",
  "tools": [
    {
      "tool_id": "tool_neo4j",
      "tool_name": "Neo4j",
      "tool_category": "Graph Database",
      "served_features": ["Knowledge Graph Storage", "Graph Query Engine"]
    },
    {
      "tool_id": "tool_docker",
      "tool_name": "Docker",
      "tool_category": "Containerization",
      "served_features": ["Knowledge Graph Storage"]
    }
  ]
}
```

---

### Query 5: Find All Team Members and Assigned Roles
**Purpose**: Resolves team members, assigned project roles, and project assignments.

#### Cypher Query
```cypher
MATCH (person:Person)-[:ASSIGNED_TO]->(role:Role)-[:ASSIGNED_TO]->(project:Project)
RETURN 
    person.person_id AS person_id,
    person.name AS member_name,
    role.title AS role_title,
    role.responsibilities AS responsibilities,
    project.name AS project_name;
```

#### Example Response JSON
```json
{
  "team_members": [
    {
      "person_id": "person_tejus",
      "member_name": "Tejus",
      "role_title": "Knowledge Graph Developer",
      "responsibilities": "Design graph schema, Neo4j setup, graph modeling",
      "project_name": "AURA-KG"
    },
    {
      "person_id": "person_varun",
      "member_name": "Varun",
      "role_title": "Data Ingestion Developer",
      "responsibilities": "Clean and normalize incoming data notes/emails/docs",
      "project_name": "AURA-KG"
    }
  ]
}
```

---

## 4. Integration Guidelines for Retrieval Subsystem

1. **Parameter Sanitization**: Always pass queries with parameter maps (`$query_name`, `$node_id`, `$project_name`) to prevent Cypher injection.
2. **Transaction Mode**: Use `session.execute_read()` for all retrieval queries.
3. **Empty Results**: Handle empty result sets gracefully; return `[]` or `"null"` context rather than raising graph execution exceptions.
