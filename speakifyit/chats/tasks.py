import ujson as json
from celery import shared_task
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from annoying.functions import get_object_or_None
from .signals import create_message
from .models import Room, Notification, Message, MessageChart
from speakifyit.users.models import ContactRequest
from .serializers import NotificationSerializer

from django.core import serializers
from django.forms.models import model_to_dict


@shared_task
def create_message_task(**kwargs):

	if kwargs['msg_type'] == 4:
		content = '{} joined the room'.format(kwargs['user'].username)
	elif kwargs['msg_type'] == 5:
		content = '{} left the room'.format(kwargs['user'].username)		

	if not content:
		content = kwargs['content']

	room = get_object_or_None(Room, kwargs['room'])

	if room:
		msg = Message.objects.create(
			user = kwargs['user'], content = content, msg_type = kwargs['msg_type'] 
		)


@shared_task
def send_notification(**kwargs):
	notification = Notification.objects.create(
		from_user = kwargs['from_user'],
		to_user = kwargs['to_user'],
		msg_type = kwargs['msg_type'],
		content = kwargs['content'],
		icon = kwargs['icon'],
		link = kwargs['link'],
		contact_request = kwargs['contact_request']
		)

	user = kwargs['from_user']
	data = NotificationSerializer(notification).data
	user.websocket_group.send(
		{"text": json.dumps(data)}
	)


@shared_task
def message_edit(**kwargs):
	message = get_object_or_None(Nessage, pk=kwargs['message'])
	if message:
		message.content = kwargs['content']
		message.is_editable = False
		nessage.save()
		chart = MessageChart.objects.create(message=message)


@receiver(create_message, sender=Room)
def receiver_create_message(sender, *args, **kwargs):
	create_message_task.apply_async(kwargs=kwargs)


@receiver(post_save, sender=Room)
def send_created_room_notification(sender, instance, created, **kwargs):
	if created:
		pass

@receiver(post_save, sender=ContactRequest)
def send_requset_notification(sender, instance, created, **kwargs):

	if created:
		content = 'User {} wants to add you to the chat'.format(instance.request_from)
		msg_type = 'create_request'
		from_user = instance.request_to
		to_user = instance.request_from
	
	else:

		if instance.accepted is True:
			content = 'User {} added you to the chat'.format(instance.request_to),
			msg_type = 'create_request'
			from_user = instance.request_from
			to_user = instance.request_to

			room = Room.objects.create()
			room.users.add(instance.request_from, instance.request_to)
			room.save()

		else:
			from_user = instance.request_to
			to_user = instance.request_from
			content = 'User {} wants to add you to the chat'.format(instance.request_from),
			msg_type = 'create_request'			
		
	send_notification.apply_async(kwargs={
		'from_user': from_user,
		'to_user': to_user,
		'msg_type': msg_type,
		'content': content,
		'icon':'',
		'link':'',
		'contact_request': instance
		})
