from bson import ObjectId


def calculate_quiz_score(quiz, submitted_answers):

    total_score = 0
    max_score = 0
    detailed_results = []

    answer_map = {ans['question_id']: ans['answer_ids'] for ans in submitted_answers}

    for idx, question in enumerate(quiz.get('questions', [])):
        if '_id' in question:
            question_id = str(question['_id'])
        else:
            question_id = str(idx)  
            print(f"[Scoring] Warning: Question at index {idx} has no _id, using index")

        points = question.get('points', 0)
        penalty_points = question.get('penalty_points', 0)
        max_score += points

        submitted_answer_ids = answer_map.get(question_id, [])

        correct_answer_ids = []
        for ans_idx, ans in enumerate(question.get('answers', [])):
            if ans.get('correct', False):
                if '_id' in ans:
                    correct_answer_ids.append(str(ans['_id']))
                else:
                    correct_answer_ids.append(str(ans_idx))
                    print(f"[Scoring] Warning: Answer at index {ans_idx} in question {idx} has no _id, using index")

        points_earned = 0

        if len(correct_answer_ids) > 0:
            points_per_correct = points / len(correct_answer_ids)

            correct_selected = set(submitted_answer_ids) & set(correct_answer_ids)

            wrong_selected = set(submitted_answer_ids) - set(correct_answer_ids)

            points_earned = len(correct_selected) * points_per_correct

            if len(wrong_selected) > 0 and penalty_points > 0:
                points_earned -= len(wrong_selected) * penalty_points

            points_earned = max(0, points_earned)

        is_fully_correct = (set(submitted_answer_ids) == set(correct_answer_ids))

        total_score += points_earned

        detailed_results.append({
            'question_id': question_id,
            'submitted_answer_ids': submitted_answer_ids,
            'correct_answer_ids': correct_answer_ids,
            'correct': is_fully_correct,
            'points_earned': round(points_earned, 2),
            'points_possible': points,
            'correct_count': len(set(submitted_answer_ids) & set(correct_answer_ids)),
            'wrong_count': len(set(submitted_answer_ids) - set(correct_answer_ids))
        })

    return round(total_score, 2), max_score, detailed_results
