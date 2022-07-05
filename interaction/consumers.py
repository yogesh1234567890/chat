import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, Thread
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        # Join room group
        await (self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        if self.scope["user"].is_authenticated:
            await self.accept()
            await self.send(text_data=json.dumps({'status':'connected','type':'text_message'}))
        else:
            await self.close(code=4001)

    async def disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('disconnect', event)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('msg_type') =='text_message':
            message = text_data_json['message']

            sent_by_id = text_data_json.get('sent_by')
            send_to_id = text_data_json.get('send_to')
            thread_id = text_data_json.get('thread_id')
            is_video = text_data_json.get('is_video')
            
            if is_video:
                print('Error:: video called')
                return False

            if not message:
                print('Error:: empty message')
                return False

            sent_by_user =await self.get_user_object(sent_by_id)
            send_to_user =await self.get_user_object(send_to_id)
            thread_obj =await self.get_thread(thread_id)
            if not sent_by_user:
                print('Error:: sent by user is incorrect')
            if not send_to_user:
                print('Error:: send to user is incorrect')
            if not thread_obj:
                print('Error:: Thread id is incorrect')
            # Create ChatMessage object
            await self.create_chat_message(thread_obj, sent_by_user, message)


            other_user_chat_room = f'chat_{send_to_id}'
            self_user = self.scope['user']
            response = {
                'message': message,
                'sent_by': self_user.id,
                'thread_id': thread_id
            }

            # await self.channel_layer.group_send(
            #     other_user_chat_room,
            #     {
            #         'type': 'chat_message',
            #         'text': json.dumps(response)
            #     }
            # )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'text': json.dumps(response)
                }
            )
        
        elif(text_data_json.get('msg_type') =='offer'):

            sent_by_id = text_data_json['fromUser']
            send_to_id = text_data_json['toUser']
            is_video = text_data_json.get('is_video')
            offer = text_data_json.get('offer')
            

            # to notify the callee we sent an event to the group name
            # and their's groun name is the name
            # msg_id = uuid.uuid4()
            await self.channel_layer.group_send(
                     self.room_group_name,
                    {
                    'type': 'user_calling',
                    'fromUser': sent_by_id,
                    'toUser':send_to_id,
                    'offer': offer,
                    'msg_id' : send_to_id,
                    'is_video': is_video
                    }
                )
            
            mess = f'Calling by {sent_by_id}'
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'text': mess,
                        'msg_id' : send_to_id,
                        'fromUser': sent_by_id,
                        'toUser':send_to_id
                    }
                )    

        elif(text_data_json.get('msg_type') == "answer"):
            # answer = data.get('answer')
            # has received call from someone now notify the calling user
            # we can notify to the group with the caller name

            sent_by_id = text_data_json['fromUser']
            send_to_id = text_data_json['toUser']
            # is_video = text_data_json.get('is_video')
            answer = text_data_json.get('answer')
            # print(answer)
            

            
            await self.channel_layer.group_send(
                     self.room_group_name,
                    {
                    'type': 'user_answer_call',
                    'answer': answer,
                    'fromUser': sent_by_id,
                    'toUser':send_to_id
                    }
                )   

        elif(text_data_json.get('msg_type') == "candidate"):
            # candidate = data.get('candidate')
            sent_by_id = text_data_json['fromUser']
            send_to_id = text_data_json['toUser']
            candidate = text_data_json.get('candidate')
            # print(candidate)
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                    'type': 'ICEcandidate',
                    'candidate': candidate,
                    'fromUser': sent_by_id,
                    'toUser':send_to_id
                    }
                )     
         
    


    async def chat_message(self, event):
        print('message', event)
        await self.send(json.dumps({
            'type': 'websocket.send',
            'text': event
        }))



    async def user_calling(self, event):

        await self.send(text_data=json.dumps({
            'msg_type':'offer',
            'offer': event['offer'],
            'fromUser':  event["fromUser"],
            'toUser': event["toUser"]
        }))

    async def user_answer_call(self, event):

        await self.send(text_data=json.dumps({
            'msg_type': 'answer',
            'answer': event['answer'],
            'fromUser':  event["fromUser"],
            'toUser': event["toUser"]
        }))

    async def ICEcandidate(self, event):
        await self.send(text_data=json.dumps({
            'msg_type': 'candidate',
            'candidate': event['candidate'],
            'fromUser':  event["fromUser"],
            'toUser': event["toUser"]
        }))




    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, message):
        ChatMessage.objects.create(thread=thread, user=user, message=message)