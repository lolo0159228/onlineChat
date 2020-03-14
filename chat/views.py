from django.shortcuts import render, HttpResponse
from dwebsocket.decorators import accept_websocket
from django.views.decorators.csrf import csrf_exempt
import uuid

OnlineUsers = {}

def SendToMsg(request):
    return render(request,'sendtoMsg.html')

def ReceiveMsg(request):
    return render(request, 'receiveMsg.html')

def chat(request):
    return render(request, 'chat.html')

@accept_websocket
def connect(request):
    if request.is_websocket():
        userID = str(uuid.uuid1())
        while True:
            message = request.websocket.wait()
            if not message:
                break
            else:
                print('USER連接成功')
                msg = '新成員->' + userID + '  加入聊天室'
                for user in OnlineUsers:
                    OnlineUsers[user].send(msg.encode('utf-8'))
                OnlineUsers[userID] = request.websocket


@csrf_exempt
def send(request):
    msg = request.POST.get('msg')
    for user in OnlineUsers:
        OnlineUsers[user].send(msg.encode('utf-8'))
    return HttpResponse({'msg':'成功發送訊息給所有user'})
