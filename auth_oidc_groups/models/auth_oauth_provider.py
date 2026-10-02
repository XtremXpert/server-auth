from odoo import fields, models


class AuthOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    oidc_create_users = fields.Boolean(
        string="Créer les comptes à la première connexion",
        help="Crée le compte (portail, d'après le modèle d'inscription) d'un utilisateur "
        "inconnu, même si l'inscription du site est sur invitation : c'est le "
        "fournisseur qui décide qui peut entrer.",
    )
    oidc_link_by_email = fields.Boolean(
        string="Lier par courriel",
        help="À la première connexion, lie le compte Odoo existant (non lié) qui porte "
        "le même courriel au lieu d'en créer un nouveau. Le fournisseur doit être de "
        "confiance : c'est lui qui garantit le courriel.",
    )
    oidc_sync_groups = fields.Boolean(
        string="Droits selon les groupes",
        help="À chaque connexion, les groupes Odoo sont remplacés : groupe admin → groupes "
        "du modèle des administrateurs, groupe utilisateurs → groupes du modèle des "
        "utilisateurs (ou accès interne de base), aucun des deux → portail. "
        "Ne touche jamais le compte admin local ni les comptes d'un autre fournisseur.",
    )
    oidc_user_group = fields.Char(
        string="Groupe des utilisateurs",
        help="Nom du groupe (revendication « groups ») qui donne un utilisateur interne.",
    )
    oidc_admin_template_id = fields.Many2one(
        "res.users",
        string="Modèle des administrateurs",
        default=lambda self: self.env.ref("base.user_admin", raise_if_not_found=False),
        help="Les membres du groupe des administrateurs reçoivent exactement les groupes de ce compte.",
    )
    oidc_user_template_id = fields.Many2one(
        "res.users",
        string="Modèle des utilisateurs",
        help="Les membres du groupe des utilisateurs reçoivent exactement les groupes de ce "
        "compte ; vide = accès interne de base seulement.",
    )
    oidc_admin_group = fields.Char(
        string="Groupe des administrateurs",
        help="Nom du groupe (revendication « groups ») qui donne l'administration.",
    )
