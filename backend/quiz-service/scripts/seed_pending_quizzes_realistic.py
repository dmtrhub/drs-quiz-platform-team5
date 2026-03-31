import os
from datetime import datetime
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

try:
    from seed_quizzes import QUIZ_BLUEPRINTS
except ImportError as exc:
    raise RuntimeError('Failed to import QUIZ_BLUEPRINTS from seed_quizzes.py') from exc

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB = os.environ.get('MONGO_DB', 'quiz_db')
TARGET_COUNT = int(os.environ.get('SEED_PENDING_QUIZ_COUNT', '12'))
SEED_TAG = 'realistic-pending-v1'

MODERATORS = [
    {'id': 5101, 'email': 'john.gotti@quizplatform.com'},
    {'id': 5102, 'email': 'sarah.connor@quizplatform.com'},
    {'id': 5103, 'email': 'michael.corleone@quizplatform.com'},
]

if not MONGO_URI:
    raise RuntimeError('MONGO_URI is required')


def build_question(order: int, question_data: dict) -> dict:
    answers = []
    for answer_index, answer_text in enumerate(question_data['answers'], start=1):
        answers.append(
            {
                '_id': ObjectId(),
                'text': answer_text,
                'correct': answer_index - 1 == question_data['correct_index'],
                'order': answer_index,
            }
        )

    return {
        '_id': ObjectId(),
        'order': order,
        'text': question_data['text'],
        'points': question_data['points'],
        'answers': answers,
    }


def build_pending_quiz(blueprint: dict, moderator: dict, ordinal: int) -> dict:
    now = datetime.utcnow()
    title_suffix = f"(Pending Review #{ordinal})"
    questions = [
        build_question(order=index + 1, question_data=question)
        for index, question in enumerate(blueprint['questions'])
    ]

    return {
        'title': f"{blueprint['title']} {title_suffix}",
        'description': f"{blueprint['description']} Submitted for moderation workflow review.",
        'duration_seconds': blueprint['duration_seconds'],
        'questions': questions,
        'author_id': moderator['id'],
        'author_email': moderator['email'],
        'status': 'PENDING',
        'seed_tag': SEED_TAG,
        'updated_at': now,
    }


def seed_pending_quizzes() -> None:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    quizzes = db.quizzes

    inserted = 0
    updated = 0

    for index in range(TARGET_COUNT):
        blueprint = QUIZ_BLUEPRINTS[index % len(QUIZ_BLUEPRINTS)]
        moderator = MODERATORS[index % len(MODERATORS)]
        quiz_doc = build_pending_quiz(blueprint, moderator, index + 1)

        result = quizzes.update_one(
            {
                'title': quiz_doc['title'],
                'author_id': quiz_doc['author_id'],
            },
            {
                '$set': quiz_doc,
                '$setOnInsert': {'created_at': datetime.utcnow()},
            },
            upsert=True,
        )

        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    pending_total = quizzes.count_documents({'status': 'PENDING'})
    by_authors = {
        moderator['email']: quizzes.count_documents({'author_id': moderator['id'], 'status': 'PENDING'})
        for moderator in MODERATORS
    }

    print(f"[SEED PENDING] Target={TARGET_COUNT} inserted={inserted} updated={updated} pending_total={pending_total}")
    for email, count in by_authors.items():
        print(f"  - {email}: pending={count}")


if __name__ == '__main__':
    seed_pending_quizzes()
