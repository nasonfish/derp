from derp import db
from derp.models import Account
from sys import argv

if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: ./drop_permissions.py <username>")
        exit(1)
    user = Account.query.filter_by(student_id=argv[1]).first()
    if not user:
        print("User {} could not be found.".format(argv[1]))
        exit(2)
    for i in user.privileges:
        db.session.delete(i)
    db.session.commit()
    print("User {}'s permissions have been revoked.".format(argv[1]))
