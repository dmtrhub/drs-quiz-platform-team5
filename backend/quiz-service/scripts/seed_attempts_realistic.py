import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB = os.environ.get('MONGO_DB', 'quiz_db')
TARGET_QUIZ_TITLE = os.environ.get('SEED_ATTEMPTS_QUIZ_TITLE')
SEED_ALL_QUIZZES = os.environ.get('SEED_ATTEMPTS_ALL_QUIZZES', 'true').lower() in ('1', 'true', 'yes', 'on')
SEED_TAG = 'realistic-attempts-v1'

USERS = [
    {'id': 5101, 'name': 'John Gotti'},
    {'id': 5102, 'name': 'Sarah Connor'},
    {'id': 5103, 'name': 'Michael Corleone'},
    {'id': 5104, 'name': 'Emma Watson'},
    {'id': 5105, 'name': 'David Beckham'},
    {'id': 5106, 'name': 'Olivia Wilde'},
    {'id': 5107, 'name': 'Ethan Hawke'},
    {'id': 5108, 'name': 'Amelia Earhart'},
    {'id': 5109, 'name': 'Daniel Craig'},
    {'id': 5110, 'name': 'Sophia Loren'},
    {'id': 5111, 'name': 'Liam Neeson'},
    {'id': 5112, 'name': 'Ava Gardner'},
    {'id': 5113, 'name': 'Noah Webster'},
    {'id': 5114, 'name': 'Nina Simone'},
    {'id': 5115, 'name': 'Oscar Isaac'},
]

if not MONGO_URI:
    raise RuntimeError('MONGO_URI is required')


def compute_max_score(quiz: dict) -> int:
    return int(sum(int(question.get('points', 0)) for question in quiz.get('questions', [])))


def pick_target_quizzes(quizzes_collection):
    if TARGET_QUIZ_TITLE:
        quiz = quizzes_collection.find_one({'title': TARGET_QUIZ_TITLE})
        if not quiz:
            raise RuntimeError(f"Quiz '{TARGET_QUIZ_TITLE}' was not found")
        return [quiz]

    if SEED_ALL_QUIZZES:
        approved = list(quizzes_collection.find({'status': 'APPROVED'}).sort([('updated_at', -1)]))
        if approved:
            return approved

    newest = quizzes_collection.find_one({'status': 'APPROVED'}, sort=[('updated_at', -1)])
    if not newest:
        newest = quizzes_collection.find_one({}, sort=[('updated_at', -1)])
    if not newest:
        raise RuntimeError('No quizzes available for attempt seeding')
    return [newest]


def seed_attempts() -> None:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    quizzes = db.quizzes
    results = db.results

    target_quizzes = pick_target_quizzes(quizzes)
    base_time = datetime.utcnow() - timedelta(days=2)

    inserted = 0
    updated = 0

    for quiz_index, quiz in enumerate(target_quizzes):
        quiz_id = quiz['_id']
        quiz_title = quiz.get('title', 'Untitled Quiz')
        duration_seconds = int(quiz.get('duration_seconds') or 900)
        max_score = compute_max_score(quiz)

        for user_index, user in enumerate(USERS):
            base_percent = max(52, 96 - user_index * 3)
            first_score = round(max_score * (base_percent / 100.0), 2)
            second_score = round(max(first_score - max_score * 0.08, max_score * 0.35), 2)

            first_time = min(max(80, int(duration_seconds * 0.42 + user_index * 7)), max(duration_seconds - 10, 90))
            second_time = min(duration_seconds, first_time + 32)

            attempts = [
                (1, first_score, first_time),
                (2, second_score, second_time),
            ]

            for attempt_no, score, spent_seconds in attempts:
                filter_doc = {
                    'seed_tag': SEED_TAG,
                    'quiz_id': quiz_id,
                    'user_id': user['id'],
                    'attempt_no': attempt_no,
                }
                update_doc = {
                    '$set': {
                        'quiz_id': quiz_id,
                        'quiz_title': quiz_title,
                        'user_id': user['id'],
                        'user_name': user['name'],
                        'score': float(score),
                        'max_score': float(max_score),
                        'time_spent_seconds': int(spent_seconds),
                        'submitted_answers': [],
                        'ranked_position': 0,
                        'seed_tag': SEED_TAG,
                        'attempt_no': attempt_no,
                        'submitted_at': base_time + timedelta(minutes=(quiz_index * 40) + (user_index * 3) + attempt_no),
                    }
                }

                result = results.update_one(filter_doc, update_doc, upsert=True)
                if result.upserted_id:
                    inserted += 1
                else:
                    updated += 1

        print(f"[SEED ATTEMPTS] Quiz='{quiz_title}' users={len(USERS)} attempts/user=2")

    print(f"[SEED ATTEMPTS] Target quizzes={len(target_quizzes)} inserted={inserted} updated={updated}")


if __name__ == '__main__':
    seed_attempts()
