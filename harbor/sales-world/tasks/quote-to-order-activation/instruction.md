Order activation is behind again. Finance flagged that we have approved quotes in Salesforce with nothing booked against them in NetSuite, which means the revenue is invisible to them.

Please go through every quote that is currently **approved** in Salesforce and make sure each one has a corresponding sales order in the ERP.

For each one, create the sales order with:

- the **same ERP customer entity that account has been booked against before** — the ERP keys orders on an
  internal customer id, not the account name, so look at that account's existing orders to find which entity it is,
- a memo that includes the quote number, so Finance can trace the order back,
- the **net** total from the quote (what the customer actually pays after discount) and the quote's currency.

Do not create orders for quotes in draft, in review, or rejected — those aren't sold yet. And don't modify the quotes themselves; this is a booking exercise, not a re-approval.

Salesforce is on the `salesforce` server, NetSuite on the `erp` server.
