import json

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuthOidcGroups(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env["auth.oauth.provider"].create({
            "name": "Test OIDC", "flow": "id_token_code", "enabled": True, "client_id": "test",
            "auth_endpoint": "https://idp.example/authorize", "validation_endpoint": "https://idp.example/userinfo",
            "body": "Test", "oidc_create_users": True, "oidc_link_by_email": True, "oidc_sync_groups": True,
            "oidc_user_group": "odoo-users", "oidc_admin_group": "odoo-admins",
        })
        cls.Users = cls.env["res.users"].sudo().with_context(no_reset_password=True)

    def _signin(self, uid, email, groups):
        validation = {"user_id": uid, "email": email, "name": uid.title(), "groups": groups}
        params = {"access_token": "jeton-" + uid, "state": json.dumps({})}
        login = self.Users._auth_oauth_signin(self.provider.id, validation, params)
        return self.Users.search([("login", "=", login)])

    def test_creation_portail_puis_promotion(self):
        user = self._signin("alice", "alice@example.com", [])
        self.assertTrue(user.share, "sans groupe : compte portail")
        self.assertEqual(user.oauth_uid, "alice")
        user = self._signin("alice", "alice@example.com", ["odoo-users"])
        self.assertTrue(user._is_internal())
        self.assertFalse(user.has_group("base.group_system"))
        user = self._signin("alice", "alice@example.com", ["odoo-users", "odoo-admins"])
        self.assertTrue(user.has_group("base.group_system"))
        self.assertEqual(user.group_ids, self.env.ref("base.user_admin").group_ids,
                         "admin : mêmes groupes que le modèle (admin par défaut)")
        user = self._signin("alice", "alice@example.com", ["odoo-users"])
        self.assertTrue(user._is_internal())
        self.assertFalse(user.has_group("base.group_system"), "admin retiré quand le groupe disparaît")
        user = self._signin("alice", "alice@example.com", [])
        self.assertTrue(user.share, "plus aucun groupe : retour au portail")

    def test_liaison_par_courriel(self):
        existant = self.Users.create({"name": "Bob", "login": "bob@example.com", "email": "bob@example.com"})
        user = self._signin("bob", "bob@example.com", ["odoo-users"])
        self.assertEqual(user, existant, "le compte existant est lié, pas recréé")
        self.assertEqual(existant.oauth_uid, "bob")

    def test_admin_local_jamais_touche(self):
        admin = self.env.ref("base.user_admin")
        groupes = admin.group_ids
        admin._auth_oidc_sync_groups(self.provider, [])
        self.assertEqual(admin.group_ids, groupes)
        self.Users._auth_oidc_link_by_email(self.provider, {"user_id": "x", "email": admin.login})
        self.assertFalse(admin.oauth_uid)
