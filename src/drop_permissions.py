from derp.db_helper import User, DerpDB
from sys import argv

if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: ./drop_permissions.py <username>")
        exit(1)
    user = DerpDB.user_query(student_id=argv[1])
    if not user:
        print("User {} could not be found.".format(argv[1]))
        exit(2)
    DerpDB.drop_permissions(user)
    print("User {}'s permissions have been revoked.".format(argv[1]))
