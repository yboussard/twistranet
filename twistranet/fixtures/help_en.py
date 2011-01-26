from twistranet.twistapp.models import *
from twistranet.content_types.models import *
from twistranet.twistapp.lib.python_fixture import Fixture

__account__ = SystemAccount.get()

FIXTURES = [
    Fixture(
        Document,
        force_update = True,
        slug = "help",
        publisher = GlobalCommunity.objects.get_query_set(),
        title = "TwistraNet Help",
        description = "TwistraNet is a social network "
        "tailored for enterprise needs. Learn how to use it within 10 minutes.",
        text = """<h2>Getting started</h2>
<p>
If you can read that document, that probably means you're already connected to TwistraNet!
If you're not logged-in, <a href="/login">login now</a>.
</p>
<table width="100%">
    <tr>
        <th width="33%">
            <p>Find your co-workers</p>
            [address_64]
        </th>
        <th width="33%">
            <p>Share with your network</p>
            [bubble_64]
        </th>
        <th width="33%">
            <p><a href="/content/new/Document">Publish content</a></p>
            [document_64]
        </th>
   </tr>
    <tr>
        <td>
            <p><strong>Who are you working the most with?</strong></p>
            <p>Find your co-workers and add them to your network. It's the easiest
            way to stay in touch with what they're doing.</p>
        </td>
        <td>
            <p><strong>What are you working on? Do you need some help?</strong></p>
            <p>
            Do you have an advice or a quick information to give to your co-workers?<br />
            You're only two clicks away from doing it right now!
            </p>
        </td>
        <td>
            <p><strong>Have a report, a memo, a template to share??</strong></p>
            <p>
            Don't spam your co-workers, use a <a href="/content/new/Document">Document</a>.
            Your network will know you've got something to say,
            and your other co-workers will be able to find it
            easily.
            </p>
        </td>
    </tr>
</table>

Working with TwistraNet is as easy as that!

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

    Fixture(
        Document,
        force_update = True,
        slug = "help_communities",
        publisher = GlobalCommunity.objects.get_query_set(),
        title = "TwistraNet Help: Communities",
        description = "Communities are a simple way to organize "
        "people and content with TwistraNet. Learn how to use them.",
        text = """<h2>About communities</h2>
<p>
Communities are spaces in twistranet where you can work in team.<br />
<strong>A community is like an intranet you can create in a few seconds!</strong><br />
</p>
<p>
Inside a community, members share status updates, documents and other content.
They can work together and publish (or not!) their work when they're done.
</p>
<p>
And you can do so much more with communities.
</p>
<table width="100%">
    <tr>
        <th width="33%">
            <p>Teamwork, teamwork, teamwork!</p>
            [diagram_64]
        </th>
        <th width="33%">
            <p>Easy blogging</p>
            [bubble_64]
        </th>
        <th width="33%">
            <p>Involve stakeholders</p>
            [heart_64]
        </th>
   </tr>
    <tr>
        <td>
            <p><strong>Working in teams has never been so cool</strong></p>
            <p>
                When you create a workgroup, you can share documents, files
                and even thoughs with your colleagues.
            </p>
            <p>
                No more "send-to-all" / "reply-to-all" emails all day long!
            </p>
            <p>
                And if your team expands as your project grows, newcomers find
                all the messages and documents history within the community.<br />
                This way, it's easier to let new people jump in!
            </p>
        </td>
        <td>
        </td>
        <td>
        </td>
    </tr>
</table>

<p>
Communities are easy to create and manage, so don't hesitate, create one and
start inviting people in it!
</p>

""",
        permissions = "public",
    ),

    Fixture(
        MenuItem,
        slug = "menuitem_help_communities",
        parent = MenuItem.objects.filter(slug = "menuitem_help"),
        order = 90,
        target = Document.objects.filter(slug = "help_communities"),
        title = "Communities",
        picture = Resource.objects.filter(slug = "default_community_picture"),
    ),


]



