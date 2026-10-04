# Secret Box: SQL injection through a secret field

## Source review

The application stores a privileged secret in a database row owned by a fixed account identifier. A normal user can create a secret, and the insertion query interpolates the submitted content directly into SQL text. That is the key boundary: authentication restricts who can log in, but it does not make dynamically concatenated SQL safe.

## Reason about the query

Inspect the exact quoting around the content field and determine whether a submitted value can change the expression parsed by the database. In the challenge, a carefully balanced string could append a scalar subquery selecting the privileged secret, then concatenate that value into the new row owned by the logged-in user. Reading the user's own newly created secret then exposed the selected data.

The owner identifier and the challenge-specific payload are intentionally omitted. The important analysis is to map the source query, identify the user-controlled SQL context, and verify the database dialect's concatenation and scalar-subquery behavior in the authorized instance.

## Defensive lesson

Use parameterized queries or the query builder's structured insert API. Treat every field value as data, never as part of SQL syntax. Authorization should also ensure that sensitive rows cannot be selected by unrelated users, even if a query-injection bug is introduced elsewhere.
