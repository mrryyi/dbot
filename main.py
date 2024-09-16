from log import *
from typing import Final
import os
from discord import Intents, Client, Message, File  # Import the necessary classes
from dotenv import load_dotenv
from responses import *

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        log_err_local('Received was empty.')
        return
    is_private: bool = user_message[0] == '?'
    if is_private:
        user_message = user_message[1]  # trim the '?'

    try:
        response: Response = get_response(user_message)
        if response:
            if is_private:
                await message.author.send(response.message, file=response.file)
            else:
                await message.channel.send(response.message, file=response.file)
    except Exception as e:
        log_err_local(e)

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
        await send_message(message, user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()