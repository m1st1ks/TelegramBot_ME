from mysql.connector import connect, Error
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile

import datetime
import os
from create import bot
from config import host, user, password, db_name


async def trigger(cb: types.CallbackQuery):
    await cb.answer()
    call = cb.data.split()[1]
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
                SELECT * FROM users WHERE id='{call}';
                """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = cursor.fetchall()
                connection.commit()
        text = f'<b>Порядковый номер:</b> {data[0][0]}\n' \
               f'<b>Type:</b> {data[0][3]}\n' \
               f'<b>Загрузил:</b> {data[0][2]}\n' \
               f'<b>Id:</b> {data[0][1]}\n' \
               f'<b>Дата загрузки:</b> {data[0][6]}\n' \
               f'<b>Status:</b> {data[0][5]}\n' \
               f'<b>Дата скачивания:</b> {data[0][7]}\n\n'

        buttons = [[types.InlineKeyboardButton(f'СКАЧАТЬ 📩', callback_data=f'trigger-download {data[0][0]}')],
                   [types.InlineKeyboardButton('🔙 Назад', callback_data="admin-content-actual"),
                    types.InlineKeyboardButton('📋 Меню', callback_data="admin")]]
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await cb.message.edit_text(f'{text}', parse_mode='html', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def change_data(id, user_id, admin_name, date):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
                UPDATE users SET url='Deleted', status='Сохранен @{admin_name}', download_date='{date}' WHERE id={id};
                """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                connection.commit()
    except Error as e:
        print(e)
        await bot.send_message(user_id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                        'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def download(cb: types.CallbackQuery):
    await cb.answer()
    call = cb.data.split()[1]
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
                SELECT type, url FROM users WHERE id='{call}';
                """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = cursor.fetchall()
                connection.commit()
            await cb.message.delete()
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin-content-actual")
            button2 = types.InlineKeyboardButton('📋 Меню', callback_data="admin")
            markup.add(button1, button2)
            if data[0][0] == 'Photo':
                await bot.send_photo(cb.from_user.id, photo=InputFile(f'{data[0][1]}'))
            elif data[0][0] == 'Video':
                await bot.send_video(cb.from_user.id, video=InputFile(f'{data[0][1]}'))
            elif data[0][0] == 'File':
                await bot.send_document(cb.from_user.id, document=InputFile(f'{data[0][1]}'))
            else:
                await bot.send_message(cb.from_user.id, f'{data[0][1]}')
            date = datetime.datetime.now()
            await bot.send_message(cb.from_user.id, f'Порядковый номер: {call}\n'
                                                    f'Status: Сохранен @{cb.from_user.username}\n'
                                                    f'Download_date: {date}', reply_markup=markup)
            await change_data(call, cb.from_user.id, cb.from_user.username, date)
            os.remove(f'{data[0][1]}')
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


def reg_admin_trigger(dp: Dispatcher):
    dp.register_callback_query_handler(trigger, Text(startswith='admin-content-actual-trigger'))
    dp.register_callback_query_handler(download, Text(startswith='trigger-download'))
