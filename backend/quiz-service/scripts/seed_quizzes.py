import os
from datetime import datetime
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB", "quiz_db")
SEED_AUTHOR_ID = int(os.environ.get("SEED_QUIZ_AUTHOR_ID", "1"))
SEED_AUTHOR_EMAIL = os.environ.get("SEED_QUIZ_AUTHOR_EMAIL", "seed@quizplatform.local")
SEED_APPROVED_BY_ADMIN_ID = int(os.environ.get("SEED_QUIZ_APPROVED_BY_ADMIN_ID", "1"))

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is required")


def q(text, answers, correct_index, points):
    if len(answers) < 3 or len(answers) > 5:
        raise ValueError("Each question must have 3 to 5 answers")
    if correct_index < 0 or correct_index >= len(answers):
        raise ValueError("correct_index out of range")
    return {
        "text": text,
        "answers": answers,
        "correct_index": correct_index,
        "points": points,
    }


QUIZ_BLUEPRINTS = [
    {
        "title": "General Knowledge Challenge",
        "description": "Mixed general knowledge quiz with one correct answer per question.",
        "duration_seconds": 900,
        "questions": [
            q("What is the capital of Canada?", ["Toronto", "Ottawa", "Vancouver", "Montreal"], 1, 5),
            q("Which planet is known as the Red Planet?", ["Mars", "Venus", "Jupiter"], 0, 6),
            q("What is the largest ocean on Earth?", ["Atlantic", "Indian", "Pacific", "Arctic"], 2, 7),
            q("Who painted the Mona Lisa?", ["Michelangelo", "Van Gogh", "Da Vinci", "Picasso"], 2, 8),
            q("How many continents are there?", ["5", "6", "7"], 2, 9),
            q("Which gas do plants absorb from the atmosphere?", ["Oxygen", "Carbon dioxide", "Nitrogen"], 1, 10),
            q("Which language has the most native speakers?", ["English", "Mandarin Chinese", "Spanish", "Hindi"], 1, 6),
            q("What is the smallest prime number?", ["0", "1", "2", "3"], 2, 7),
            q("What does CPU stand for?", ["Central Processing Unit", "Computer Primary Unit", "Core Processing Utility"], 0, 8),
            q("Which country hosted the 2016 Summer Olympics?", ["China", "Brazil", "UK", "Japan"], 1, 9),
        ],
    },
    {
        "title": "Mathematics Fundamentals",
        "description": "Core math concepts across algebra, geometry, and arithmetic.",
        "duration_seconds": 840,
        "questions": [
            q("What is 15% of 200?", ["20", "25", "30", "35"], 2, 5),
            q("Solve: 7 * 8", ["54", "56", "58"], 1, 6),
            q("What is the value of pi approximately?", ["2.14", "3.14", "4.13", "3.41"], 1, 7),
            q("What is the square root of 144?", ["10", "11", "12", "14"], 2, 8),
            q("A triangle with all equal sides is called?", ["Scalene", "Isosceles", "Equilateral"], 2, 9),
            q("What is 2^5?", ["10", "16", "32", "64"], 2, 10),
            q("Solve: 45 / 9", ["4", "5", "6"], 1, 6),
            q("What is the perimeter of a square with side 6?", ["12", "18", "24", "36"], 2, 7),
            q("What is 9 + 13?", ["21", "22", "23"], 1, 8),
            q("Which is an even number?", ["27", "31", "42", "55"], 2, 9),
        ],
    },
    {
        "title": "Physics Essentials",
        "description": "Basic mechanics, energy, and waves with practical examples.",
        "duration_seconds": 960,
        "questions": [
            q("What is the SI unit of force?", ["Joule", "Newton", "Watt", "Pascal"], 1, 5),
            q("Who formulated the laws of motion?", ["Einstein", "Newton", "Galileo"], 1, 6),
            q("What is the speed of light in vacuum?", ["300,000 km/s", "150,000 km/s", "30,000 km/s"], 0, 7),
            q("Which quantity is measured in volts?", ["Current", "Resistance", "Potential difference", "Power"], 2, 8),
            q("What type of lens is used to correct myopia?", ["Convex", "Concave", "Cylindrical"], 1, 9),
            q("Energy cannot be created or destroyed. This is:", ["Ohm's law", "Conservation of energy", "Snell's law"], 1, 10),
            q("What is acceleration due to gravity on Earth?", ["9.8 m/s^2", "4.9 m/s^2", "19.6 m/s^2"], 0, 6),
            q("Sound cannot travel through:", ["Water", "Air", "Vacuum", "Steel"], 2, 7),
            q("Unit of electrical resistance is:", ["Ohm", "Ampere", "Tesla"], 0, 8),
            q("Which wave is electromagnetic?", ["Sound wave", "Radio wave", "Water wave"], 1, 9),
        ],
    },
    {
        "title": "Chemistry Basics",
        "description": "Introductory chemistry from atoms to reactions.",
        "duration_seconds": 900,
        "questions": [
            q("Chemical symbol for gold is:", ["Gd", "Ag", "Au", "Go"], 2, 5),
            q("pH value below 7 indicates:", ["Acidic solution", "Neutral solution", "Basic solution"], 0, 6),
            q("Water formula is:", ["H2O", "CO2", "O2", "H2"], 0, 7),
            q("Atomic number represents number of:", ["Neutrons", "Protons", "Electrons and neutrons"], 1, 8),
            q("NaCl is commonly known as:", ["Sugar", "Salt", "Baking soda"], 1, 9),
            q("Gas essential for combustion is:", ["Nitrogen", "Oxygen", "Helium"], 1, 10),
            q("Periodic table was organized by:", ["Mendeleev", "Bohr", "Curie", "Dalton"], 0, 6),
            q("CH4 is:", ["Methane", "Ethane", "Propane"], 0, 7),
            q("A substance that speeds up reaction is:", ["Solvent", "Catalyst", "Acid"], 1, 8),
            q("Electron has:", ["Positive charge", "Negative charge", "No charge"], 1, 9),
        ],
    },
    {
        "title": "Biology and Life Sciences",
        "description": "Cell biology, genetics, and human body fundamentals.",
        "duration_seconds": 930,
        "questions": [
            q("Basic unit of life is:", ["Atom", "Cell", "Tissue"], 1, 5),
            q("DNA stands for:", ["Deoxyribonucleic acid", "Dynamic nucleic acid", "Dual nitrogen acid"], 0, 6),
            q("Human heart has how many chambers?", ["2", "3", "4"], 2, 7),
            q("Photosynthesis occurs in:", ["Mitochondria", "Chloroplast", "Nucleus"], 1, 8),
            q("Blood cells carrying oxygen are:", ["White blood cells", "Red blood cells", "Platelets"], 1, 9),
            q("Largest human organ is:", ["Liver", "Skin", "Brain", "Lung"], 1, 10),
            q("Which is a mammal?", ["Shark", "Dolphin", "Octopus"], 1, 6),
            q("Genetic material is stored in:", ["RNA only", "DNA", "Proteins"], 1, 7),
            q("Plants release which gas during photosynthesis?", ["Carbon dioxide", "Nitrogen", "Oxygen"], 2, 8),
            q("Human normal body temperature is about:", ["35 C", "37 C", "39 C"], 1, 9),
        ],
    },
    {
        "title": "World Geography",
        "description": "Countries, capitals, landmarks, and physical geography.",
        "duration_seconds": 900,
        "questions": [
            q("Longest river in the world is commonly listed as:", ["Amazon", "Nile", "Yangtze"], 1, 5),
            q("Mount Everest lies in:", ["Andes", "Himalayas", "Alps"], 1, 6),
            q("Capital of Australia is:", ["Sydney", "Melbourne", "Canberra"], 2, 7),
            q("Sahara is located in:", ["Asia", "Africa", "South America"], 1, 8),
            q("Japan is in which ocean region?", ["Pacific", "Atlantic", "Arctic"], 0, 9),
            q("Which country has the largest population?", ["India", "USA", "Indonesia", "Brazil"], 0, 10),
            q("Capital of Germany is:", ["Munich", "Berlin", "Frankfurt"], 1, 6),
            q("Which continent has the most countries?", ["Europe", "Africa", "Asia"], 1, 7),
            q("Iceland is known for many:", ["Volcanoes", "Deserts", "Rainforests"], 0, 8),
            q("The equator passes through:", ["Egypt", "Kenya", "Spain"], 1, 9),
        ],
    },
    {
        "title": "History Through Eras",
        "description": "Major historical events and figures across world history.",
        "duration_seconds": 960,
        "questions": [
            q("World War II ended in:", ["1943", "1945", "1947"], 1, 5),
            q("The Roman Empire was centered in:", ["Athens", "Rome", "Carthage"], 1, 6),
            q("Who discovered penicillin?", ["Einstein", "Fleming", "Pasteur"], 1, 7),
            q("The French Revolution began in:", ["1789", "1812", "1750"], 0, 8),
            q("The Great Wall is in:", ["India", "China", "Japan"], 1, 9),
            q("First man on the Moon was:", ["Yuri Gagarin", "Neil Armstrong", "Buzz Aldrin"], 1, 10),
            q("The Renaissance started in:", ["France", "Italy", "England"], 1, 6),
            q("UN was founded in:", ["1945", "1919", "1963"], 0, 7),
            q("Ancient pyramids are most associated with:", ["Greece", "Egypt", "Persia"], 1, 8),
            q("The Cold War was mainly between:", ["USA and USSR", "UK and Germany", "China and Japan"], 0, 9),
        ],
    },
    {
        "title": "Literature Classics",
        "description": "Authors, novels, and literary terminology.",
        "duration_seconds": 900,
        "questions": [
            q("Author of Hamlet is:", ["Charles Dickens", "William Shakespeare", "Jane Austen"], 1, 5),
            q("1984 was written by:", ["George Orwell", "Aldous Huxley", "Ernest Hemingway"], 0, 6),
            q("Pride and Prejudice author is:", ["Emily Bronte", "Jane Austen", "Mary Shelley"], 1, 7),
            q("Epic poem The Odyssey is attributed to:", ["Homer", "Virgil", "Socrates"], 0, 8),
            q("A story's main conflict and resolution form the:", ["Plot", "Theme", "Tone"], 0, 9),
            q("Don Quixote was written by:", ["Cervantes", "Kafka", "Tolstoy"], 0, 10),
            q("The Great Gatsby author is:", ["F. Scott Fitzgerald", "J. D. Salinger", "Mark Twain"], 0, 6),
            q("Poetry line grouping is called:", ["Chapter", "Stanza", "Paragraph"], 1, 7),
            q("War and Peace was written by:", ["Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov"], 0, 8),
            q("Metaphor compares things:", ["Using like/as", "Directly without like/as", "With numbers"], 1, 9),
        ],
    },
    {
        "title": "Computer Science Basics",
        "description": "Programming, networking, and system fundamentals.",
        "duration_seconds": 900,
        "questions": [
            q("HTTP stands for:", ["HyperText Transfer Protocol", "HighText Transmission Program", "Hyper Transfer Text Process"], 0, 5),
            q("Which data structure uses FIFO?", ["Stack", "Queue", "Tree"], 1, 6),
            q("Binary numbers use base:", ["2", "8", "10", "16"], 0, 7),
            q("SQL is mainly used for:", ["Image editing", "Database queries", "Audio processing"], 1, 8),
            q("Git command to upload local commits is:", ["git pull", "git clone", "git push"], 2, 9),
            q("Which is a backend language?", ["Python", "HTML", "CSS"], 0, 10),
            q("RAM is:", ["Permanent storage", "Volatile memory", "Network card"], 1, 6),
            q("Port commonly used by HTTPS is:", ["80", "21", "443"], 2, 7),
            q("API usually means:", ["Application Programming Interface", "Automated Program Index", "Applied Protocol Integration"], 0, 8),
            q("O(1) lookup is typical for:", ["Array index access", "Linear search", "Bubble sort"], 0, 9),
        ],
    },
    {
        "title": "Sports and Competitions",
        "description": "Popular sports, records, and global competitions.",
        "duration_seconds": 840,
        "questions": [
            q("How many players in a soccer team on field?", ["9", "10", "11"], 2, 5),
            q("Tennis Grand Slam tournament played on clay is:", ["Wimbledon", "US Open", "French Open"], 2, 6),
            q("Basketball hoop height is about:", ["3.05 m", "2.5 m", "4.0 m"], 0, 7),
            q("Olympic Games are held every:", ["2 years", "3 years", "4 years"], 2, 8),
            q("In volleyball, a set is usually won at:", ["15 points", "25 points", "30 points"], 1, 9),
            q("Formula 1 is primarily a:", ["Motor racing sport", "Sailing sport", "Cycling sport"], 0, 10),
            q("Cricket uses a:", ["Bat and ball", "Racket and shuttle", "Stick and puck"], 0, 6),
            q("The FIFA World Cup is for:", ["Basketball", "Soccer", "Rugby"], 1, 7),
            q("Marathon distance is about:", ["42.195 km", "21.1 km", "50 km"], 0, 8),
            q("In chess, checkmate means:", ["Draw", "King is trapped", "Pawn promoted"], 1, 9),
        ],
    },
    {
        "title": "Art and Music",
        "description": "Painting styles, composers, instruments, and art history.",
        "duration_seconds": 900,
        "questions": [
            q("The Starry Night was painted by:", ["Monet", "Van Gogh", "Rembrandt"], 1, 5),
            q("Piano belongs to which instrument family?", ["Percussion and string", "Wind", "Brass"], 0, 6),
            q("Beethoven was primarily a:", ["Painter", "Composer", "Poet"], 1, 7),
            q("Sculpture David was created by:", ["Michelangelo", "Donatello", "Raphael"], 0, 8),
            q("Tempo marking for very fast is:", ["Largo", "Adagio", "Presto"], 2, 9),
            q("Watercolor is typically applied with:", ["Brush and water", "Palette knife only", "Spray only"], 0, 10),
            q("Mona Lisa is displayed in:", ["Louvre Museum", "Prado Museum", "Uffizi Gallery"], 0, 6),
            q("A group of musicians performing together is an:", ["Ensemble", "Solo", "Canvas"], 0, 7),
            q("Primary colors in traditional art are:", ["Red, blue, yellow", "Red, green, blue", "Cyan, magenta, yellow"], 0, 8),
            q("Symphony is usually written for:", ["Solo voice", "Orchestra", "Single guitar"], 1, 9),
        ],
    },
    {
        "title": "Film and Pop Culture",
        "description": "Cinema basics, awards, and modern pop culture references.",
        "duration_seconds": 870,
        "questions": [
            q("Oscar awards are presented by:", ["BAFTA", "Academy of Motion Picture Arts and Sciences", "Golden Globes"], 1, 5),
            q("The movie medium predecessor to digital is:", ["Film reel", "Podcast", "E-book"], 0, 6),
            q("A sequel is:", ["Behind-the-scenes clip", "A continuation of a story", "A movie trailer"], 1, 7),
            q("IMDb is mainly known for:", ["Restaurant reviews", "Movie and TV database", "Music streaming"], 1, 8),
            q("The director is primarily responsible for:", ["Directing creative execution", "Selling tickets", "Running cinema projectors"], 0, 9),
            q("Box office refers to:", ["Movie revenue performance", "Movie script format", "Video resolution"], 0, 10),
            q("Animated movies are created using:", ["Only live actors", "Frame-by-frame visuals", "Only documentary footage"], 1, 6),
            q("Streaming platforms primarily deliver:", ["Physical DVDs", "On-demand digital content", "Printed magazines"], 1, 7),
            q("A film genre example is:", ["Comedy", "Tripod", "Subtitle"], 0, 8),
            q("A cameo is:", ["A brief appearance by a known person", "A camera model", "A studio logo"], 0, 9),
        ],
    },
]


def build_question(order, question_data):
    answers = []
    for idx, answer_text in enumerate(question_data["answers"], start=1):
        answers.append(
            {
                "_id": ObjectId(),
                "text": answer_text,
                "correct": idx - 1 == question_data["correct_index"],
                "order": idx,
            }
        )

    correct_count = sum(1 for item in answers if item["correct"])
    if correct_count != 1:
        raise ValueError(f"Question '{question_data['text']}' must have exactly one correct answer")

    return {
        "_id": ObjectId(),
        "order": order,
        "text": question_data["text"],
        "points": question_data["points"],
        "answers": answers,
    }


def build_quiz_document(quiz_blueprint):
    now = datetime.utcnow()
    questions = [
        build_question(order=idx + 1, question_data=question)
        for idx, question in enumerate(quiz_blueprint["questions"])
    ]

    return {
        "title": quiz_blueprint["title"],
        "description": quiz_blueprint["description"],
        "duration_seconds": quiz_blueprint["duration_seconds"],
        "questions": questions,
        "author_id": SEED_AUTHOR_ID,
        "author_email": SEED_AUTHOR_EMAIL,
        "status": "APPROVED",
        "approved_by_admin_id": SEED_APPROVED_BY_ADMIN_ID,
        "approval_notes": "Seeded for demo/testing",
        "updated_at": now,
    }


def seed_quizzes():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db.quizzes

    inserted = 0
    updated = 0

    for quiz_blueprint in QUIZ_BLUEPRINTS:
        quiz_doc = build_quiz_document(quiz_blueprint)
        result = collection.update_one(
            {
                "title": quiz_doc["title"],
                "author_id": SEED_AUTHOR_ID,
            },
            {
                "$set": quiz_doc,
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                },
            },
            upsert=True,
        )

        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    print(f"[SEED QUIZZES] Completed. Inserted: {inserted}, Updated: {updated}, Total: {len(QUIZ_BLUEPRINTS)}")


if __name__ == "__main__":
    seed_quizzes()
