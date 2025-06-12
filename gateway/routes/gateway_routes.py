# adapte : Na API: 
# @strategies_bp.route('/chat')
# def chat():
#     # return 'oi'
#     return render_template('chat.html')

# @strategies_bp.route('/chat/create', methods=['POST'])
# def create_chat():    
#     new_chat = Message()
#     db.session.add(new_chat)
#     db.session.commit()
#     return jsonify({"success": "Chat created!", "id": new_chat.id}), 200

# @strategies_bp.route('/chat/show', methods=['GET'])
# def show_chats():
#     all_chats = Message.query.all()
#     return jsonify([{"id": c.id, "messages": c.messages} for c in all_chats]), 200

# @strategies_bp.route('/chat/<int:chat_id>', methods=['GET'])
# def get_chat(chat_id):
#     chat = Message.query.get(chat_id)
#     if chat:
#         return jsonify(chat.as_dict()), 200
#     return jsonify({"error": "Chat not found"}), 404

# @strategies_bp.route('/chat/<int:chat_id>/add_message', methods=['POST'])
# def add_message(chat_id):
#     chat = Message.query.get(chat_id)
#     if chat:
#         username = request.json.get('username')
#         content = request.json.get('content')
#         chat.messages.append({"username": username, "content": content})
#         db.session.commit()
#         return jsonify(chat.as_dict()), 200
#     return jsonify({"error": "Chat not found"}), 404


# # Criar uma nova mensagem privada
# @strategies_bp.route('/private_chat/send', methods=['POST'])
# def send_private_message():
#     data = request.json
#     msg = PrivateMessage(
#         sender_id=data['sender_id'],
#         receiver_id=data['receiver_id'],
#         content=data['content']
#     )
#     db.session.add(msg)
#     db.session.commit()
#     return jsonify(msg.as_dict()), 201

# # Obter histórico entre dois usuários
# @strategies_bp.route('/private_chat/history', methods=['GET'])
# def get_private_messages():
#     sender_id = request.args.get('sender_id', type=int)
#     receiver_id = request.args.get('receiver_id', type=int)
    
#     messages = PrivateMessage.query.filter(
#         ((PrivateMessage.sender_id == sender_id) & (PrivateMessage.receiver_id == receiver_id)) |
#         ((PrivateMessage.sender_id == receiver_id) & (PrivateMessage.receiver_id == sender_id))
#     ).order_by(PrivateMessage.timestamp).all()
    
#     return jsonify([m.as_dict() for m in messages]), 200


# NO GATEWAY;


# @socketio.on('message')
# def handle_message(data):
#     id = data.get('id')
#     username = data.get('username')
#     content = data.get('content')

#     mensagem = {
#         "username": username,
#         "content": content
#     }

#     mensagem_as_dic = requests.post(f"{STRATEGIES_URL}/chat/{id}/add_message", json=mensagem).json()
 
    
#     # enviar para todos os clientes
#     send(mensagem_as_dic, broadcast=True)

# @socketio.on('load_messages')
# def handle_load_messages(data):
#     id = data.get('id') 
#     mensagem_as_dic = requests.get(f"{STRATEGIES_URL}/chat/{id}").json()
#     send(mensagem_as_dic, broadcast=True)


# @socketio.on('private_message')
# def handle_private_message(data):
#     sender_id = data.get('sender_id')
#     receiver_id = data.get('receiver_id')
#     content = data.get('content')

#     msg = {
#         "sender_id": sender_id,
#         "receiver_id": receiver_id,
#         "content": content
#     }

#     response = requests.post(f"{STRATEGIES_URL}/private_chat/send", json=msg)
#     if response.status_code == 201:
#         send(response.json(), broadcast=True)  # ou para um grupo específico depois

# @socketio.on('load_private_messages')
# def handle_load_private_messages(data):
#     sender_id = data.get('sender_id')
#     receiver_id = data.get('receiver_id')
#     response = requests.get(
#         f"{STRATEGIES_URL}/private_chat/history",
#         params={"sender_id": sender_id, "receiver_id": receiver_id}
#     )
#     if response.status_code == 200:
#         send(response.json(), broadcast=True)


# connected_users = {}  # username -> socket_id

# @socketio.on('connect')
# def on_connect():
#     print("Client connected")

# @socketio.on('disconnect')
# def on_disconnect():
#     for user, sid in list(connected_users.items()):
#         if sid == request.sid:
#             del connected_users[user]
#             break
#     socketio.emit('update_users', list(connected_users.keys()))

# @socketio.on('register_username')
# def register_username(data):
#     username = data.get("username")
#     connected_users[username] = request.sid
#     socketio.emit('update_users', list(connected_users.keys()))
