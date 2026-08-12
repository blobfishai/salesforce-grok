# CRM question

Use the case routing policy to determine the most suitable agent for the given case. Return only the Id of the agent.
## Given Case
- Case Subject: Size Mismatch on Marathon Performance Shoes
- Case Description: I recently purchased a pair of Marathon Performance Shoes, but the size chart on the website doesn't seem to match the actual size of the product. The shoes are much tighter than what I expected based on the chart.

## Context


## How to work
The CRM is on the `crm` MCP server. Query it with `issue_soql_query` (SOQL;
relationship traversal like `Account.Name` and subqueries are not supported), and
use `get_schema` to see what fields an object has. `search_knowledge_articles`
searches the knowledge base.

When you have the answer, call `respond` **exactly once** with the answer only —
an Id, a value, or the string `None` if the question cannot be answered from the
data. Do not include explanation in the answer.
