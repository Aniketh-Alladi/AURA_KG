// ============================================================================
// AURA-KG V1 Seed Data
// Neo4j Version: 5.x
// ----------------------------------------------------------------------------
// Purpose:
// Seeds the AURA-KG database with sample data for development and testing.
// This script is idempotent and can be executed multiple times safely.
// ============================================================================


// ============================================================================
// PERSON
// ============================================================================

MERGE (tejus:Person {person_id: "P001"})
ON CREATE SET
    tejus.name = "Tejus"
ON MATCH SET
    tejus.name = "Tejus";


// ============================================================================
// ROLE
// ============================================================================

MERGE (kgLead:Role {role_id: "R001"})
ON CREATE SET
    kgLead.title = "Knowledge Graph Developer",
    kgLead.responsibilities = "Design graph schema, Neo4j setup, graph modeling"
ON MATCH SET
    kgLead.title = "Knowledge Graph Developer",
    kgLead.responsibilities = "Design graph schema, Neo4j setup, graph modeling";


// ============================================================================
// PROJECT
// ============================================================================

MERGE (aura:Project {project_id: "PR001"})
ON CREATE SET
    aura.name = "AURA-KG",
    aura.description = "Personal Knowledge Graph Assistant",
    aura.timeline = "14 Weeks"
ON MATCH SET
    aura.name = "AURA-KG",
    aura.description = "Personal Knowledge Graph Assistant",
    aura.timeline = "14 Weeks";


// ============================================================================
// DOMAIN
// ============================================================================

MERGE (domain:Domain {domain_id: "D001"})
ON CREATE SET
    domain.name = "Knowledge Graphs + NLP"
ON MATCH SET
    domain.name = "Knowledge Graphs + NLP";


// ============================================================================
// TOOLS
// ============================================================================

MERGE (neo4j:Tool {tool_id: "T001"})
ON CREATE SET
    neo4j.name = "Neo4j",
    neo4j.category = "Graph Database"
ON MATCH SET
    neo4j.name = "Neo4j",
    neo4j.category = "Graph Database";

MERGE (docker:Tool {tool_id: "T002"})
ON CREATE SET
    docker.name = "Docker",
    docker.category = "Containerization"
ON MATCH SET
    docker.name = "Docker",
    docker.category = "Containerization";


// ============================================================================
// FEATURES
// ============================================================================

MERGE (graphStorage:Feature {feature_id: "F001"})
ON CREATE SET
    graphStorage.description = "Knowledge Graph Storage",
    graphStorage.status = "Planned"
ON MATCH SET
    graphStorage.description = "Knowledge Graph Storage",
    graphStorage.status = "Planned";

MERGE (graphQuery:Feature {feature_id: "F002"})
ON CREATE SET
    graphQuery.description = "Graph Query Engine",
    graphQuery.status = "Planned"
ON MATCH SET
    graphQuery.description = "Graph Query Engine",
    graphQuery.status = "Planned";


// ============================================================================
// PHASE
// ============================================================================

MERGE (phase1:Phase {phase_id: "PH001"})
ON CREATE SET
    phase1.name = "Graph Design",
    phase1.status = "In Progress"
ON MATCH SET
    phase1.name = "Graph Design",
    phase1.status = "In Progress";


// ============================================================================
// MILESTONE
// ============================================================================

MERGE (milestone1:Milestone {milestone_id: "M001"})
ON CREATE SET
    milestone1.deadline = "2026-08-15",
    milestone1.status = "Pending"
ON MATCH SET
    milestone1.deadline = "2026-08-15",
    milestone1.status = "Pending";


// ============================================================================
// DATASET
// ============================================================================

MERGE (dataset:Dataset {dataset_id: "DS001"})
ON CREATE SET
    dataset.name = "Dummy Personal Notes",
    dataset.source_type = "Synthetic",
    dataset.size = "100 Documents"
ON MATCH SET
    dataset.name = "Dummy Personal Notes",
    dataset.source_type = "Synthetic",
    dataset.size = "100 Documents";


// ============================================================================
// OUTCOME
// ============================================================================

MERGE (learning:Outcome {outcome_id: "O001"})
ON CREATE SET
    learning.description = "Hands-on experience with Knowledge Graphs and Neo4j"
ON MATCH SET
    learning.description = "Hands-on experience with Knowledge Graphs and Neo4j";


// ============================================================================
// RELATIONSHIPS
// ============================================================================

MATCH (tejus:Person {person_id: "P001"})
MATCH (kgLead:Role {role_id: "R001"})
MATCH (aura:Project {project_id: "PR001"})
MATCH (domain:Domain {domain_id: "D001"})
MATCH (neo4j:Tool {tool_id: "T001"})
MATCH (docker:Tool {tool_id: "T002"})
MATCH (graphStorage:Feature {feature_id: "F001"})
MATCH (graphQuery:Feature {feature_id: "F002"})
MATCH (phase1:Phase {phase_id: "PH001"})
MATCH (milestone1:Milestone {milestone_id: "M001"})
MATCH (dataset:Dataset {dataset_id: "DS001"})
MATCH (learning:Outcome {outcome_id: "O001"})

WITH tejus, kgLead, aura, domain, neo4j, docker,
     graphStorage, graphQuery, phase1,
     milestone1, dataset, learning

MERGE (tejus)-[:ASSIGNED_TO]->(kgLead)
MERGE (kgLead)-[:ASSIGNED_TO]->(aura)
MERGE (aura)-[:BELONGS_TO_DOMAIN]->(domain)
MERGE (aura)-[:USES_TOOL]->(neo4j)
MERGE (aura)-[:USES_TOOL]->(docker)
MERGE (neo4j)-[:SERVES_PURPOSE]->(graphStorage)
MERGE (neo4j)-[:SERVES_PURPOSE]->(graphQuery)
MERGE (aura)-[:HAS_FEATURE]->(graphStorage)
MERGE (aura)-[:HAS_FEATURE]->(graphQuery)
MERGE (aura)-[:HAS_PHASE]->(phase1)
MERGE (phase1)-[:HAS_DEADLINE]->(milestone1)
MERGE (dataset)-[:USED_IN]->(phase1)
MERGE (tejus)-[:GAINED]->(learning);

// ============================================================================
// End of AURA-KG V1 Seed Data
// ============================================================================