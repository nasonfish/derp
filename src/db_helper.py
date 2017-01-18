import datetime


# globals

# note: this is a gross hack for converting utc to local ... platform dependent and incorrect
#       in general ... do not assume that this will work without checking that it does!
TZ_OFFSET = datetime.datetime.now() - datetime.datetime.utcnow()


# TODO: wrap db queries into functions
