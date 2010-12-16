# -*- coding: utf-8 -*-
"""
Some sample data in there.
"""
from twistranet.core import *
from twistranet.core.lib.python_fixture import Fixture
from django.contrib.auth.models import User
import random


N_DOCUMENTS = 10000
N_USERS = 1000
N_STATUS_UPDATES = 10000
N_COMMUNITIES = 1000

STATUS_UPDATES = [
    """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
    
    """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit. Ut velit mauris, egestas sed, gravida nec, ornare ut, mi. Aenean ut orci vel massa suscipit pulvinar. Nulla sollicitudin. Fusce varius, ligula non tempus aliquam, nunc turpis ullamcorper nibh, in tempus sapien eros vitae ligula. Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur aliquet pellentesque diam. Integer quis metus vitae elit lobortis egestas. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi vel erat non mauris convallis vehicula. Nulla et sapien. Integer tortor tellus, aliquam faucibus, convallis id, congue eu, quam. Mauris ullamcorper felis vitae erat. Proin feugiat, augue non elementum posuere, metus purus iaculis lectus, et tristique ligula justo vitae magna. Aliquam convallis sollicitudin purus. Praesent aliquam, enim at fermentum mollis, ligula massa adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce vulputate sem at sapien. Vivamus leo. Aliquam euismod libero eu enim. Nulla nec felis sed leo placerat imperdiet. Aenean suscipit nulla in justo. Suspendisse cursus rutrum augue. Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel rhoncus faucibus, felis magna fermentum augue, et ultricies lacus lorem varius purus. Curabitur eu amet.
    """,
    
    """Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?""",
    
    """But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?""",
    
    """At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.""",
    
    """On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue; and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided. But in certain circumstances and owing to the claims of duty or the obligations of business it will frequently occur that pleasures have to be repudiated and annoyances accepted. The wise man therefore always holds in these matters to this principle of selection: he rejects pleasures to secure other greater pleasures, or else he endures pains to avoid worse pains.""",
    ]


DOCUMENTS = STATUS_UPDATES

# From http://en.wikipedia.org/wiki/List_of_most_popular_given_names
FIRST_NAMES = [
    "Mohammed",	"Ahmed",	"Ali	Hamza",	"Ibrahim",	"Mahmoud",	"Abdallah",	"Tareq",	"Hassan",	"Khaled",
    "Aya","Rania","Sarah","Reem","Hoda","Marwa","Mona","Fatima","Eisha","Nesreen",
    "Oliver","Jack","Harry","Alfie","Thomas","Joshua","Charlie","William","James","Daniel",	
    "Mohamed-Amine","Jean-Baptiste","Pierre-Louis","Léo-Paul","Mohamed-Ali",
    "Lucas", "Mathis", "Noah", "Nathan", "Mathéo", "Enzo", "Louis", "Raphaël", "Ethan", "Gabriel",
    "Maximilian", "Alexander", "Leon", "Paul", "Luca", "Elias", "Felix", "Jonas", "David",
    "Olivia", "Ruby", "Emily", "Sophie", "Chloe", "Jessica", "Grace", "Lily", "Amelia", "Evie",
    "Emma", "Jade", "Chloé", "Sarah", "Léa", "Manon", "Louna", "Inès", "Lilou", "Camille",
    "Lou-Anne", "Lily-Rose", "Marie-Lou", "Fatima-Zahra", "Anne-Sophie",
    "Noam", "Itai", "Ori", "Daniel", "David", "Yonatan", "Yosef", "Ido", "Moshe", "Ariel",
    "Noa", "Shira", "Maya", "Tamar", "Yael", "Talia", "Sarah", "Hila", "Noya", "Michal",
    ]
    
# From http://en.wikipedia.org/wiki/List_of_most_common_surnames_in_Europe
LAST_NAMES = [
    "Smith","Jones","Taylor","Brown","Williams","Wilson","Johnson","Davies","Robinson","Wright","Thompson",
    "Evans","Walker","White","Roberts","Green","Hall","Wood","Jackson","Clarke","Martin","Bernard","Perrot",
    "Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau","Simon","Laurent","Lefebvre","Michel",
    "Garcia","David","Bertrand","Roux","Vincent","Fournier","Morel","Girard","André","Lefèvre","Mercier",
    "Dupont","Lambert","Bonnet","François","Martinez",
    ]

USERACCOUNT_PERMISSIONS = UserAccount.permission_templates.perm_dict.keys()
PICTURES = ['default_admin_picture', 'default_a_picture', 'default_b_picture']

FIXTURES = []
USERNAMES = []
COMMUNITIES = []

# Create users and add Admin as a friend
while True:
    rnd = random.randrange(0, 9999)
    if User.objects.filter(username = "user%i" % rnd).exists():
        continue
    if User.objects.filter(username = "user%i" % (rnd + N_USERS,)).exists():
        continue
    break
print "User range is %i to %i" % (rnd, rnd + N_USERS)

for i in range(rnd, rnd + N_USERS):
    # Basic user information
    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    pw = "azerty"
    username = "user%i" % i
    permission = random.choice(USERACCOUNT_PERMISSIONS)
    USERNAMES.append(username)
    
    # Create the actual user
    u = User.objects.create(
        username = username,
        password = pw,
        email = "%s@localhost" % (username,),
    )
    
    # Add the UserAccount fixture in the stack
    FIXTURES.append(
        Fixture(
            UserAccount,
            slug = username,
            title = "%s %s" % (fn, ln),
            description = "Sample user account %i for %s %s with %s permissions" % (i, fn, ln, permission),
            permissions = permission,
            user = User.objects.get(id = u.id),
            picture = Resource.objects.filter(slug = random.choice(PICTURES))
        )
    )
    
# Create N_COMMUNITIES communities and add a status update on each of them
print "Now creating %d communities" % N_COMMUNITIES
for i in range(N_COMMUNITIES):
    community_slug = "Community%s" % random.getrandbits(64)
    COMMUNITIES.append(community_slug)
    creator = random.choice(USERNAMES)
    FIXTURES.append(
        Fixture(
            Community,
            logged_account = creator,
            slug = community_slug,
            description = "Bulk community creation",
            permissions = random.choice(Community.permission_templates.perm_dict.keys()),
        )
    )
    FIXTURES.append(
        Fixture(
            StatusUpdate,
            logged_account = creator,
            slug = "SU%s" % community_slug,
            text = random.choice(STATUS_UPDATES),
            permissions = random.choice(StatusUpdate.permission_templates.perm_dict.keys()),
        ),
    )
    for i in range(N_DOCUMENTS / N_COMMUNITIES):
        FIXTURES.append(
            Fixture(
                Document,
                logged_account = creator,
                slug = "DOC%s-%s" % (community_slug, i),
                # publisher = random.choice([Account.objects.filter(slug = creator)]),
                title = random.choice(STATUS_UPDATES)[:50],
                description = random.choice(STATUS_UPDATES),
                text = random.choice(DOCUMENTS),
                permissions = random.choice(Document.permission_templates.perm_dict.keys()),
            ),
        )

# Create a bunch of status updates on each person's wall.
print "Generating %d status updates" % N_STATUS_UPDATES
for i in range(N_STATUS_UPDATES):
    slug = "status%s" % (random.getrandbits(64),)
    FIXTURES.append(
        Fixture(
            StatusUpdate,
            logged_account = random.choice(USERNAMES),
            slug = slug,
            text = random.choice(STATUS_UPDATES),
            permissions = random.choice(StatusUpdate.permission_templates.perm_dict.keys()),
        )
    )

# Apply fixtures.
__account__ = SystemAccount.objects.get()
for obj in FIXTURES:    obj.apply()

# Let users join communities. Each community can have 1-N_USERS/10 members
print "importing back communities"
for c in COMMUNITIES:
    community = Community.objects.get(slug = c)
    for n in range(random.randrange(0, N_USERS / 10)):
        u = UserAccount.objects.get(slug = random.choice(USERNAMES))
        # print "User %s joins %s" % (u, community)
        community.join(u)

# Admin should be friend with everybody
print "Make admin friend with everybody"
admin = UserAccount.objects.get(slug = "admin")
for u in USERNAMES:
    user = UserAccount.objects.get(slug = u)
    user.follow(admin)
    admin.follow(user)

