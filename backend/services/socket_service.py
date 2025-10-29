"""
Socket.IO Service untuk Real-time Chat
Miluv.app
"""

import socketio
import os
from typing import Dict, Set
from dotenv import load_dotenv

load_dotenv()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=os.getenv('SOCKET_CORS_ORIGINS', '*'),
    logger=True,
    engineio_logger=False
)

# Store active connections: {user_id: sid}
active_users: Dict[str, str] = {}

# Store user rooms (match_id): {match_id: Set[user_id]}
match_rooms: Dict[str, Set[str]] = {}


@sio.event
async def connect(sid, environ, auth):
    """
    Handle client connection
    Client harus kirim auth token
    """
    print(f"Client connected: {sid}")
    
    # Get user_id from auth
    user_id = auth.get('user_id') if auth else None
    
    if user_id:
        active_users[user_id] = sid
        print(f"User {user_id} connected with sid {sid}")
        
        # Emit connection success
        await sio.emit('connected', {'user_id': user_id}, room=sid)
    else:
        print(f"Anonymous connection: {sid}")


@sio.event
async def disconnect(sid):
    """Handle client disconnect"""
    # Remove from active users
    user_id = None
    for uid, user_sid in active_users.items():
        if user_sid == sid:
            user_id = uid
            break
    
    if user_id:
        del active_users[user_id]
        print(f"User {user_id} disconnected")
        
        # Remove from all rooms
        for match_id, users in match_rooms.items():
            if user_id in users:
                users.remove(user_id)


@sio.event
async def join_chat(sid, data):
    """
    User bergabung ke chat room
    data = {
        "user_id": str,
        "match_id": str
    }
    """
    user_id = data.get('user_id')
    match_id = data.get('match_id')
    
    if not user_id or not match_id:
        await sio.emit('error', {'message': 'user_id and match_id required'}, room=sid)
        return
    
    # Add to room
    await sio.enter_room(sid, match_id)
    
    # Track in match_rooms
    if match_id not in match_rooms:
        match_rooms[match_id] = set()
    match_rooms[match_id].add(user_id)
    
    print(f"User {user_id} joined chat {match_id}")
    
    # Notify others in room
    await sio.emit(
        'user_joined',
        {'user_id': user_id, 'match_id': match_id},
        room=match_id,
        skip_sid=sid
    )


@sio.event
async def leave_chat(sid, data):
    """
    User keluar dari chat room
    data = {
        "user_id": str,
        "match_id": str
    }
    """
    user_id = data.get('user_id')
    match_id = data.get('match_id')
    
    if not user_id or not match_id:
        return
    
    # Remove from room
    await sio.leave_room(sid, match_id)
    
    # Remove from match_rooms
    if match_id in match_rooms and user_id in match_rooms[match_id]:
        match_rooms[match_id].remove(user_id)
    
    print(f"User {user_id} left chat {match_id}")
    
    # Notify others
    await sio.emit(
        'user_left',
        {'user_id': user_id, 'match_id': match_id},
        room=match_id
    )


@sio.event
async def send_message(sid, data):
    """
    Kirim pesan real-time
    data = {
        "match_id": str,
        "sender_id": str,
        "message_id": str,
        "content": str,
        "type": str,  # text, image, voice
        "created_at": str
    }
    """
    match_id = data.get('match_id')
    sender_id = data.get('sender_id')
    
    if not match_id or not sender_id:
        await sio.emit('error', {'message': 'Invalid message data'}, room=sid)
        return
    
    print(f"Message from {sender_id} to {match_id}: {data.get('content', '')[:50]}")
    
    # Broadcast to all users in chat room (except sender)
    await sio.emit(
        'new_message',
        data,
        room=match_id,
        skip_sid=sid
    )
    
    # Send delivery confirmation to sender
    await sio.emit(
        'message_sent',
        {'message_id': data.get('message_id'), 'status': 'delivered'},
        room=sid
    )


@sio.event
async def typing_start(sid, data):
    """
    User mulai mengetik
    data = {
        "match_id": str,
        "user_id": str
    }
    """
    match_id = data.get('match_id')
    user_id = data.get('user_id')
    
    if match_id and user_id:
        await sio.emit(
            'user_typing',
            {'user_id': user_id},
            room=match_id,
            skip_sid=sid
        )


@sio.event
async def typing_stop(sid, data):
    """
    User berhenti mengetik
    data = {
        "match_id": str,
        "user_id": str
    }
    """
    match_id = data.get('match_id')
    user_id = data.get('user_id')
    
    if match_id and user_id:
        await sio.emit(
            'user_stop_typing',
            {'user_id': user_id},
            room=match_id,
            skip_sid=sid
        )


@sio.event
async def message_read(sid, data):
    """
    Mark message as read
    data = {
        "match_id": str,
        "message_id": str,
        "reader_id": str
    }
    """
    match_id = data.get('match_id')
    
    if match_id:
        await sio.emit(
            'message_read_receipt',
            data,
            room=match_id,
            skip_sid=sid
        )


# Helper functions untuk emit dari backend

async def notify_new_match(user_a_id: str, user_b_id: str, match_id: str):
    """
    Notify both users tentang match baru
    """
    match_data = {
        'match_id': match_id,
        'message': "It's a match!"
    }
    
    # Notify user A
    if user_a_id in active_users:
        await sio.emit('new_match', match_data, room=active_users[user_a_id])
    
    # Notify user B
    if user_b_id in active_users:
        await sio.emit('new_match', match_data, room=active_users[user_b_id])


async def notify_message_saved(match_id: str, message_data: Dict):
    """
    Notify setelah message disimpan ke database
    """
    await sio.emit('message_saved', message_data, room=match_id)


def get_active_users() -> Dict[str, str]:
    """Get dictionary of active users"""
    return active_users.copy()


def get_user_status(user_id: str) -> bool:
    """Check if user is online"""
    return user_id in active_users


def get_room_users(match_id: str) -> Set[str]:
    """Get users in a chat room"""
    return match_rooms.get(match_id, set()).copy()
