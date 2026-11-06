from app import app
from backend.models.user import User

with app.app_context():

    users = User.query.all()

    print("\n========== REGISTERED USERS ==========")
    print("Total users:", len(users))

    for user in users:
        print("ID:", user.id)
        print("Name:", user.name)
        print("Email:", user.email)
        print("Password hash exists:", bool(user.password_hash))
        print("--------------------------------------")

    print("======================================")