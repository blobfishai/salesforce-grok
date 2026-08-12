Our sender reputation is slipping and deliverability flagged it this morning.

Part of the cause: we have sequence enrollments sitting in a **bounced** state that were never stopped. A bounced address doesn't recover on its own, so every subsequent step in the sequence is another hard bounce against our domain.

Please close those out — any enrollment whose status is bounced should be marked **completed** so no further steps go out.

Leave everything else alone. Active enrollments are working, replied ones are being handled by the reps, and already-completed ones are done.

The `salesforce` server has the sequence and enrollment tools.
