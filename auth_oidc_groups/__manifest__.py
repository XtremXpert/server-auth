{
    "name": "OpenID Connect : comptes et droits selon les groupes",
    "version": "20.0.1.1.0",
    "summary": "Crée ou lie le compte Odoo à la première connexion OIDC et règle "
    "interne / admin / portail d'après les groupes du fournisseur (Authentik)",
    "author": "Benoit Vézina",
    "license": "AGPL-3",
    "category": "Hidden/Tools",
    "depends": ["auth_oidc"],
    "data": ["views/auth_oauth_provider.xml"],
    "installable": True,
}
