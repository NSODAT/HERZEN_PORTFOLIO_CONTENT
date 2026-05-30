import g4f
import g4f.Provider
import config
import sqlite3
import newdb
import asyncio
from aiogram.types import Message
from g4f import client
from g4f.client import AsyncClient
import random
import re

_providers = [
    g4f.Provider.Cohere,
    g4f.Provider.Pi,
    g4f.Provider.Blackbox,
    g4f.Provider.HuggingChat,
]

def extract_name_from_response(response: str, player_names: list) -> str:
    # Регулярное выражение для извлечения имени из сообщения
    match = re.match(r"Я выбрал - ([\w\sа-яА-ЯёЁ]+)", response)
    if match:
        chosen_name = match.group(1).strip()
        if chosen_name in player_names:
            return chosen_name
    return None

async def gpt_us_send_mess(ComparedMessage,provider:g4f.Provider.BaseProvider):
    try:
        response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": ComparedMessage}],
                provider=provider,
            )
        chat_gpt_response = response
        return chat_gpt_response
    except Exception as e:
        print(f"{provider.__name__}:", e)

async def gpt_us(ComparedMessage):
    tasks = [
        gpt_us_send_mess(ComparedMessage, provider) for provider in _providers
    ]
    for task in asyncio.as_completed(tasks):
        response = await task
        if response is not None:
            cleaned_response = re.sub(r'\$@\$.+?\$@\$', '', response)
            return cleaned_response
    return None


    
async def generate_players(player_count, game_key):
    Gamer = random.randint(1, player_count)
    Gamer = 1
    # Определение ролей
    mafia_count = int(player_count // 3.5)
    roles = ['Мирный житель'] * (player_count - mafia_count)
    roles.extend(['Мафия'] * mafia_count)
    roles.extend(['Доктор', 'Шериф'])
    names = ["Фетучинни", "Макиавелли", "Шегги", "Базилик",
              "Фелиция", "Саманта", "Роуз", "Герда", "Курт",
                "Савелий", "Шершень", "Элизабет", "Ханна",
                  "Виолетта", "Чарльз", "Грегорри", "Витто",
                  "Альварэ","Донателло","Альма","Сальваторе"]
    for i in range(player_count):
        random.shuffle(roles)
        random.shuffle(names)

    # Генерация данных игроков
    players = []
    for i in range(player_count):
        player = {
            'game_key': game_key,
            'queue': i + 1,
            'role': roles[i],
            'suit': 'Черный' if roles[i] == 'Мафия' else 'Красный',
            'con1': [],
            'con2': [],
            'con3': [],
            'is_gamer': True if i == Gamer else False,
            'name': names[i]
        }
        players.append(player)
    return players

async def add_generated_players_to_db(db_manager, player_count):
    players = await generate_players(player_count)
    for player in players:
        db_manager.add_player(player['queue'], player['role'], player['suit'],
                               player['con1'], player['con2'], player['con3'],
                               player['isgamer'], player['name'])



