from derp.models import Account, Privilege
from sys import argv

# TODO specify these in the modules, and retrieve them in this script
# Also useful: identifying a set of permissions as the ones which constitute "admin"
# I'm sort of going about this like IRC permissions work. It allows fine-tuned flexibility,
# but perhaps more than we need?
ADMIN_PERMISSIONS = ['course:create', 'assignment:create']


if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: ./promote_to_admin.py <username>")
        exit(1)
    user = Account.query.filter_by(student_id=argv[1]).first()
    if not user:
        print("User {} could not be found.".format(argv[1]))
        exit(2)
    for perm in ADMIN_PERMISSIONS:
        Privilege(user, perm)
    print("User {} has been promoted to admin permissions".format(argv[1]))
