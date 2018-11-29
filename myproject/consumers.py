#!/usr/bin/env python
# -*- coding:utf-8 -*-

# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json

class ChatConsumer__A(WebsocketConsumer):
    """
    channel 未使用ChannelLayer, 该为同步消费者(WebsocketConsumer)
    """
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # print("channel_name:", self.channel_name)
        text_data_json = json.loads(text_data)
        print("text_data:", text_data_json)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


############################################################################


class ChatConsumer__B(WebsocketConsumer):
    """
    channel 使用ChannelLayer，该为同步消费者(WebsocketConsumer)
    当用户发布消息时，JavaScript函数将通过WebSocket将消息传输到ChatConsumer。
    ChatConsumer将接收该消息并将其转发到与房间名称对应的组。
    然后，同一组中的每个ChatConsumer（因此在同一个房间中）将接收来自该组的消息，
    并通过WebSocket将其转发回JavaScript，并将其附加到聊天日志中。
    """
    def connect(self):
        """
        建立ws连接
        :return:
        """
        print("Scope:", self.scope)
        print("Channel_Name:", self.channel_name)
        #scope 包含有关其连接的信息，特别是包括URL路由中的任何位置或关键字参数以及当前经过身份验证的用户
        #从url中获取房间名
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        #设置channge_group组名
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        # 将当前的channel名称(self.channel_name)加入到指定的组中.
        #async_to_sync（...）包装器是必需的，因为ChatConsumer是同步WebsocketConsumer，
        # 但它调用异步通道层方法。（所有通道层方法都是异步的。）
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        #接受WebSocket连接。如果不在connect（）方法中调用accept（），则拒绝并关闭连接。
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        #指定当前channel离开指定组
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        """
        从当前channel获取到websocket的消息，并将该信息发给其所在的组
        :param text_data:
        :return:
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

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
        """
        从当前channel所属组中获取消息并发送给websocket客户端
        :param event:
        :return:
        """
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


##############################################################################

class ChatConsumer(AsyncWebsocketConsumer):
    """
    异步消费者AsyncWebsocketConsumer
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))