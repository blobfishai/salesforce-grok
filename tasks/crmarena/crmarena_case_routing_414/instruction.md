# CRM question

Use the case routing policy to determine the most suitable agent for the given case. Return only the Id of the agent.
## Given Case
- Case Subject: Incorrect Item Received for Women's High-Performance Jacket
- Case Description: I ordered the Women's High-Performance Jacket for my outdoor workouts, but I received a completely different item instead. I need an immediate exchange to get the correct jacket.

## Context


## How to work
The CRM is on the `crm` MCP server. Query it with `issue_soql_query` (SOQL;
relationship traversal like `Account.Name` and subqueries are not supported), and
use `get_schema` to see what fields an object has. `search_knowledge_articles`
searches the knowledge base.

When you have the answer, call `respond` **exactly once** with the answer only —
an Id, a value, or the string `None` if the question cannot be answered from the
data. Do not include explanation in the answer.
