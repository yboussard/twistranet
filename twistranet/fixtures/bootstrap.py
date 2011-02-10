# -*- coding: utf-8 -*-
"""
The minimal bootstrap for TN to work.
We use a python file to ensure proper DB alimentation. Django fixtures are not enough to ensure DB consistancy.

Objects in those fixtures will get created but NEVER updated.
"""
from twistranet.twistapp.models import *
from twistranet.twistapp.lib.python_fixture import Fixture

FIXTURES = [
    Fixture(
        GlobalCommunity,
        slug = "all_twistranet",
        title_en = "All Twistranauts",
        title_fr = "Tous les twistranautes",
        description_en = "You can find all twistranauts in here. "
            "This community is a good place to start looking for people "
            "or for critical information about twistranet.",
        description_fr = "Vous pouvez retrouver tous les twistranautes ici. "
            "Cette communauté est un bon endroit pour commencer à chercher des collègues, "
            "ou pour trouver des informations importantes sur twistranet.",
        site_name = 'twistranet',
        baseline_en = "Reinvent teamwork.",
        baseline_fr = "Réinventez l'esprit d'équipe.",
        permissions = "intranet",
    ),
    Fixture(
        AdminCommunity,
        slug = "administrators",
        title_en = "Administrators",
        title_fr = "Administrateurs",
        description_en = "twistranet admin team",
        description_fr = "L'équipe d'administration de twistranet",
        permissions = "workgroup",
        publisher = GlobalCommunity.objects.filter(),
    ),

    # Default menu items
    Fixture(
        Menu,
        slug = "menu_main",
        title_en = "Main Menu",
        title_fr = "Menu principal",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = Menu.objects.filter(slug = "menu_main"),
        order = 0,
        view_path = "twistranet_home",
        title_en = "Home",
        title_fr = "Accueil",
        slug = "menuitem_home",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = Menu.objects.filter(slug = "menu_main"),
        order = 10,
        view_path = 'communities',
        title_en = "Communities",
        title_fr = "Communautés",
        slug = "menuitem_communities",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = MenuItem.objects.filter(slug = "menuitem_communities"),
        order = 0,
        view_path = 'communities',
        title_en = "All communities",
        title_fr = "Toutes les communautés",
        slug = "menuitem_all_communities",
        publisher = GlobalCommunity.objects.filter(),
    ),
    
]


