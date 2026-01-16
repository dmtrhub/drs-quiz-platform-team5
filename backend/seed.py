#!/usr/bin/env python3
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src import create_app, db
from src.models.user import User


def create_test_users():
    """Create test users"""
    users = []

    # ======================
    # ADMINISTRATOR
    # ======================
    admin = User(
        first_name="Admin",
        last_name="Sistem",
        email="admin@quiz.com",
        date_of_birth=date(1985, 1, 15),
        gender="male",
        country="Srbija",
        street="Glavna ulica",
        street_number="1",
        role="admin",
        is_active=True
    )
    admin.set_password("Admin123!")
    users.append(admin)

    # ======================
    # MODERATORS
    # ======================
    moderator1 = User(
        first_name="Marko",
        last_name="Moderator",
        email="moderator1@quiz.com",
        date_of_birth=date(1990, 5, 20),
        gender="male",
        country="Srbija",
        street="Moderatorska",
        street_number="10",
        role="moderator",
        is_active=True
    )
    moderator1.set_password("Moderator123!")
    users.append(moderator1)

    moderator2 = User(
        first_name="Ana",
        last_name="Moderator",
        email="moderator2@quiz.com",
        date_of_birth=date(1992, 8, 12),
        gender="female",
        country="Crna Gora",
        street="Kvizna",
        street_number="25",
        role="moderator",
        is_active=True
    )
    moderator2.set_password("Moderator123!")
    users.append(moderator2)

    # ======================
    # PLAYERS
    # ======================
    player_data = [
        ("Petar", "Petrović", "petar.petrovic@quiz.com", date(1995, 3, 10), "male", "Srbija", "Kralja Petra", "123"),
        ("Jovana", "Jovanović", "jovana.jovanovic@quiz.com", date(1998, 7, 20), "female", "Srbija", "Kneza Mihaila",
         "456"),
        ("Nikola", "Nikolić", "nikola.nikolic@quiz.com", date(1993, 11, 5), "male", "Bosna i Hercegovina", "Titova",
         "789"),
        ("Marija", "Marković", "marija.markovic@quiz.com", date(2000, 2, 14), "female", "Crna Gora", "Njegoševa",
         "101"),
        ("Stefan", "Stefanović", "stefan.stefanovic@quiz.com", date(1997, 9, 30), "male", "Srbija",
         "Bulevar kralja Aleksandra", "202"),
        ("Milica", "Milić", "milica.milic@quiz.com", date(1994, 12, 25), "female", "Srbija", "Svetog Save", "303"),
        ("Dragan", "Dragić", "dragan.dragic@quiz.com", date(1991, 6, 18), "male", "Bosna i Hercegovina", "Mostarska",
         "404"),
        ("Sofija", "Sofić", "sofija.sofic@quiz.com", date(1999, 4, 8), "female", "Crna Gora", "Bokeška", "505"),
        ("Luka", "Lukić", "luka.lukic@quiz.com", date(1996, 8, 12), "male", "Srbija", "Sremska", "606"),
        ("Jelena", "Jelenić", "jelena.jelenic@quiz.com", date(1992, 10, 3), "female", "Srbija", "Vojvode Mišića",
         "707"),
    ]

    for i, (first_name, last_name, email, dob, gender, country, street, street_num) in enumerate(player_data, start=1):
        player = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=dob,
            gender=gender,
            country=country,
            street=street,
            street_number=street_num,
            role="player",
            is_active=True
        )
        player.set_password(f"Player{i}123!")
        users.append(player)

    return users


def seed_database():
    """Seed the database with test data"""
    print("Pokrećem seed skriptu...")

    app = create_app('development')

    with app.app_context():
        try:
            # Check if users already exist
            existing_users = User.query.count()

            if existing_users > 0:
                print(f"Baza već sadrži {existing_users} korisnika.")
                response = input("Želite li obrisati postojeće podatke? (da/ne): ")

                if response.lower() == 'da':
                    print("Brisanje postojećih podataka...")
                    # Delete all users
                    User.query.delete()
                    db.session.commit()
                    print("Postojeći podaci obrisani")
                else:
                    print("Prekidam - baza nije prazna.")
                    return

            # Create test users
            print("Kreiranje testnih korisnika...")
            test_users = create_test_users()

            for user in test_users:
                db.session.add(user)

            # Save to database
            db.session.commit()

            print(f"Uspešno kreirano {len(test_users)} testnih korisnika!")
            print("=" * 60)

            # Show created users
            for user in test_users:
                print(f"{user.first_name} {user.last_name}")
                print(f"{user.email}")
                print(f"Uloga: {user.role}")
                print(f"Lozinka: PlayerX123! (zamjeni X rednim brojem)")
                print("-" * 40)

            print("=" * 60)
            print("\nTESTNI KREDENCIJALI:")
            print("=" * 60)
            print(" ADMIN:")
            print("   Email: admin@quiz.com")
            print("   Lozinka: Admin123!")
            print("\n MODERATORI:")
            print("   Email: moderator1@quiz.com / moderator2@quiz.com")
            print("   Lozinka: Moderator123!")
            print("\n IGRAČI:")
            print("   Email: petar.petrovic@quiz.com (Player1)")
            print("   Lozinka: Player1 123!")
            print("   (Ostali: Player2 123!, Player3 123!, itd.)")
            print("=" * 60)
            print("\n Baza podataka uspešno popunjena!")

        except Exception as e:
            db.session.rollback()
            print(f" Greška pri populaciji baze: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    seed_database()