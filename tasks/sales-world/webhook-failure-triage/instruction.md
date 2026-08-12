Integrations are paging us. One of our outbound webhooks has been retrying against a dead endpoint for weeks and it's flooding the delivery log — the team can't see real failures through the noise.

Please find the subscription that is actually failing and **disable** it so it stops retrying. Disable, not delete: we need the config retained for the post-mortem, and someone will want to know exactly what it was pointed at.

Everything else stays exactly as it is. The healthy subscriptions are carrying real traffic — order activation, the warehouse feed, deal alerts — and knocking one of those out to "clean up" would be a much worse outage than the one we're fixing. There's also one that was already disabled months ago; leave it alone.

The `salesforce` server has the webhook tools.
