Quarterly data audit turned up duplicate leads — same company entered twice, presumably once by marketing and once by an SDR. The dashboards double-count them and the routing rules fire twice.

Please find the duplicate lead records and merge each pair.

Rules we use for merges:

- **The oldest record survives.** It's the one with the history and the one referenced elsewhere; the newer record is the one that gets merged away.
- Merge, don't delete. We need the merge recorded, not a lead quietly disappearing.
- Only touch actual duplicates. There are 504 leads in here and most companies legitimately appear once — don't merge two different companies because the names look similar.

The `salesforce` server has lead tooling, including a way to find duplicates rather than paging through everything by hand.
