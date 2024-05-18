import sqlite3 as sq

url = 'http://proxy.server:3128'
def db_connect():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS money(money_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "date DATETIME, "
                "money_up TEXT, "
                "money_name_up TEXT, "
                "money_down TEXT,"
                "money_name_dw TEXT)")
    db.commit()


def create_new_mdw(user, date, money_down, money_name_dw):
    money_down = cur.execute(
        "INSERT INTO money(user_id, date, money_down, money_name_dw) VALUES (?, ?, ?, ?)",
        (user, date, money_down, money_name_dw))
    db.commit()
    return money_down


def create_new_mup(user_id, date, money_up, money_name_up):
    money_up = cur.execute(
        "INSERT INTO money(user_id, date, money_up, money_name_up) VALUES (?, ?, ?, ?)",
        (user_id, date, money_up, money_name_up))
    db.commit()
    return money_up


def get_user_id(user_id):
    result = cur.execute("SELECT distinct user_id from money")
    return result.fetchall()

#def get_user_id(user_id):
#    """Достаем id юзера в базе по его user_id"""
#    result = cur.execute("SELECT `id` FROM `money` WHERE `user_id` = ?", (user_id,))
#    return result.fetchone()[0]


def stat(user_id):
    """Получаем общую статистику"""
    db_res = cur.execute('''select sum(money_up), sum(money_down), sum(money_up) - sum(money_down)
                from money
                where user_id = ? ''',
                         (user_id,)).fetchone()

    result = f'''
Общая статистика
Доходы: {db_res[0]}
Расходы: {db_res[1]}
Текущий баланс: {db_res[2]}
'''

    """Получаем статистику по доходам"""
    db_res = cur.execute('''select money_name_up, sum(money_up)
                                        from money
                                        where money_name_up is not null
                                          and money_up > 0
                                          and user_id = ?
                                        group by 1
                                        order by 2 desc ''', (user_id,)).fetchall()

    res = '\n'.join(i[0] + ': ' + str(i[1]) for i in db_res)
    result = result + '\n\nСтатистика доходов\n' + res

    """Получаем статистику по расходам"""
    db_res = cur.execute('''select money_name_dw, sum(money_down)
                                        from money
                                        where money_name_dw is not null
                                          and money_name_dw > 0
                                          and user_id = ?
                                        group by 1
                                        order by 2 desc ''', (user_id,)).fetchall()

    res = '\n'.join(i[0] + ': ' + str(i[1]) for i in db_res)
    result = result + '\n\nСтатистика расходов\n' + res

    return result

def delete_records(user_id):
    del_res = cur.execute("""DELETE FROM money where user_id = ?""",(user_id,)).fetchall()
    db.commit()
    print("Запись успешно удалена")
    return del_res