// ============================================================================
// AURA-KG V1 Graph Schema
// Neo4j Version: 5.x
// ----------------------------------------------------------------------------
// Purpose:
// Documents the graph schema used by the AURA-KG project.
// This file serves as the single source of truth for the graph model.
// It is intended for documentation only and does not execute any Cypher
// statements. Constraints, indexes, and seed data are maintained in their
// respective files.
// ============================================================================


// ============================================================================
// NODE LABELS
// ============================================================================
//
// Person
// ├── person_id (Unique)
// └── name
//
// Role
// ├── role_id (Unique)
// ├── title
// └── responsibilities
//
// Project
// ├── project_id (Unique)
// ├── name
// ├── description
// └── timeline
//
// Domain
// ├── domain_id (Unique)
// └── name
//
// Tool
// ├── tool_id (Unique)
// ├── name
// └── category
//
// Feature
// ├── feature_id (Unique)
// ├── description
// └── status
//
// Phase
// ├── phase_id (Unique)
// ├── name
// └── status
//
// Milestone
// ├── milestone_id (Unique)
// ├── deadline
// └── status
//
// Dataset
// ├── dataset_id (Unique)
// ├── name
// ├── source_type
// └── size
//
// Outcome
// ├── outcome_id (Unique)
// └── description
//
// Deliverable
// ├── deliverable_id (Unique)
// ├── name
// ├── type
// └── status


// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================

// ---------------------------------------------------------------------------
// Assignment
// ---------------------------------------------------------------------------

// A person is assigned a role.
(:Person)-[:ASSIGNED_TO]->(:Role)

// A role is assigned to a project.
(:Role)-[:ASSIGNED_TO]->(:Project)

// Roles may depend on other roles.
(:Role)-[:DEPENDS_ON]->(:Role)


// ---------------------------------------------------------------------------
// Project Structure
// ---------------------------------------------------------------------------

// A project contains features.
(:Project)-[:HAS_FEATURE]->(:Feature)

// A project is divided into phases.
(:Project)-[:HAS_PHASE]->(:Phase)

// A phase has a milestone/deadline.
(:Phase)-[:HAS_DEADLINE]->(:Milestone)

// A project produces deliverables.
(:Project)-[:HAS_DELIVERABLE]->(:Deliverable)


// ---------------------------------------------------------------------------
// Technology
// ---------------------------------------------------------------------------

// A project uses one or more tools.
(:Project)-[:USES_TOOL]->(:Tool)

// A tool exists to support a feature.
(:Tool)-[:SERVES_PURPOSE]->(:Feature)


// ---------------------------------------------------------------------------
// Classification
// ---------------------------------------------------------------------------

// A project belongs to a specific domain.
(:Project)-[:BELONGS_TO_DOMAIN]->(:Domain)


// ---------------------------------------------------------------------------
// Learning
// ---------------------------------------------------------------------------

// A person gains outcomes from working on projects.
(:Person)-[:GAINED]->(:Outcome)


// ---------------------------------------------------------------------------
// Dataset Usage
// ---------------------------------------------------------------------------

// A dataset is used during a project phase.
(:Dataset)-[:USED_IN]->(:Phase)

// ============================================================================
// DELIVERABLE
// ============================================================================

CREATE CONSTRAINT deliverable_id_unique IF NOT EXISTS
FOR (dl:Deliverable)
REQUIRE dl.deliverable_id IS UNIQUE;

// ============================================================================
// End of AURA-KG V1 Graph Schema
// ============================================================================