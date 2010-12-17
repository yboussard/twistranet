from twistranet.twistranet.models import *
from twistranet.content_types.models import *
from twistranet.twistranet.lib.python_fixture import Fixture

__account__ = SystemAccount.get()

FIXTURES = [
    Fixture(
        Document,
        force_update = True,
        slug = "help",
        publisher = GlobalCommunity.objects.get_query_set(),
        title = "TwistraNet Help",
        description = "TwistraNet is a simple yet very efficient social network "
        "tailored for enterprise needs. This document will get you started at using it.",
        text = """<h2>Getting started</h2>

If you can read that document, that probably means you're already connected to TwistraNet! If you're not logged-in, use the 'login' link in this page to connect with your credentials.

Once you're logged in, you can already work with TwistraNet.

<table width="100%">
    <tr>
        <th width="33%">
        </th>
        <th width="33%">
        </th>
        <th width="33%">
        </th>
   </tr>
    <tr>
        <td>
            Who are you working the most with?<br />
            Find your co-workers and add them to your network. It's the easiest
            way to stay in touch with what they're doing.
        </td>
        <td>
            What are you working on? Do you need some help?<br />
            Do you have an advice or a quick information to give to your co-workers?<br />
            You're only two clicks away from doing it right now!
        </td>
        <td>
            Have some content to publish? A report, a memo, something back in the 2000s
            you'd write an email and CCing your whole office?<br />
            Don't spam your co-workers, use a <b>Document</b>. Your network will know you've
            got something to say, and your other co-workers will be able to find it
            easily.
        </td>
    </tr>
</table>

Working with TwistraNet is as easy as that!

<h2>Configuration and administration</h2>

If you want to configure and adminitrate TwistraNet, please read the /content/admin documentation.

""",
        permissions = "public",
    ),
    
    Fixture(
        MenuItem,
        slug = "menuitem_help",
        parent = Menu.objects.filter(slug = "menu_main"),
        order = 90,
        target = Document.objects.filter(slug = "help"),
        title = "Help",
    ),
]



