// ============================================================================
// AURA-KG V1 Constraints
// Neo4j Version: 5.x
// ----------------------------------------------------------------------------
// Purpose:
// Defines uniqueness constraints for all node labels in the AURA-KG graph.
// These constraints ensure that every entity has a unique identifier and
// prevent duplicate nodes from being created.
// Safe to execute multiple times due to IF NOT EXISTS.
// ============================================================================


// ============================================================================
// PERSON
// ============================================================================

CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person)
REQUIRE p.person_id IS UNIQUE;


// ============================================================================
// ROLE
// ============================================================================

CREATE CONSTRAINT role_id_unique IF NOT EXISTS
FOR (r:Role)
REQUIRE r.role_id IS UNIQUE;


// ============================================================================
// PROJECT
// ============================================================================

CREATE CONSTRAINT project_id_unique IF NOT EXISTS
FOR (p:Project)
REQUIRE p.project_id IS UNIQUE;


// ============================================================================
// DOMAIN
// ============================================================================

CREATE CONSTRAINT domain_id_unique IF NOT EXISTS
FOR (d:Domain)
REQUIRE d.domain_id IS UNIQUE;


// ============================================================================
// TOOL
// ============================================================================

CREATE CONSTRAINT tool_id_unique IF NOT EXISTS
FOR (t:Tool)
REQUIRE t.tool_id IS UNIQUE;


// ============================================================================
// FEATURE
// ============================================================================

CREATE CONSTRAINT feature_id_unique IF NOT EXISTS
FOR (f:Feature)
REQUIRE f.feature_id IS UNIQUE;


// ============================================================================
// PHASE
// ============================================================================

CREATE CONSTRAINT phase_id_unique IF NOT EXISTS
FOR (p:Phase)
REQUIRE p.phase_id IS UNIQUE;


// ============================================================================
// MILESTONE
// ============================================================================

CREATE CONSTRAINT milestone_id_unique IF NOT EXISTS
FOR (m:Milestone)
REQUIRE m.milestone_id IS UNIQUE;


// ============================================================================
// DATASET
// ============================================================================

CREATE CONSTRAINT dataset_id_unique IF NOT EXISTS
FOR (d:Dataset)
REQUIRE d.dataset_id IS UNIQUE;


// ============================================================================
// OUTCOME
// ============================================================================

CREATE CONSTRAINT outcome_id_unique IF NOT EXISTS
FOR (o:Outcome)
REQUIRE o.outcome_id IS UNIQUE;


// ============================================================================
// End of AURA-KG V1 Constraints
// ============================================================================