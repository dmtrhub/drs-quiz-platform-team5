from flask import Blueprint, request, jsonify, Response
from app.utils.decorators import token_required
import requests
import os

quiz_proxy_bp = Blueprint('quiz_proxy', __name__)

QUIZ_SERVICE_URL = os.environ.get('QUIZ_SERVICE_URL', 'http://quiz-service:5001')
HOP_BY_HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade'
}
REWRITTEN_ENTITY_HEADERS = {'content-encoding', 'content-length'}

def forward_request(path, method='GET', include_body=True, extra_params=None):
    url = f"{QUIZ_SERVICE_URL}{path}"
    headers = {}

    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    if 'Content-Type' in request.headers:
        headers['Content-Type'] = request.headers['Content-Type']

    params = request.args.to_dict()
    if extra_params:
        params.update(extra_params)

    data = None
    if include_body and method in ['POST', 'PUT', 'PATCH']:
        data = request.get_json(silent=True)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            timeout=30
        )
        safe_headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in HOP_BY_HOP_HEADERS
            and k.lower() not in REWRITTEN_ENTITY_HEADERS
        }
        return Response(response.content, status=response.status_code, headers=safe_headers)

    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to connect to quiz service"}), 503


@quiz_proxy_bp.route('/quizzes', methods=['GET'])
@token_required
def get_quizzes():
    return forward_request('/quizzes', method='GET', include_body=False)

@quiz_proxy_bp.route('/quizzes/my-quizzes', methods=['GET'])
@token_required
def get_my_quizzes():
    return forward_request('/quizzes/my-quizzes', method='GET', include_body=False)

@quiz_proxy_bp.route('/quizzes/<quiz_id>', methods=['GET'])
@token_required
def get_quiz(quiz_id):
    return forward_request(f'/quizzes/{quiz_id}', method='GET', include_body=False)

@quiz_proxy_bp.route('/quizzes', methods=['POST'])
@token_required
def create_quiz():
    return forward_request('/quizzes', method='POST')

@quiz_proxy_bp.route('/quizzes/<quiz_id>', methods=['PUT'])
@token_required
def update_quiz(quiz_id):
    return forward_request(f'/quizzes/{quiz_id}', method='PUT')

@quiz_proxy_bp.route('/quizzes/<quiz_id>', methods=['DELETE'])
@token_required
def delete_quiz(quiz_id):
    return forward_request(f'/quizzes/{quiz_id}', method='DELETE', include_body=False)

@quiz_proxy_bp.route('/quizzes/<quiz_id>/attempts', methods=['POST'])
@token_required
def submit_quiz_attempt(quiz_id):
    return forward_request('/results/submit', method='POST', extra_params={'quiz_id': quiz_id})

@quiz_proxy_bp.route('/quizzes/pending', methods=['GET'])
@token_required
def get_pending_quizzes():
    return forward_request(f'/quizzes/pending', method='GET', include_body=False)

@quiz_proxy_bp.route('/quizzes/<quiz_id>/approve', methods=['PUT'])
@token_required
def approve_quiz(quiz_id):
    return forward_request(f'/quizzes/{quiz_id}/approve', method='PUT')

@quiz_proxy_bp.route('/quizzes/<quiz_id>/reject', methods=['PUT'])
@token_required
def reject_quiz(quiz_id):
    return forward_request(f'/quizzes/{quiz_id}/reject', method='PUT')

@quiz_proxy_bp.route('/results/submit', methods=['POST'])
@token_required
def submit_results():
    return forward_request('/results/submit', method='POST')

@quiz_proxy_bp.route('/results/my-results', methods=['GET'])
@token_required
def get_my_results():
    return forward_request('/results/my-results', method='GET', include_body=False)

@quiz_proxy_bp.route('/results/leaderboard/<quiz_id>', methods=['GET'])
@token_required
def get_leaderboard(quiz_id):
    return forward_request(f'/results/leaderboard/{quiz_id}', method='GET', include_body=False)

@quiz_proxy_bp.route('/reports/quiz/<quiz_id>', methods=['POST'])
@token_required
def create_pdf_report(quiz_id):
    return forward_request(f'/reports/quiz/{quiz_id}', method='POST')

@quiz_proxy_bp.route('/reports/result/<result_id>', methods=['GET'])
@token_required
def create_user_pdf_report(result_id):
    return forward_request(f'/reports/result/{result_id}', method='GET', include_body=False)