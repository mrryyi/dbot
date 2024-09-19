from flask import Flask, request, jsonify, render_template
from threading import Thread
import asyncio
from enum import Enum
from log import *
from typing import Final
import os
from discord import Intents, Client, Message, File  # Import the necessary classes
from dotenv import load_dotenv
from responses import *

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

app = Flask(__name__)

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

async def handle_web_message_response(user_message: str) -> str:
    try:
        response: Response = get_response(user_message)
        if not response:
            return "No response"
        return response.message
    except Exception as e:
        return str(e)

async def handle_discord_message_response(message: Message, user_message: str) -> None:
    if not user_message:
        log_warn_local('Received was empty.')
        return
    is_private: bool = user_message[0] == '?'
    if is_private:
        user_message = user_message[1]  # trim the '?'

    try:
        response: Response = get_response(user_message)
        if not response:
            return
        
        if is_private:
            await message.author.send(response.message, file=response.file)
        else:
            await message.channel.send(response.message, file=response.file)
    except Exception as e:
        log_exception_local(e)

@app.route('/')
def index():
    return render_template('index.html')

# Flask route to communicate with bot
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_message = data.get('message')
    if user_message:
        # This will return a response from the bot
        response = asyncio.run(handle_web_message_response(user_message))
        return jsonify({'response': response})
    return jsonify({'error': 'No message received.'}), 400

# Start Flask in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

@client.event
async def on_ready() -> None:
    log_inf_local(f'{client.user} is now running!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return # prevent infinite loop
    
    user_name:    str = str(message.author)
    user_message: str = message.content
    channel:      str = str(message.channel)

    print(f'[{channel}] {user_name}: {user_message}')
    
    if user_message != '':
        await handle_discord_message_response(message, user_message)

def main() -> None:
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()