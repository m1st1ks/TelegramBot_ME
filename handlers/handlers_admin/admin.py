from mysql.connector import connect, Error
from aiogram import types, Dispatcher

from create import bot
from config import host, user, password, db_name


async def authentication(msg: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('🔎 Проверка', callback_data="admin")
    markup.add(button1)
    await bot.send_message(msg.from_user.id, 'Нажмите на кнопку для аутентификации 👇', reply_markup=markup)


async def admin(cb: types.CallbackQuery):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
            SELECT * FROM admins;
            """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                    if cb.from_user.id == line[1]:
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        button1 = types.InlineKeyboardButton('👨‍💻 Список админов', callback_data="admin-admin_list")
                        button2 = types.InlineKeyboardButton('🗂 Контент', callback_data="admin-content")
                        markup.add(button1, button2)
                        await cb.message.edit_text(f'Приветствую, {line[2]}', reply_markup=markup)
                        break
                else:
                    await cb.message.edit_text(f'У вас нет прав администратора! 😕\n'
                                               f'Главное меню 👉 /start')
                connection.commit()
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


def reg_admin(dp: Dispatcher):
    dp.register_message_handler(authentication, commands='admin')
    dp.register_callback_query_handler(admin, text='admin')
