from derp.db_helper import Session, User, UserCourse, Course, Assignment


# TODO if someone could help me make this more dynamic that would be rad
if __name__ == '__main__':
    for i in [Session, User, UserCourse, Course, Assignment]:
        i.table_init()
    print("Database tables have been initialized")
