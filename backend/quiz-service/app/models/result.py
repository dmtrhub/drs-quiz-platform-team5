from bson import ObjectId
from datetime import datetime


class ResultModel:

    def __init__(self, mongo_db):
        self.collection = mongo_db.results

    def create_result(self, result_data):
        result_data['submitted_at'] = datetime.utcnow()
        result = self.collection.insert_one(result_data)
        return str(result.inserted_id)

    def find_result_by_id(self, result_id):
        return self.collection.find_one({'_id': ObjectId(result_id)})

    def find_results_by_quiz(self, quiz_id):
        return list(self.collection.find({'quiz_id': ObjectId(quiz_id)}).sort([('score', -1), ('time_spent_seconds', 1)]))

    def find_results_by_user(self, user_id):
        return list(self.collection.find({'user_id': user_id}).sort('submitted_at', -1))

    def get_leaderboard(self, quiz_id, limit=10):
        pipeline = [
            {'$match': {'quiz_id': ObjectId(quiz_id)}},
            {'$sort': {'score': -1, 'time_spent_seconds': 1}},
            {'$group': {
                '_id': '$user_id',
                'user_id': {'$first': '$user_id'},
                'score': {'$first': '$score'},
                'max_score': {'$first': '$max_score'},
                'time_spent_seconds': {'$first': '$time_spent_seconds'},
                'submitted_at': {'$first': '$submitted_at'}
            }},
            {'$sort': {'score': -1, 'time_spent_seconds': 1}},
            {'$limit': limit}
        ]
        return list(self.collection.aggregate(pipeline))

    def update_result_rank(self, result_id, rank):
        result = self.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': {'ranked_position': rank}}
        )
        return result.modified_count > 0

    def calculate_user_rank(self, quiz_id, score, time_spent):
        better_results = self.collection.count_documents({
            'quiz_id': ObjectId(quiz_id),
            '$or': [
                {'score': {'$gt': score}},
                {'score': score, 'time_spent_seconds': {'$lt': time_spent}}
            ]
        })
        return better_results + 1
