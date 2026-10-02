import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)
        if oauth_provider.oidc_link_by_email:
            self._auth_oidc_link_by_email(oauth_provider, validation)
        if oauth_provider.oidc_create_users:
            self._auth_oidc_create_user(oauth_provider, validation, params)
        login = super()._auth_oauth_signin(provider, validation, params)
        if login and oauth_provider.oidc_sync_groups:
            user = self.search(
                [("login", "=", login), ("oauth_provider_id", "=", provider)], limit=1
            )
            user._auth_oidc_sync_groups(oauth_provider, validation.get("groups") or [])
        return login

    @api.model
    def _auth_oidc_link_by_email(self, oauth_provider, validation):
        oauth_uid = validation.get("user_id")
        email = (validation.get("email") or "").strip()
        if not oauth_uid or not email:
            return
        if self.search_count(
            [("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", oauth_provider.id)]
        ):
            return
        users = self.search(
            [("oauth_provider_id", "=", False), "|", ("login", "=ilike", email), ("email", "=ilike", email)]
        )
        admin = self.env.ref("base.user_admin", raise_if_not_found=False)
        if len(users) != 1 or users == admin:
            return
        users.write({"oauth_provider_id": oauth_provider.id, "oauth_uid": oauth_uid})
        _logger.info("OIDC : compte %s lié à %s (%s)", users.login, oauth_uid, oauth_provider.name)

    @api.model
    def _auth_oidc_create_user(self, oauth_provider, validation, params):
        oauth_uid = validation.get("user_id")
        if not oauth_uid or self.search_count(
            [("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", oauth_provider.id)]
        ):
            return
        values = self._generate_signup_values(oauth_provider.id, validation, params)
        if self.with_context(active_test=False).search_count([("login", "=ilike", values["login"])]):
            return  # le login existe déjà : auth_oauth refusera, rien à créer
        user = self.with_context(no_reset_password=True)._create_user_from_template(values)
        _logger.info("OIDC : compte %s créé pour %s (%s)", user.login, oauth_uid, oauth_provider.name)

    def _auth_oidc_target(self, oauth_provider, groups):
        names = set(groups)
        if oauth_provider.oidc_admin_group and oauth_provider.oidc_admin_group in names:
            return "admin"
        if oauth_provider.oidc_user_group and oauth_provider.oidc_user_group in names:
            return "user"
        return "portal"

    def _auth_oidc_sync_groups(self, oauth_provider, groups):
        self.ensure_one()
        admin = self.env.ref("base.user_admin", raise_if_not_found=False)
        if not self or self == admin or self._is_superuser():
            return
        target = self._auth_oidc_target(oauth_provider, groups)
        if target == "admin":
            wanted = (oauth_provider.oidc_admin_template_id or admin).group_ids
        elif target == "user":
            template = oauth_provider.oidc_user_template_id
            wanted = template.group_ids if template else self.env.ref("base.group_user")
        else:
            wanted = self.env.ref("base.group_portal")
        if self.group_ids != wanted:
            self.write({"group_ids": [(6, 0, wanted.ids)]})
            _logger.info("OIDC : %s réglé en « %s »", self.login, target)
