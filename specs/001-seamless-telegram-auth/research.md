# Phase 0 — Research: Seamless Telegram Auth (MVP)

Decision: Use Telegram Web App initData verification only (no deep-link fallback) for the MVP.

Rationale:

- initData verification is supported by the Telegram Web App and provides a secure, server-verifiable payload containing the user's Telegram ID and a signature (hash). This is sufficient for an initial "who is this Telegram user" check when opening the Mini App.
- It minimizes UX complexity for the MVP: users only open the Mini App and the backend verifies identity; there is no extra OAuth flow to orchestrate.
- Working with initData keeps frontend and backend changes small and reduces edge cases (no redirects, no bot login flow).

Alternatives considered:

- Deep-link login / bot-based OAuth: would allow a richer, more persistent auth handshake, but requires extra redirects and bot interaction flows. Higher implementation and QA cost — deferred to post-MVP.
- Telegram bot-only verification (send code to bot): adds friction for users and mixes app and bot flows. Not chosen for MVP.

Admin authorization model — decision and rationale

Decision: Administrative actions (accept/reject requests) must be performed by an existing SOSenki user with Administrator role. Admin actions are authenticated using the same initData verification if performed from the Mini App; for other admin UI, use existing backend session auth.

Rationale:

- Re-using the same identity verification method keeps the threat model simple. Admin actions must be tied to SOSenkiUser records with role=Administrator.

Alternatives considered:

- Delegated admin tokens or separate admin OAuth flows — more complexity, not needed for MVP.

Edge cases and notes

- Duplicate telegram_id: `telegram_id` is unique. If an admin attempts to accept a request and a SOSenki user with the same `telegram_id` already exists, the API returns an error `user_already_exists`. The admin flow should show this error and suggest linking instead (linking flow is out-of-scope for MVP).
- Request creation only shown when the visiting Telegram ID is not already linked to a SOSenkiUser.

Security notes

- Server must verify `initData` signature strictly (check hash per Telegram docs) and reject expired `auth_date` values.
- Store only the minimal Telegram profile fields required for onboarding (telegram_id, first_name, last_name, username, photo_url) and treat them as optionally mutable fields.

Decision summary

- MVP: initData-only verification, admin actions require Administrator role, create-on-accept behavior for new SOSenki users, `telegram_id` uniqueness enforced.
