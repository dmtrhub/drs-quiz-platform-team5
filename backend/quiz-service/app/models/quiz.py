from bson import ObjectId
from datetime import datetime


class QuizModel:
    """MongoDB model for Quiz collection"""

    def __init__(self, mongo_db):
        self.collection = mongo_db.quizzes

    def create_quiz(self, quiz_data):
        """Create a new quiz"""
        quiz_data['created_at'] = datetime.utcnow()
        quiz_data['updated_at'] = datetime.utcnow()
        quiz_data['status'] = 'PENDING'
        result = self.collection.insert_one(quiz_data)
        return str(result.inserted_id)

    def find_quiz_by_id(self, quiz_id):
        """Find quiz by ID"""
        return self.collection.find_one({'_id': ObjectId(quiz_id)})

    def find_all_quizzes(self, filter_dict=None):
        """Find all quizzes with optional filter"""
        if filter_dict is None:
            filter_dict = {}
        return list(self.collection.find(filter_dict))

    def update_quiz(self, quiz_id, update_data):
        """Update quiz"""
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(quiz_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_quiz(self, quiz_id):
        """Delete quiz"""
        result = self.collection.delete_one({'_id': ObjectId(quiz_id)})
        return result.deleted_count > 0

    def approve_quiz(self, quiz_id, admin_id, notes=None):
        """Approve a quiz"""
        update_data = {
            'status': 'APPROVED',
            'approved_by_admin_id': admin_id,
            'approval_notes': notes,
            'updated_at': datetime.utcnow()
        }
        return self.update_quiz(quiz_id, update_data)

    def reject_quiz(self, quiz_id, admin_id, reason):
        """Reject a quiz"""
        update_data = {
            'status': 'REJECTED',
            'rejected_by_admin_id': admin_id,
            'rejection_reason': reason,
            'updated_at': datetime.utcnow()
        }
        return self.update_quiz(quiz_id, update_data)

    def get_pending_quizzes(self):
        """Get all pending quizzes"""
        return self.find_all_quizzes({'status': 'PENDING'})

    def get_approved_quizzes(self):
        """Get all approved quizzes"""
        return self.find_all_quizzes({'status': 'APPROVED'})
