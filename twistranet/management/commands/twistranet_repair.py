"""
Perform database repairings.
Handy for bootstraping the application!
"""

from django.core.management.base import BaseCommand, CommandError
from twistranet.lib import dbsetup

class Command(BaseCommand):
    args = ''
    help = 'Repairs TwistraNet data. Useful when migrating existing data.'

    def handle(self, *args, **options):
        dbsetup.repair()
        print "Finished repairing. You can safely use TwistraNet now."

