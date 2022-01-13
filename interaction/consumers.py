import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, Thread
User = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({'status':'connected'}))


        # async def websocket_connect(self, event):
    #     
    #     user = self.scope['user']
    #     chat_room = f'user_chatroom_{user.id}'
    #     self.chat_room = chat_room
    #     await self.channel_layer.group_add(
    #         chat_room,
    #         self.channel_name
    #     )
    #     await self.send({
    #         'type': 'websocket.accept'
    #     })


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']

        sent_by_id = text_data_json.get('sent_by')
        send_to_id = text_data_json.get('send_to')
        thread_id = text_data_json.get('thread_id')

        if not message:
            print('Error:: empty message')
            return False


        sent_by_user =self.get_user_object(sent_by_id)
        send_to_user =self.get_user_object(send_to_id)
        thread_obj =self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')
        # Create ChatMessage object
        print(thread_obj, sent_by_user, message)
        self.create_chat_message(thread_obj, sent_by_user, message)


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_user_object(self, user_id):
        print(user_id)
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        print(qs)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, message):
        ChatMessage.objects.create(thread=thread, user=user, message=message)