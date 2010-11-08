from twistranet.models import *
from twistranet.lib.python_fixture import Fixture

FIXTURES = [
    Fixture(
        Document,
        force_update = True,
        slug = "help",
        text = """TwistraNet Help

TwistraNet is a simple yet very efficient social network tailored for enterprise needs. This document will get you started at using it.

<h1>Getting started</h1>

If you can read that document, that probably means you're already connected to TwistraNet! If you're not logged-in, use the 'login' link in this page to connect with your credentials.

Once you're logged in, you can already work with TwistraNet.

<ul>
<li>Start by saying what you're working on with the little status update form below.</li>
<li>You can also publish "rich" documents with images, links and files. Use the "Create document" link on the right bar.</li>
<li>Search already contributed content and co-workers with the integrated search engine.</li>
<li>Connect with people by adding them to your network.</li>
</ul>

Working with TwistraNet is as easy as that!

<h1>Configuration and administration</h1>

If you want to configure and adminitrate TwistraNet, please read the /content/admin documentation.

""",
        permissions = "public",
    )
]

# MENU_STRUCTURE = (
#     "help", (
#         "admin",
#     )
# )
