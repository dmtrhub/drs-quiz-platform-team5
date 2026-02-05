from marshmallow import Schema, fields, validates, ValidationError


class AnswerSchema(Schema):
    text = fields.Str(required=True)
    correct = fields.Boolean(required=True)
    order = fields.Int(required=True)


class QuestionSchema(Schema):
    order = fields.Int(required=True)
    text = fields.Str(required=True)
    points = fields.Int(required=True)
    answers = fields.List(fields.Nested(AnswerSchema), required=True)

    @validates('answers')
    def validate_answers(self, value):
        if len(value) < 2:
            raise ValidationError("Question must have at least 2 answers")
        correct_count = sum(1 for ans in value if ans.get('correct'))
        if correct_count < 1:
            raise ValidationError("Question must have at least one correct answer")


class CreateQuizSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    duration_seconds = fields.Int(required=True)
    questions = fields.List(fields.Nested(QuestionSchema), required=True)

    @validates('questions')
    def validate_questions(self, value):
        if len(value) < 1:
            raise ValidationError("Quiz must have at least one question")


class UpdateQuizSchema(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False, allow_none=True)
    duration_seconds = fields.Int(required=False)
    questions = fields.List(fields.Nested(QuestionSchema), required=False)


class ApprovalSchema(Schema):
    notes = fields.Str(required=False, allow_none=True)


class RejectionSchema(Schema):
    reason = fields.Str(required=True)


class SubmitAnswersSchema(Schema):
    question_id = fields.Str(required=True)
    answer_ids = fields.List(fields.Str(), required=True)


class QuizSubmissionSchema(Schema):
    answers = fields.List(fields.Nested(SubmitAnswersSchema), required=True)
    time_spent_seconds = fields.Int(required=True)
