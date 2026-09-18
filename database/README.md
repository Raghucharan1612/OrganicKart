# database/

This folder is for database-level assets that live outside the service application code — things a DBA or infra engineer would look for first, separate from the service ORM models and Alembic migrations for each microservice.

Intended future contents:
- Raw SQL seed/reference data scripts
- One-off data migration or backfill scripts
- ER diagrams / schema documentation exports
- MySQL-specific tuning or initialization scripts (charset, collation, users)

Sprint 1 scope: folder created only. No schema or seed data yet.
