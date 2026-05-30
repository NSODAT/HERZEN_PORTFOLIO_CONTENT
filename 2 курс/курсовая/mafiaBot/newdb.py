import sqlite3
from aiogram.types import Message
class GameManager:
    def __init__(self, db_name='game.db'):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_game_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game (
            game_key INTEGER PRIMARY KEY,
            game_state TEXT,
            GotKilled TEXT,
            GotHealed TEXT,
            GotSearched TEXT,
            player_count INTEGER,
            CurrentQueue INTEGER
        )
        ''')
        self.connection.commit()

    def create_night_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS mafia (
            player_id INTEGER PRIMARY KEY,
            game_key INTEGER,
            role TEXT,
            con1 TEXT,
            con2 TEXT,
            con3 TEXT,
            name TEXT,
            FOREIGN KEY (game_key) REFERENCES game(game_key)
        )
        ''')

    def create_player_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            player_id INTEGER PRIMARY KEY,
            game_key INTEGER,  
            queue INTEGER,
            role TEXT,
            suit TEXT,
            con1 TEXT,
            con2 TEXT,
            con3 TEXT,
            is_gamer TEXT,
            name TEXT,
            FOREIGN KEY (game_key) REFERENCES game(game_key)
        )
        ''')
        self.connection.commit()

    def add_game(self, msg, player_count):
    # Проверяем, существует ли уже игра с таким ключом
        sql_query = f"SELECT * FROM game WHERE game_key = ?"
        existing_game = self.cursor.execute(sql_query, (msg.from_user.id,)).fetchone()

        if existing_game is not None:
        # Если игра существует, удаляем ее из базы данных
            self.cursor.execute("DELETE FROM game WHERE game_key = ?", (msg.from_user.id,))
            self.cursor.execute("DELETE FROM player WHERE game_key = ?", (msg.from_user.id,))
            self.connection.commit()

    # Добавляем новую игру
        baseinteger = 1
        baseInfo = ""
        sql_query = f"INSERT INTO game(game_key, game_state, GotKilled, GotHealed, GotSearched, player_count, CurrentQueue) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(sql_query, (msg.from_user.id, baseInfo, baseInfo, baseInfo, "Тебе известно, что:", player_count, baseinteger))
        self.connection.commit()

    def get_game_state_info(self, game_key):
        game_data = self.get_game_data(game_key)
        if game_data is not None:
            game_key, game_state, GotKilled, GotHealed, GotSearched, game_note, player_count, CurrentQueue = game_data
            return game_state
        else:
            return None
        
    def get_night_info(self, game_key):
        game_data = self.get_game_data(game_key)
        if game_data is not None:
            game_key,game_state, GotKilled, GotHealed, GotSearched, player_count, CurrentQueue = game_data
            return GotKilled, GotHealed, GotSearched
        else:
            return None, None, None
        
    def update_game_info(self, game_key, field_name, value):
        query = f'''
        UPDATE game
        SET {field_name} = ?
        WHERE game_key = ?
        '''
        self.cursor.execute(query, (value, game_key))
        self.connection.commit()

    def get_current_game_mafia(self, game_key, player_count, CheckingRole="Мафия"):
        names = []
        for i in range(1, player_count+1):
            player_data = self.get_player_data_by_queue(game_key, i)
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            if role == CheckingRole: 
                names.append(name)
        Mafios = ' '.join(names)
        return Mafios
        
    def get_game_data(self, game_key):
        self.cursor.execute('''
        SELECT game_key, game_state, GotKilled, GotHealed, GotSearched, player_count, CurrentQueue FROM game WHERE game_key=?
        ''', (game_key,))
        return self.cursor.fetchone()
    
    def get_current_game_player_count(self, game_key):
        game_data = self.get_game_data(game_key)
        if game_data is not None:
            game_key, game_state, GotKilled, GotHealed, GotSearched, player_count, CurrentQueue = game_data
            return player_count
        else:
            return None
    
    def get_current_game_queue(self, game_key):
        game_data = self.get_game_data(game_key)
        if game_data is not None:
            game_key,game_state, GotKilled, GotHealed, GotSearched, player_count, CurrentQueue = game_data
            return CurrentQueue
        else:
            return 1
            
    def update_current_game_queue(self, game_key, player_count):

        limit = player_count+1
        current = self.get_current_game_queue(game_key)
        if current == limit:
            new = 1
        else:
            new = current+1

        self.cursor.execute('''
        UPDATE game SET CurrentQueue=? WHERE game_key=?
        ''', (new,game_key))
        self.connection.commit()

    def add_player(self, game_key, queue, role, suit, con1, con2, con3, is_gamer, name):
        con1_str = ','.join(con1)
        con2_str = ','.join(con2)
        con3_str = ','.join(con3)

        self.cursor.execute('''
        INSERT INTO player (game_key, queue, role, suit, con1, con2, con3, is_gamer, name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (game_key, queue, role, suit, con1_str, con2_str, con3_str, is_gamer, name))
        self.connection.commit()

    def get_player_con_by_queue(self, game_key, queue):
        player_data = self.get_player_data_by_queue(game_key, queue)
        if player_data is not None:
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            return con1, con2, con3
        else:
            return None, None, None
    
    def get_player_role_by_queue(self,game_key,queue):
        player_data = self.get_player_data_by_queue(game_key, queue)
        if player_data is not None:
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            return role
        else:
            return None
    
    def get_player_data_by_queue(self, game_key, queue):
        self.cursor.execute('''
        SELECT queue, role, suit, con1, con2, con3, is_gamer, name FROM player WHERE queue=? AND game_key=?
        ''', (queue,game_key))
        return self.cursor.fetchone()
    def get_player_data_by_name(self, game_key, name):
        self.cursor.execute('''
        SELECT queue, role, suit, con1, con2, con3, is_gamer, name FROM player WHERE name=? AND game_key=?
        ''', (name,game_key))
        return self.cursor.fetchone()
    
    def get_players_names(self, game_key, player_count):
        names = []
        for i in range(1, player_count+1):
            player_data = self.get_player_data_by_queue(game_key, i)
            if player_data is not None:
                queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            names.append(name)
        answ = ' '.join(names)
        return answ

    def get_gamer_data(self, game_key, is_gamer=True):
        self.cursor.execute('''
        SELECT queue, role, suit, con1, con2, con3, is_gamer, name FROM player WHERE game_key=? AND is_gamer=?
        ''', (game_key, is_gamer))
        return self.cursor.fetchone()
    
    def get_gamer_queue(self, game_key):
        player_data = self.get_gamer_data(game_key)
        if player_data is not None:
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
        return queue

    def get_gamer_summary(self, game_key):
        player_data = self.get_gamer_data(game_key)
        if player_data is not None:
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            avatar = None
            Color = None
            legend = None
            if role == "Мафия":
                avatar = "🤵🏻"
                color = "⚫"
                legend = "Вы - мафиози, ваша задача убить всех жителей деревни красных мастей, "\
                "старайтесь сохранить в тайне ваш ужасный секрет до конца игры, не раскрывайте роль и выбирайте цель с умом!"
            elif role == "Доктор":
                avatar = "👨🏻‍⚕‍"
                color = "🔴"
                legend = "Вы - доктор, ваша задача недопустить смертей мирных жителей вашей деревни, "\
                "вам неизвестны роли других жителей, старайтесь выбирать пациентов с умом "\
                "и устранить всю чернь на голосованиях, советую не раскрывать свою роль для других жителей чтобы не стать целью мафии"
            elif role == "Шериф":
                avatar = "🕵🏼‍♂️"
                color = "🔴"
                legend = "Вы - шериф, ваша задача любым способом вычислить, кто именно замышляет совершить страшное в деревне, "\
                "ночью вы собираете улики на жителей города и если житель был нечист - результат проверки покажет Черную масть, выбирайте цель с умом! "\
                "Советую не раскрывать свою личность для других жителей чтобы не стать целью мафии"
            else:
                avatar = "👨‍🌾"
                color = "🔴"
                legend = "Вы - обычный мирный житель, ваша задача ВЫЖИТЬ, совместными усилиями, "\
                "постарайтесь определить чернь в деревне на собрании и казнить невежду, выбирайте с умом, ведь могут пострадать невинные!"
            summary = f"Здравствуйте, {name}, сегодня утром над деревней повисли алые тучи, грядет страшное, "\
            f"вам предстоит пережить это несчастное время\n\n Роль – {role}{avatar}\n Масть – {suit}{color}\n\n{legend}\n"
            return summary
        else:
            return "⚠️ Ошибка генерации персонажа! Повторите попытку генерации"
    def clear_conversations_by_queue(self,game_key, queue):
        # Получаем беседы и обрабатываем случаи, когда результат может быть None
        con1, con2, con3 = self.get_player_con_by_queue(game_key, queue)

        # Очищаем беседы
        cleared_con = ''
        self.cursor.execute('''
        UPDATE player SET con1=?, con2=?, con3=? WHERE queue=?
        ''', (cleared_con, cleared_con, cleared_con, queue))
        self.connection.commit()

    def update_conversations_by_queue(self,game_key, queue, new_con1):
        con1, con2, con3 = self.get_player_con_by_queue(game_key,queue)
        self.cursor.execute('''
        UPDATE player SET con1=?, con2=?, con3=? WHERE queue=?
        ''', (new_con1, con1, con2, queue))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
    
    def save_last_messages(self, game_key, num_participants):
        # Получаем данные об участниках текущей сессии игры
        participants_data = []
        for i in range(1, num_participants + 1):
            player_data = self.get_player_data_by_queue(game_key,i)
            if player_data:
                participants_data.append(player_data)
    
        if participants_data:
            last_messages = ""
            # Формируем строку с последними тремя сообщениями каждого участника
            for player_data in participants_data:
                queue, role, suit, con1, con2, con3, is_gamer, name = player_data
                last_messages += f"Последнее, что говорил {name}:"
                if con1 or con2 or con3:
                    last_messages += f"\n- {con1}" if con1 else ""
                    last_messages += f"\n- {con2}" if con2 else ""
                    last_messages += f"\n- {con3}" if con3 else ""
                else:
                    last_messages += "\n- участник пока еще не высказывался"
                last_messages += "\n"
        
            # Возвращаем сформированную строку
            return last_messages
        else:
            return f"Участники с ключом игры {game_key} не найдены в базе данных."
        
    def doctor(self, game_key, healchoise):
        self.cursor.execute('''
                UPDATE game SET GotHealed=? WHERE game_key=?
                ''', (healchoise, game_key))
        self.connection.commit()
    
    def mafia(self, game_key, killchoise):
        killinfo = self.get_night_info(game_key)[0]
        killinfo +=f" {killchoise}"
        self.cursor.execute('''
                UPDATE game SET GotKilled=? WHERE game_key=?
                ''', (killinfo, game_key))
        self.connection.commit()
    
    def police(self, game_key, searchchoise):
        searchinfo = self.get_night_info(game_key)[2]
        searchinfo += f" {searchchoise}"
        self.cursor.execute('''
                UPDATE game SET GotSearched=? WHERE game_key=?
                ''', (searchinfo, game_key))
        self.connection.commit()
        player_data = self.get_player_data_by_name(game_key, searchchoise)
        if player_data is not None:
            queue, role, suit, con1, con2, con3, is_gamer, name = player_data
            return suit
        else:
        # Возвращаем None или другой подходящий для вашего случая результат
            return None


    