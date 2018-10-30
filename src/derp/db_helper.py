import datetime


# globals

# note: this is a gross hack for converting utc to local ... platform dependent and incorrect
#       in general ... do not assume that this will work without checking that it does!
# UTC_OFFSET = datetime.datetime.now() - datetime.datetime.utcnow()
UTC_OFFSET = datetime.timedelta(hours = 8)  # worse hack ... difference between PT and UTC


# TODO: wrap db queries into functions
