"""
Perform database repairings.
Handy for bootstraping the application!
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import syncdb

class Command(BaseCommand):
    args = ''
    help = 'Bootstrap your TwistraNet installation. Use this to load initial data and start playing with TN.'

    def handle(self, *args, **options):
        cmd = syncdb.Command()
        cmd.execute()
        from django_twistranet.twistranet.lib import dbsetup
        dbsetup.bootstrap()
        dbsetup.repair()
        print "Finished bootstraping. You can play with TwistraNet now."

