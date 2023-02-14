from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import json

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI websockets</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var json_object = JSON.parse(event.data)
                var content = document.createTextNode(json_object['message'])
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                if (input.value === '') {
                    alert('Message cannot be empty')
                } else {
                    ws.send(JSON.stringify({message : input.value}))
                    input.value = ''
                    
                }
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

# Пусть и не самый оптимальный способ хранения данных, но задумка была в том, чтобы мы
# с этого массива переносили в другой, дабы можно было хрнаить сообщения, но и удалять при обновлении
# отсюда
messages = []

@app.get("/")
async def get():
    global messages
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global messages
    await websocket.accept()
    while True:
        data_raw = await websocket.receive_text()
        data = json.loads(data_raw) # Распаковка JSON объекта
        messages.append(data['message'])
        json_object = json.dumps({'message' : str(len(messages)) + ' - '+ data['message']}) # Создание JSON обьекта
        await websocket.send_text(json_object)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
