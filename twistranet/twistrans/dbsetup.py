try:
    from twistrans.fixtures.help_fr import FIXTURES as HELP_FR_FIXTURES
except:
    print "unable to import"

def install_fixtures():
    """
    Install fixtures provided by this product
    """
    try:
        HELP_FR_FIXTURES
    except NameError:
        print "nameerror on HELP_FR_FIXTURES"
        return
    for obj in HELP_FR_FIXTURES:
        print obj.apply()
    print "OK, applied"
