Complements `auth_oidc` so that the OpenID Connect provider (e.g. Authentik) drives
who gets an Odoo account and with which rights. Everything is configured on the
`auth.oauth.provider` record, so the same module serves every database with a
different configuration:

- **Create accounts on first login** (`oidc_create_users`): an unknown user gets an
  account from the signup template user, even when website signup is "on invitation"
  (with `website` installed, signup follows the website setting, not
  `auth_signup.invitation_scope`).
- **Link by email** (`oidc_link_by_email`): an existing, not yet linked account with
  the same email is linked instead of duplicated. Only enable it when the provider
  guarantees the email (not with public social logins).
- **Rights from groups** (`oidc_sync_groups`), on every login, from the `groups`
  claim: the admin group gets exactly the groups of the *admin template* user
  (`admin` by default), the user group gets the groups of the *user template*
  (or plain internal access), anyone else becomes portal. Odoo groups are replaced:
  rights are managed in the provider and on the template users.

The local `admin` account and accounts linked to another provider are never touched.
