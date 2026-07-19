# File: notes_ingestion_blockers.md
Title: Ingestion Pipeline & Auth Blockers
Date: July 22, 2026

Quick sync with Varun regarding the data pipeline & ingestion setup. Varun is currently acting as the Pipeline Engineer. 

Status update:
- He's writing the Python scripts to pull data from the Google Workspace APIs.
- The Gmail API connector is mostly unblocked, but OAuth scopes are proving annoying. 
- The ultimate outcome we need from this pipeline is automated document syncing so the graph updates in near real-time.
- Varun is worried that if the pipeline is too slow, we won't hit the upcoming frontend phase milestone on July 30th. He's going to map the pipeline dependencies to a strict milestone chart by Friday.