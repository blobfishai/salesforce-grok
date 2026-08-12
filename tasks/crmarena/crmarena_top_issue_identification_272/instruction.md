# CRM question

What was the most frequent issue with Women's Running Tank Top in Q1 2022? The associated product Id is 01tWs000002wOIYIA2. Return only the issue Id of the most reported issue for this product.

## Context


## How to work
The CRM is on the `crm` MCP server. Query it with `issue_soql_query` (SOQL;
relationship traversal like `Account.Name` and subqueries are not supported), and
use `get_schema` to see what fields an object has. `search_knowledge_articles`
searches the knowledge base.

When you have the answer, call `respond` **exactly once** with the answer only —
an Id, a value, or the string `None` if the question cannot be answered from the
data. Do not include explanation in the answer.
