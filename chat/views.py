from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from dwebsocket.decorators import accept_websocket
from django.views.decorators.csrf import csrf_exempt
import uuid
import json

OnlineUsers = {}

def entry(request):
    return render(request, 'entry.html',{'online':len(OnlineUsers)})

@accept_websocket
def chat(request):
    if request.method in ['POST']:
        global username
        username = request.POST.get('user')
        if username in OnlineUsers:
            return render(request, 'entry.html',{'online':len(OnlineUsers), 'err':'此暱稱已有人使用' })
        else:
            return render(request, 'chat.html', {'online':len(OnlineUsers)+1, 'users':OnlineUsers.keys()})

    if request.is_websocket():
        # userID = str(uuid.uuid1())
        while True:
            message = request.websocket.wait()
            if not message:
                if request.websocket.is_closed():
                    if request.session.get('user'):
                        msg = {
                            'id': request.session['user'],
                            'text': '成員->' + request.session['user'] + '  離開聊天室',
                            'type': -1
                        }
                        for user in OnlineUsers:
                            OnlineUsers[user].send(json.dumps(msg).encode('utf-8'))
                        del OnlineUsers[request.session['user']]
                    request.websocket.close()
                    return redirect(entry)
            else:
                print('USER連接成功')
                print(message.decode())  #message是bytes type
                if message.decode() == 'connected':
                    msg = {
                        'id':username,
                        'text': '新成員->' + username + '  加入聊天室',
                        'type': 0
                    }
                    #user第一次進入聊天室
                    request.websocket.send(json.dumps(msg).encode('utf-8'))
                    request.session['user'] = username
                    #通知所有user有新成員進入
                    msg['type'] = 1
                    for user in OnlineUsers:
                        OnlineUsers[user].send(json.dumps(msg).encode('utf-8'))
                    OnlineUsers[username] = request.websocket
    else:
        request.websocket.close()
        return redirect(entry())

@csrf_exempt
def send(request):
    msg = {
        'from': request.POST.get('from'),
        'text': request.POST.get('msg'),
        'type': 2
    }
    for user in OnlineUsers:
        OnlineUsers[user].send(json.dumps(msg).encode('utf-8'))
    return HttpResponse({'msg':'成功發送訊息給所有user'})
