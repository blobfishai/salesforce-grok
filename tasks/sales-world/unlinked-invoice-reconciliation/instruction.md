Finance closed the month and the billing sub-ledger doesn't tie out to the order book. Their theory is that some invoices were raised directly, without ever being created from a sales order, so there's nothing on the order side to match them against.

Can you work out which invoices those are and get them tracked?

For every invoice in NetSuite that isn't linked back to a sales order, open one issue in the **RECON** Jira project. Put the invoice id in the summary so the reconciliation team can find it, and note the customer and the amount in the description.

One issue per orphaned invoice — Finance wants to burn them down individually, not as a single batch ticket. Invoices that *are* linked to an order are fine and don't need anything.

NetSuite is on the `erp` server, Jira on the `jira` server.
