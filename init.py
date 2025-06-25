from app import db, User, PersonalInfo
import datetime

db.create_all()

Admin_user = User("admin@gmail.com", "Admin", "111", "1")
db.session.add(Admin_user)
db.session.commit()

personalinfo1 = PersonalInfo(1, 9.5)
db.session.add(personalinfo1)
db.session.commit()


