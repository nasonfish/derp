from derp import db
import derp.models

# TODO if someone could help me make this more dynamic that would be rad
if __name__ == '__main__':
    db.create_all()
    print("Database tables have been initialized")
