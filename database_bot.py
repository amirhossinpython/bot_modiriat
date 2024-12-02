import sqlite3
def init_db():
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_settings (
        id INTEGER PRIMARY KEY,
        learning_enabled BOOLEAN DEFAULT 1
    )
    ''')
    cursor.execute('INSERT OR IGNORE INTO bot_settings (id, learning_enabled) VALUES (1, 1)')
    connection.commit()
    connection.close()

def save_question_answer(question, answer):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    try:
        cursor.execute('INSERT OR REPLACE INTO knowledge_base (question, answer) VALUES (?, ?)', (question, answer))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        connection.close()

def get_answer(question):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('SELECT answer FROM knowledge_base WHERE question = ?', (question,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None

def is_learning_enabled():
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('SELECT learning_enabled FROM bot_settings WHERE id = 1')
    result = cursor.fetchone()
    connection.close()
    return result[0] == 1 if result else True

def set_learning_enabled(state: bool):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE bot_settings SET learning_enabled = ? WHERE id = 1', (1 if state else 0,))
    connection.commit()
    connection.close()

def get_all_questions_answers():
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('SELECT question, answer FROM knowledge_base')
    results = cursor.fetchall()
    connection.close()
    return results

def clear_knowledge_base():
    """پاک‌سازی کل اطلاعات جدول knowledge_base"""
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM knowledge_base')
    connection.commit()
    connection.close()

# مقداردهی اولیه دیتابیس
init_db()
