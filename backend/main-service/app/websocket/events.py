from flask_socketio import emit, join_room, leave_room
from flask import request
from app.utils.jwt_utils import decode_jwt_token

def register_socketio_events(socketio):

    @socketio.on('connect')
    def handle_connect():
        print(f"[WebSocket] Client connected: {request.sid}")
        emit('connection_response', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"[WebSocket] Client disconnected: {request.sid}")

    @socketio.on('authenticate')
    def handle_authenticate(data):
        try:
            token = data.get('token')
            if not token:
                emit('error', {'message': 'No token provided'})
                return

            payload = decode_jwt_token(token)
            if not payload:
                emit('error', {'message': 'Invalid token'})
                return

            user_role = payload.get('role')
            user_id = payload.get('sub')

            if user_role == 'ADMIN':
                join_room('admin_room')
                print(f"[WebSocket] User {user_id} joined admin_room")
                emit('authenticated', {'role': user_role, 'room': 'admin_room'})
            elif user_role == 'MODERATOR':
                join_room('moderator_room')
                join_room(f'user_{user_id}')  
                print(f"[WebSocket] User {user_id} joined moderator_room")
                emit('authenticated', {'role': user_role, 'room': 'moderator_room'})
            else:
                join_room(f'user_{user_id}')
                emit('authenticated', {'role': user_role})

        except Exception as e:
            print(f"[WebSocket] Authentication error: {str(e)}")
            emit('error', {'message': 'Authentication failed'})

    @socketio.on('leave_room')
    def handle_leave_room(data):
        room = data.get('room')
        if room:
            leave_room(room)
            emit('left_room', {'room': room})


def emit_quiz_created(socketio, quiz_data):
    socketio.emit('new_quiz_created', quiz_data, room='admin_room')
    print(f"[WebSocket] Emitted new_quiz_created to admin_room")


def emit_quiz_approved(socketio, quiz_data, author_id):
    socketio.emit('quiz_approved', quiz_data, room=f'user_{author_id}')
    print(f"[WebSocket] Emitted quiz_approved to user_{author_id}")


def emit_quiz_rejected(socketio, quiz_data, author_id):
    socketio.emit('quiz_rejected', quiz_data, room=f'user_{author_id}')
    print(f"[WebSocket] Emitted quiz_rejected to user_{author_id}")


def emit_quiz_deleted(socketio, quiz_data, deleted_by_role):
    if deleted_by_role == 'MODERATOR':
        socketio.emit('quiz_deleted', quiz_data, room='admin_room')
        print(f"[WebSocket] Emitted quiz_deleted to admin_room")
    elif deleted_by_role == 'ADMIN':
        socketio.emit('quiz_deleted', quiz_data, room='moderator_room')
        print(f"[WebSocket] Emitted quiz_deleted to moderator_room")
