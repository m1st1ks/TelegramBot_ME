from mysql.connector import connect, Error
from aiogram import types, Dispatcher

from create import bot
from config import host, user, password, db_name


async def admin_list(cb: types.CallbackQuery):
    await cb.answer()
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Весь список', callback_data="admin-admin_list-full_list")
    button2 = types.InlineKeyboardButton('Изменить список', callback_data="admin-admin_list-change_list")
    button3 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin")
    markup.add(button1, button2, button3)
    await cb.message.edit_text('👨‍💻 Список админов', reply_markup=markup)


async def admin_list_full_list(cb: types.CallbackQuery):
    await cb.answer()
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
                text = 'Список админов: \n\n'
                for line in cursor.fetchall():
                    text += f'<b>Порядковый номер:</b> {line[0]}\n' \
                            f'<b>Id:</b> {line[1]}\n' \
                            f'<b>Username:</b> {line[2]}\n' \
                            f'<b>Role:</b> {line[3]}\n\n'
                connection.commit()
        markup = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin-admin_list")
        button2 = types.InlineKeyboardButton('📋 Меню', callback_data="admin")
        markup.add(button1, button2)
        await cb.message.edit_text(text, parse_mode='html', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


async def change_list(cb: types.CallbackQuery):
    await cb.answer()
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
            SELECT admin_id, role FROM admins;
            """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                    if cb.from_user.id == line[0] and (line[1] == 'Admin' or line[1] == 'Creator'):
                        buttons = [types.InlineKeyboardButton('➕ Добавить админа',
                                                              callback_data="admin-admin_list-change_list-add")], \
                                  [types.InlineKeyboardButton('❌ Удалить админа',
                                                              callback_data="admin-admin_list-change_list-remove")], \
                                  [types.InlineKeyboardButton('🔙 Назад', callback_data="admin-admin_list"),
                                   types.InlineKeyboardButton('📋Меню', callback_data="admin")]
                        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
                        await cb.message.edit_text('Изменить список:', reply_markup=markup)
                        break
                else:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    button1 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin-admin_list")
                    button2 = types.InlineKeyboardButton('📋 Меню', callback_data="admin")
                    markup.add(button1, button2)
                    await cb.message.edit_text(f'Модераторам сюда нельзя! 😕', reply_markup=markup)
                connection.commit()
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


def reg_admin_list(dp: Dispatcher):
    dp.register_callback_query_handler(admin_list, text='admin-admin_list')
    dp.register_callback_query_handler(admin_list_full_list, text='admin-admin_list-full_list')
    dp.register_callback_query_handler(change_list, text='admin-admin_list-change_list')
