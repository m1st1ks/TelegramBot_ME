from mysql.connector import connect, Error
from aiogram import types, Dispatcher

from create import bot
from config import host, user, password, db_name


async def admin_content(cb: types.CallbackQuery):
    await cb.answer()
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Актуальный материал', callback_data="admin-content-actual")
    button2 = types.InlineKeyboardButton('История скачиваний', callback_data="admin-content-history")
    button3 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin")
    markup.add(button1, button2, button3)
    await cb.message.edit_text('🗂 Контент', reply_markup=markup)


async def history(cb: types.CallbackQuery):
    await cb.answer()
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            select_table_query = f"""
            SELECT * FROM users WHERE download_date!='Не скачивалось админом';
            """
            text = 'История скачиваний: \n\n'
            table_query = f"""
                        SELECT admin_id, role FROM admins;
                        """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                    if cb.from_user.id == line[0] and (line[1] == 'Admin' or line[1] == 'Creator'):
                        cursor.execute(select_table_query)
                        for ln in cursor.fetchall():
                            text += f'<b>Порядковый номер:</b> {ln[0]}\n' \
                                    f'<b>Type:</b> {ln[3]}\n' \
                                    f'<b>Загрузил: </b> {ln[2]}\n' \
                                    f'<b>Id:</b> {ln[1]}\n' \
                                    f'<b>Дата загрузки:</b> {ln[5]}\n' \
                                    f'<b>Status:</b> {ln[4]}\n' \
                                    f'<b>Дата скачивания:</b> {ln[6]}\n\n'
                        buttons = [types.InlineKeyboardButton('🗑 Очистить историю', callback_data="admin-content-history-test_clear")], \
                                  [types.InlineKeyboardButton('🔙 Назад', callback_data="admin-content"),
                                   types.InlineKeyboardButton('📋 Меню', callback_data="admin")]
                        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
                        await cb.message.edit_text(text, parse_mode='html', reply_markup=markup)
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


async def test_clear(cb: types.CallbackQuery):
    await cb.answer()
    buttons = [types.InlineKeyboardButton('Да, это так', callback_data="admin-content-history-test_clear-clear")], \
              [types.InlineKeyboardButton('Нет', callback_data="admin-content")], \
              [types.InlineKeyboardButton('🔙 Назад', callback_data="admin-content"),
               types.InlineKeyboardButton('📋 Меню', callback_data="admin")]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await cb.message.edit_text('Вы собираетесь очистить историю скачиваний. Это так?', reply_markup=markup)


async def clear(cb: types.CallbackQuery):
    await cb.answer()
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
            DELETE FROM users WHERE download_date!='Не скачивалось админом';
            """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                connection.commit()
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('👨‍💻 Список админов', callback_data="admin-admin_list")
        button2 = types.InlineKeyboardButton('🗂 Контент', callback_data="admin-content")
        markup.add(button1, button2)
        await cb.message.edit_text('История сохранений очищена!', parse_mode='html', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


def reg_admin_content(dp: Dispatcher):
    dp.register_callback_query_handler(admin_content, text='admin-content')
    dp.register_callback_query_handler(history, text='admin-content-history')
    dp.register_callback_query_handler(test_clear, text='admin-content-history-test_clear')
    dp.register_callback_query_handler(clear, text='admin-content-history-test_clear-clear')
