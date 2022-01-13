from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
# Create your views here.
from .models import Thread


def index(request):
    user = request.user.username
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads,
        'use':user
    }
    return render(request, 'chat.html', context)

def room(request, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })

@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads
    }
    return render(request, 'discussions.html', context)
