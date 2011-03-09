# -*- coding: utf-8 -*-
"""
Sample building script for the COGIP example.
"""
import csv
import os

from twistranet.twistapp.models import *
from twistranet.content_types.models import *
from twistranet.twistapp.lib.python_fixture import Fixture
from twistranet.twistapp.lib.slugify import slugify
from twistranet.twistapp.lib.log import *
from twistranet.tagging.models import *
from django.contrib.auth.models import User
from django.core.files import File as DjangoFile

HERE_COGIP = os.path.abspath(os.path.dirname(__file__))


def generate_tags(flat_list):
    """
    Generate a tags list from a flat list.
    Return a list of Tag objects.
    """
    ret = []
    if not flat_list:
        return ret
    tags = [ t.strip() for t in flat_list.split(",") ]
    for t in tags:
        if not Tag.objects.filter(title = t).exists():
            log.debug("Creating tag %s" % t)
            tag = Tag(title = t)
            tag.save()
        else:
            tag = Tag.objects.get(title = t)
        ret.append(tag)
    return ret

def load_cogip():
    """
    WARNING: THIS IS MEANT TO BE LOAD FROM AN EMPTY DATABASE!
    We didn't bother testing it with a pre-populated one as it doesn't make that much sense.
    """
    # Just to be sure, we log as system account
    __account__ = SystemAccount.get()

    # Create tags

    # Import the whole file, creating all needed fixtures, including Service as communities.
    f = open(os.path.join(HERE_COGIP, "cogip.csv"), "rU")
    c = csv.DictReader(f, delimiter = ';', fieldnames = ['firstname', 'lastname', 'sex', 'service', 'function', 'email', 'picture_file', 'tags', 'network'])
    services = []
    for useraccount in c:
        # Create the user if necessary
        username = slugify("%s" % (useraccount['lastname'].decode('utf-8'), ))
        # username = slugify(useraccount['lastname']).lower()
        password = username
        if not User.objects.filter(username = username).exists():
            u = User.objects.create(
                username = username,
                email = useraccount['email'],
            )
            u.set_password(password)
            u.save()
    
        # Create the user account
        u = Fixture(
            UserAccount,
            slug = username,
            title = "%s %s" % (useraccount['firstname'], useraccount['lastname'], ),
    		description = useraccount['function'],
            permissions = "public",
            user = User.objects.get(username = username),
            force_update = True,
        ).apply()
    
        # Create a community matching user's service or make him join the service. And put it in a menu!
        service_slug = slugify(useraccount['service'])
        if not service_slug in services:
            services.append(service_slug)
            service = Fixture(
                Community,
                slug = service_slug,
                title = useraccount['service'],
                permissions = "blog",
                logged_account = username,
                force_update = True,
            ).apply()
        
            # Add default picture in the community
            source_fn = os.path.join(HERE_COGIP, 'cogip.png')
            r = Resource(
                publisher = service,
                resource_file = DjangoFile(open(source_fn, "rb"), 'cogip.png'),
            )
            r.save()
            service.picture = r
            service.save()
        
            # Create the menu item
            if not MenuItem.objects.filter(slug = "cogip_menu").exists():
                cogip_menu = MenuItem.objects.create(
                    slug = "cogip_menu",
                    order = 5,
                    title = "La COGIP",
                    parent = Menu.objects.get(),
                    link_url = "/",
                )
                cogip_menu.save()
            else:
                cogip_menu = MenuItem.objects.get(slug = "cogip_menu")
            item = MenuItem.objects.create(parent = cogip_menu, target = service)
            item.save()
        else:
            Community.objects.get(slug = service_slug).join(UserAccount.objects.get(slug = username))
            
        # Set tags
        for tag in generate_tags(useraccount['tags']):
            u.tags.add(tag)

        # Create / Replace the profile picture if the image file is available.
        source_fn = os.path.join(HERE_COGIP, "images", useraccount['picture_file'])
        if os.path.isfile(source_fn):
            picture_slug = slugify("pict_%s" % useraccount['picture_file'])
            Resource.objects.filter(slug = picture_slug).delete()
            r = Resource(
                publisher = UserAccount.objects.get(slug = username),
                resource_file = DjangoFile(open(source_fn, "rb"), useraccount['picture_file']),
                slug = picture_slug,
            )
            r.save()
            u = UserAccount.objects.get(slug = username)
            u.picture = Resource.objects.get(slug = picture_slug)
            u.save()
        
        # Add friends in the network (with pending request status)
        if useraccount['network']:
            for friend in [ s.strip() for s in useraccount['network'].split(',') ]:
                if friend.startswith('-'):
                    approved = False
                    friend = friend[1:]
                else:
                    approved = True
                log.debug("Put '%s' and '%s' in their network." % (username, friend))
                current_account = UserAccount.objects.get(slug = username)
                __account__ = UserAccount.objects.get(slug = username)
                friend_account = UserAccount.objects.get(slug = friend)
                friend_account.add_to_my_network()
                if approved:
                    __account__ = UserAccount.objects.get(slug = friend)
                    current_account.add_to_my_network()
                __account__ = SystemAccount.objects.get()

    # Create communities and join ppl from there
    f = open(os.path.join(HERE_COGIP, "communities.csv"), "rU")
    c = csv.DictReader(f, delimiter = ';', fieldnames = ['title', 'description', 'permissions', 'tags', 'members', ])
    for community in c:
        if not community['members']:
            continue
        member_slugs = [ slug.strip() for slug in community['members'].split(',') ]
        if not member_slugs:
            continue
        service_slug = slugify(community['title'])
        com = Fixture(
            Community,
            slug = service_slug,
            title = community['title'],
            description = community['description'],
            permissions = community['permissions'],
            logged_account = member_slugs[0],
        ).apply()
    
        for member in member_slugs:
            log.debug("Make %s join %s" % (member, com.slug))
            com.join(UserAccount.objects.get(slug = member))

        # Set tags
        for tag in generate_tags(community['tags']):
            com.tags.add(tag)

    # Create content updates
    f = open(os.path.join(HERE_COGIP, "content.csv"), "rU")
    contents = csv.DictReader(f, delimiter = ';', fieldnames = ['type', 'owner', 'publisher', 'permissions', 'text', 'filename', 'tags', ])
    for content in contents:
        log.debug("Importing %s" % content)
        __account__ = UserAccount.objects.get(slug = content['owner'])
        if content['type'].lower() == "status":
            log.debug("Publisher: %s" % content['publisher'])
            status = StatusUpdate(
                publisher = Account.objects.get(slug = content['publisher']),
                permissions = content['permissions'],
                description = content['text'],
            )
            status.save()
            log.debug("Adding status update: %s" % status)
        elif content['type'].lower() == 'document':
            source_fn = os.path.join(HERE_COGIP, "documents", content['filename'])
            file_content = ""
            if os.path.isfile(source_fn):
                f = open(source_fn, 'rU')
                file_content = f.read()
            article = Document.objects.create(
                slug = slugify(content['filename']),
                title = content['text'],
                publisher = Account.objects.get(slug = content['publisher']),
                permissions = content['permissions'],
                text = file_content or "(empty file)",
            )
            for tag in generate_tags(content['tags']):
                article.tags.add(tag)
        elif content['type'].lower() == "comment":
            comment = Comment.objects.create(in_reply_to = status, description = content['text'], )
        else:
            raise ValueError("Invalid content type: %s" % content['type'])
        __account__ = SystemAccount.get()

    # Special stuff
    cogip_menu = MenuItem.objects.get(slug = "cogip_menu")
    cogip_menu.target = Document.objects.get(slug = "presentation_cogip_html")
    cogip_menu.link_url = None
    cogip_menu.save()
