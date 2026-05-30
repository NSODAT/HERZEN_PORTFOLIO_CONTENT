from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import CallbackQuery
from config import *
import kb
import text
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
import utils
from states import Gen
import newdb
import time
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
logging.basicConfig(level=logging.DEBUG)


router = Router()
return_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])


@router.message(Command('начать игру'))
@router.callback_query(F.data == "opening")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.opening)
    await clbck.message.answer(text.genPl, reply_markup=kb.exit_kb)


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == "menu")
async def menu_handler(callback_query: CallbackQuery):
    await callback_query.message.answer(text.menu, reply_markup=kb.menu)


@router.message(Gen.opening)
async def RoleGen(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        # Создаем клавиатуру с кнопкой "Выйти в меню"
        instructions = "Пожалуйста, введите количество игроков в виде числа или подтвердите выход в меню."
        # Отправляем сообщение с инструкциями о вводе числа и кнопкой для возвращения в меню
        mess = await msg.answer(instructions, reply_markup=return_markup)
        return
    player_count = int(msg.text)
    if (player_count < 6) or (player_count > 15):
        instructions = "Пожалуйста, введите количество игроков в диапазоне от 6 до 15 или подтвердите выход в меню."
        await msg.answer(instructions, reply_markup=return_markup)
        return
    global db_manager
    db_manager = newdb.GameManager()
    db_manager.create_player_table()
    db_manager.create_game_table()
    game_key = msg.from_user.id
    print(f"Opening: GAMEKEY IS: {game_key}")
    db_manager.add_game(msg, player_count)
    global players
    players = await utils.generate_players(player_count, game_key)
    for i in range(1,player_count+1):
        db_manager.clear_conversations_by_queue(game_key,i)
    for player in players:
        if 'game_key' in player:
            db_manager.add_player(player["game_key"], player["queue"], player["role"],
                                     player["suit"], player["con1"], player["con2"],
                                     player["con3"], player["is_gamer"], player["name"])
        else:
        # Handle the case where 'game_key' is missing in the player dictionary
            print("Error: 'game_key' is missing for player:", player)
    mesg = await msg.answer(text.opening)
    Gamer_data = db_manager.get_gamer_summary(game_key)
    next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продолжить", callback_data="FirstDay")]])
    names = db_manager.get_players_names(game_key, player_count)
    chat_id = msg.chat.id
    mess = f"{names} Вошли в чат"
    mesg = await msg.answer(mess)
    mesg = await msg.answer(Gamer_data,reply_markup=next_markup)


@router.callback_query(F.data == "FirstDay")
async def menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    game_key = callback_query.from_user.id
    print(f"FirstDay: GAMEKEY IS: {game_key}")
    player_count = db_manager.get_current_game_player_count(game_key)
    names = db_manager.get_players_names(game_key, player_count)
    gamer_queue = db_manager.get_gamer_queue(game_key)
    CurrentGameQueue = db_manager.get_current_game_queue(game_key)
    if CurrentGameQueue > player_count: #Все жители познакомились, переходим в Фазу "Ночь"
        await state.set_state(Gen.Night)
        print("123")
        next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продолжить", callback_data="Night")]])
        mess = "Все жители выссказались, вечереет, собираемся по домам..."
        db_manager.update_current_game_queue(game_key,player_count)
        mesg = await callback_query.message.answer(mess,reply_markup=next_markup)
        return
    else:
        player = db_manager.get_player_data_by_queue(game_key,CurrentGameQueue)
        name = player[7]
        if gamer_queue == CurrentGameQueue:
            Setstate = Gen.DailyWaitingForReply
            mess = "Настала ваша очередь выссказаться, жители ждут вашей речи."
            await callback_query.message.answer(mess)
            await state.set_state(Setstate)
            return
        else:
            await asyncio.sleep(10)
            mess = f"{name} печатает...♻️"
            mesg = await callback_query.message.answer(mess)
            #try:
            chat_history =db_manager.save_last_messages(game_key, player_count)
            name = player[7]
            basemsg = f"Ответ на русском языке.Будь краток в ответе. Не пиши, что ты искусственный интеллект!Ты играешь в популярную игру Мафия, твое имя - {player[7]}, твоя роль {player[1]}, будь в образе, масть твоей роли - {player[2]}, расскажи о себе, о своих планах на игру, немного об участниках если тебе выдали любую роль, кроме мирного жителя, не пиши ее и масть, тем более, если ты мафия, старайся скрыть свои истинные планы, сейчас в игре находятся {player_count} игроков, их имена: {names}\n"
            converstation = basemsg+chat_history
            chat_gpt_response = await utils.gpt_us(converstation)
            reply = f"Сообщение от {player[7]}:\n{chat_gpt_response}\n"
            db_manager.update_conversations_by_queue(game_key,CurrentGameQueue,chat_gpt_response)
            next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="продолжить", callback_data="FirstDay")]])
            mesg = await callback_query.message.answer(reply, reply_markup = next_markup)
            db_manager.update_current_game_queue(game_key,player_count)
            #except Exception as e:
                #print(e)
                #instructions = "Извините, произошла ошибка в работе сервиса.Пожалуйста, подтвердите выход в меню и подтвердите попытку."
                #chat_gpt_response = "Извините, произошла ошибка."
                #mesg = await callback_query.message.answer(instructions, reply_markup=return_markup)
                #return
        
@router.message(Gen.DailyWaitingForReply)
async def process_message(message: types.Message, state: FSMContext) -> None:
    game_key = message.from_user.id
    user_message = message.text
    player_queue = db_manager.get_gamer_queue(message.from_user.id)
    player_count = db_manager.get_current_game_player_count(message.from_user.id)   
    db_manager.update_conversations_by_queue(game_key,player_queue, user_message)
    stateInfo = await state.get_state()
    match stateInfo:
        case Gen.DailyWaitingForReply:
            nexthandle = "FirstDay"
        case Gen.Day:
            nexthandle = "Day"
        case Gen.Night:
            nexthandle = "Night"
    next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продолжить", callback_data=nexthandle)]])
    mesg = await message.answer("Жители внимательно выслушали вас, они возьмут сказанное к сведению",reply_markup=next_markup)
    db_manager.update_current_game_queue(game_key, player_count)
    return


@router.callback_query(F.data == "Night")
async def Night_process(callback_query: CallbackQuery, state: FSMContext) -> None:
    game_key = callback_query.from_user.id

    CurrentGameQueue = db_manager.get_current_game_queue(game_key)
    player_count = db_manager.get_current_game_player_count(game_key)
    gamer_queue = db_manager.get_gamer_queue(game_key)
    player = db_manager.get_player_data_by_queue(game_key, CurrentGameQueue)
    player_names = db_manager.get_players_names(game_key, player_count)
    role = player[1]
    chat_history = db_manager.save_last_messages(game_key, player_count)
    name = player[7]

    if CurrentGameQueue > player_count:  # Ночь закончилась, переходим в фазу дня
        await state.set_state(Gen.Day)
        next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продолжить", callback_data="Day")]])
        mess = "Наступает утро, жители неохотно выбираются из домов для новых обсуждений"
        db_manager.update_current_game_queue(game_key, player_count)
        await callback_query.message.answer(mess, reply_markup=next_markup)
        return
    print(role)
    match role:
        case "Шериф":
            await handle_sheriff(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history)
        case "Доктор":
            await handle_doctor(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history)
        case "Мафия":
            await handle_mafia(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history)
        case "Мирный житель":
            db_manager.update_current_game_queue(game_key, player_count)
            await Night_process(callback_query, state)
            return

async def handle_sheriff(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history):
    print("Sheriff")
    searchedInfo = str(db_manager.get_night_info(game_key)[2])
    if CurrentGameQueue == gamer_queue:
        await callback_query.message.answer("Доброй ночи, шериф, этой ночью вы можете поискать улики в доме одного из игроков, выберете игрока для проверки:")
        keyboard = await kb.send_player_selection_keyboard(callback_query.message.chat.id, player_names)
        await callback_query.message.answer("Выберите игрока", reply_markup=keyboard)
    else:
        basemsg = f"Ответ на русском.Будь краток в ответе.Тебя зовут {name}, ты играешь в популярную игру мафия,{searchedInfo}, твоя роль - шериф, сейчас в игре {player_count} игроков, их имена {player_names}, наступила ночь, твоя задача выбрать игрока для проверки на то является ли он мафией или нет, если проверка покажет красную масть - значит это не мафия, выбери игрока из списка случайно или основываясь на его последних высказываниях(я использую парсер сообщений, поэтому в твоем ответе выбор игрока должен быть указан в следующем формате: Я выбрал - ([\\w\\s]+). ([\\w\\s]+): Группа захвата, которая будет содержать имя выбранного игрока.:\n"
        conversation = basemsg + chat_history
        chat_gpt_response = await utils.gpt_us(conversation)
        print(f'ОТЛАДКА РОЛИ ШЕРИФ ОТВЕТ ОТ ГПТ:{chat_gpt_response}')
        chosen_name = utils.extract_name_from_response(chat_gpt_response, player_names)
        print(f"ОТЛАДКА РОЛИ ШЕРИФ ВЫБРАННОЕ ИМЯ:{chosen_name}")
        if chosen_name:
            searchedInfo += chosen_name
            db_manager.update_game_info(game_key, "GotSearched", chosen_name)
        else:
            mess = f'{name}, случайно ударился об угол кровати, переукладываем его спать'
            await callback_query.message.answer(mess)
            await Night_process(callback_query, state)
            return
        db_manager.update_current_game_queue(game_key, player_count)
        await Night_process(callback_query, state)
        return

async def handle_doctor(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history):
    print("Doctor")
    healedInfo = db_manager.get_night_info(game_key)[1]
    if CurrentGameQueue == gamer_queue:
        await callback_query.message.answer("Доброй ночи, док, этой ночью мафия собирается напасть на одного из игроков, выберете, кого вы хотите навестить сегодня")
        keyboard = await kb.send_player_selection_keyboard(callback_query.message.chat.id, player_names)
        await callback_query.message.answer("Выберите игрока", reply_markup=keyboard)
    else:
        basemsg = f"Ответ на русском языке.Будь краток в ответе.Тебя зовут {name}, ты играешь в популярную игру мафия,твоя роль - доктор, сейчас в игре {player_count} игроков, их имена {player_names}, наступила ночь, твоя задача выбрать игрока кого вылечить этой ночью, выбери игрока из списка, кроме:{healedInfo}, потому, что прошлой ночью ты его лечил, случайно или основываясь на его последних высказываниях(я использую парсер сообщений, поэтому в твоем ответе выбор игрока должен быть указан в следующем формате: Я выбрал - ([\\w\\sа-яА-ЯёЁ]+). ([\\w\\sа-яА-ЯёЁ]+): Группа захвата, которая будет содержать имя выбранного игрока.:\n"
        conversation = basemsg + chat_history
        chat_gpt_response = await utils.gpt_us(conversation)
        print(f'ОТЛАДКА РОЛИ ДОКТОР ОТВЕТ ОТ ГПТ:{chat_gpt_response}')
        chosen_name = utils.extract_name_from_response(chat_gpt_response, player_names)
        print(f'ОТЛАДКА РОЛИ ДОКТОР ВЫБРАННОЕ ИМЯ:{chosen_name}')
        if chosen_name and chosen_name not in healedInfo:
            db_manager.update_game_info(game_key, "GotHealed", chosen_name)
        else:
            mess = f'{name}, случайно ударился об угол кровати, переукладываем его спать'
            await callback_query.message.answer(mess)
            await Night_process(callback_query, state)
            return
        db_manager.update_current_game_queue(game_key, player_count)
        await Night_process(callback_query, state)
        return

async def handle_mafia(callback_query, state, game_key, name, player_count, player_names, CurrentGameQueue, gamer_queue, chat_history): 
    # Получаем информацию о выборах на убийство
    killed_info = db_manager.get_night_info(game_key)[0] 
    killed_choices = killed_info.split() 

    # Получаем список мафиози
    mafiosi = db_manager.get_current_game_mafia(game_key) 
    mafiosi_list = mafiosi.split() 

    # Если еще не все мафиози проголосовали
    if len(killed_choices) < len(mafiosi_list): 
        # Если очередь текущего игрока
        if CurrentGameQueue == gamer_queue: 
            # Оповещаем игрока о его роли и предлагаем выбрать цель
            await callback_query.message.answer(f"Доброй ночи, {name}. Вы - мафиози. Вместе с вашей командой ({mafiosi}) выберите, кого убить сегодня. Ваш выбор:\n{killed_info}") 
            # Отправляем клавиатуру для выбора игрока
            keyboard = await kb.send_player_selection_keyboard(callback_query.message.chat.id, player_names) 
            await callback_query.message.answer("Выберите игрока", reply_markup=keyboard) 
            return
        else: 
            basemsg = f"Ответ на русском языке.Будь краток в ответе.Тебя зовут {name}, ты играешь в популярную игру мафия,твоя роль - мафия, твоя команда мафиози:{mafiosi}, сейчас в игре {player_count} игроков, их имена {player_names}, наступила ночь, твоя задача выбрать игрока кого убить этой ночью, выбери игрока из списка, сейчас на убийство наминированы{killed_info}, случайно или основываясь на его последних высказываниях(я использую парсер сообщений, поэтому в твоем ответе в конце должно быть указано: Я выбрал - ([\\w\\sа-яА-ЯёЁ]+). где ([\\w\\sа-яА-ЯёЁ]+): имя выбранного тобой игрока.:\n"
            conversation = basemsg + chat_history
            chat_gpt_response = await utils.gpt_us(conversation)
            print(f'ОТЛАДКА РОЛИ МАФИЯ ОТВЕТ ОТ ГПТ:{chat_gpt_response}')
            chosen_name = utils.extract_name_from_response(chat_gpt_response, player_names)
            print(f'ОТЛАДКА РОЛИ МАФИЯ ВЫБРАННОЕ ИМЯ:{chosen_name}')
            if chosen_name:
                db_manager.update_game_info(game_key, "GotHealed", chosen_name)
            else:
                mess = f'{name}, случайно ударился об угол кровати, переукладываем его спать'
                await callback_query.message.answer(mess)
                await Night_process(callback_query, state)
                return
            db_manager.update_current_game_queue(game_key, player_count)
            await Night_process(callback_query, state)
        return
    else:
        # Если все мафиози уже проголосовали
        # Рассчитываем голоса за каждого игрока
        votes = {}
        for choice in killed_choices:
            if choice in votes:
                votes[choice] += 1
            else:
                votes[choice] = 1
        # Находим игрока с наибольшим количеством голосов
        max_votes = max(votes.values())
        max_voted_players = [player for player, vote_count in votes.items() if vote_count == max_votes]
        
        if len(max_voted_players) == 1:
            # Если есть игрок с наибольшим количеством голосов
            target_player = max_voted_players[0]
            await callback_query.message.answer(f"Мафия выбрала свою цель на убийство. Цель: {target_player}.")
            # Обновляем базу данных с информацией о убийстве
            db_manager.update_killed_info(game_key, target_player)
        else:
            # Если нет однозначного выбора мафии
            await callback_query.message.answer("Мафия не смогла прийти к однозначному решению. Необходимо прийти к общему выбору.")
            # Обновляем killed_info до пустой строки и запрашиваем голоса у игроков
            db_manager.clear_killed_info(game_key)
            # Запускаем процесс голосования заново
            await Night_process(callback_query, state)
                          
@router.callback_query(F.data.startswith("select_"))
async def handle_player_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_name = callback_query.data.split("_")[1]
    game_key = callback_query.from_user.id
    player_count = db_manager.get_current_game_player_count(game_key)
    CurrentGameQueue = db_manager.get_current_game_queue(game_key)
    role = db_manager.get_player_role_by_queue(game_key,CurrentGameQueue)
    db_manager.update_current_game_queue(game_key, player_count)
    stateInfo = await state.get_state()
    print(stateInfo)
    match stateInfo:
        case Gen.DailyWaitingForReply:
            nexthandle = "FirstDay"
        case Gen.Day:
            nexthandle = "Day"
        case Gen.Night:
            nexthandle = "Night"
    next_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продолжить", callback_data=nexthandle)]])
    # Сохраните выбранного игрока в базе данных
    match role:
        case "Доктор":
            db_manager.doctor(game_key,selected_name)
            await callback_query.message.answer(f"Вы выбрали игрока: {selected_name}",reply_markup=next_markup)
        case "Мафия":
            db_manager.mafia(game_key,selected_name)
            await callback_query.message.answer(f"Вы выбрали игрока: {selected_name}",reply_markup=next_markup)
        case "Шериф":
            db_manager.police(game_key,selected_name)
            await callback_query.message.answer(f"Вы выбрали игрока: {selected_name}",reply_markup=next_markup)

@router.callback_query(F.data == "Day", Gen.Day)
async def Day_process(callback_query: CallbackQuery, state: FSMContext) -> None:
    return
    

    