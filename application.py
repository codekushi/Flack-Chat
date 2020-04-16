import os
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask_socketio import *
from collections import deque

app = Flask(__name__)
app.config["SECRET_KEY"] = 'cs50project2bykushwanth'
socketio = SocketIO(app)

rooms = ["default"]
userlogged = ["default"]
roomchat = dict()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
       session['user'] = request.form.get("user")
       session['room'] = request.form.get("cname")
       if session['user'] in userlogged:
          return "username exits"
       userlogged.append(session['user'])
       if session['room']  not in rooms:
          rooms.append(session['room'])
       if session['room'] not in roomchat.keys():
          roomchat[session['room']] = deque()
       return render_template("channel.html", room=session['room'], user=session['user'], msgs=roomchat[session['room']])
    if request.method == "GET":
       if session.get('user') != None and session.get('room') != None:
          return render_template("channel.html", room=session['room'], user=session['user'], msgs=roomchat)
       return render_template("home.html", room=rooms)

@socketio.on('message')
def message(data):
    uname = session.get('user')
    cname = session.get('room')
    msg = data["msg"]
    time = datetime.now()
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    roomchat[cname].append([uname,msg,timestamp])
    if len(roomchat[cname]) > 100:
       roomchat[cname].popleft()
    join_room(cname)
    emit('roommsg', {'user': uname, 'time':timestamp, 'msg':msg}, room=cname)


@app.route("/logout", methods=['GET'])
def logout():
    try:
        userlogged.remove(session['user'])
    except ValueError:
        pass
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    socketio.run(app, debug=True)
