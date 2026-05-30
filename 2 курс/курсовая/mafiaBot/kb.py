from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
menu = [
    [InlineKeyboardButton(text="🎲 начать игру", callback_data="opening"),
    InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

async def send_player_selection_keyboard(chat_id: int, names):
    player_names = names.split()
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"select_{name}")]
        for name in player_names
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard