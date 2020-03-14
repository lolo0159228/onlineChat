from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from dwebsocket.decorators import accept_websocket
from django.views.decorators.csrf import csrf_exempt
import uuid

OnlineUsers = {}

def entry(request):
    return render(request, 'entry.html',{'online':len(OnlineUsers)})

@accept_websocket
def chat(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('user')
        if username in OnlineUsers:
            return render(request, 'entry.html',{'online':len(OnlineUsers), 'err':'此暱稱已有人使用'})
        else:
            return render(request, 'chat.html')

    if request.is_websocket():
        userID = str(uuid.uuid1())
        while True:
            message = request.websocket.wait()
            if not message:
                break
            else:
                print('USER連接成功')
                msg = '新成員->' + username + '  加入聊天室'
                for user in OnlineUsers:
                    OnlineUsers[user].send(msg.encode('utf-8'))
                OnlineUsers[username] = request.websocket

# @accept_websocket
# def connect(request):
#



@csrf_exempt
def send(request):
    msg = request.POST.get('msg')
    for user in OnlineUsers:
        OnlineUsers[user].send(msg.encode('utf-8'))
    return HttpResponse({'msg':'成功發送訊息給所有user'})
