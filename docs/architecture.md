# USF Data Platform Architecture (Fabric-centric)
- Ingestion via Fivetran to OneLake (Bronze)
- Transformations to Silver/Gold (Spark/SQL)
- Governance via Purview (scans, glossary, classifications)
- Reporting with Power BI / Fabric semantic models
- CI in GitHub Actions; CD in Azure DevOps
