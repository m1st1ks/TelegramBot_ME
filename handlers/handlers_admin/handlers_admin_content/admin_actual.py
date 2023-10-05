from mysql.connector import connect, Error
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from math import ceil

from create import bot
from config import host, user, password, db_name


def create_buttons(data, page, last_page):
    buttons = []
    print(page, last_page)
    if len(data) <= 10:
        if len(data) % 2 == 0:
            for i in range(0, len(data), 2):
                buttons.append([types.InlineKeyboardButton(f'{data[i][0]} №{data[i][1]}',
                                                           callback_data=f'admin-content-actual-trigger {data[i][1]}'),
                                types.InlineKeyboardButton(f'{data[i + 1][0]} №{data[i + 1][1]}',
                                                           callback_data=f'admin-content-actual-trigger {data[i + 1][1]}')])
        else:
            for i in range(0, len(data) - 1, 2):
                buttons.append([types.InlineKeyboardButton(f'{data[i][0]} №{data[i][1]}',
                                                           callback_data=f'admin-content-actual-trigger {data[i][1]}'),
                                types.InlineKeyboardButton(f'{data[i + 1][0]} №{data[i + 1][1]}',
                                                           callback_data=f'admin-content-actual-trigger {data[i + 1][1]}')])
            buttons.append([types.InlineKeyboardButton(f'{data[-1][0]} №{data[-1][1]}',
                                                       callback_data=f'admin-content-actual-trigger {data[-1][1]}')])
    elif len(data) > 10:
        for i in range(0, 10, 2):
            buttons.append([types.InlineKeyboardButton(f'{data[i][0]} №{data[i][1]}',
                                                       callback_data=f'admin-content-actual-trigger {data[i][1]}'),
                            types.InlineKeyboardButton(f'{data[i + 1][0]} №{data[i + 1][1]}',
                                                       callback_data=f'admin-content-actual-trigger {data[i + 1][1]}')])
    if (page == 0 and last_page == -1) or (page == last_page == 0):
        pass
    elif page == 0 and page < last_page:
        buttons.append(
            [types.InlineKeyboardButton(f'➡️', callback_data=f'admin-content-actual-page-next {page} {last_page}')])
    elif page == last_page:
        buttons.append(
            [types.InlineKeyboardButton(f'⬅️️', callback_data=f'admin-content-actual-page-back {page} {last_page}')])
    else:
        buttons.append(
            [types.InlineKeyboardButton(f'⬅️️', callback_data=f'admin-content-actual-page-back {page} {last_page}'),
             types.InlineKeyboardButton(f'➡️', callback_data=f'admin-content-actual-page-next {page} {last_page}')])
    buttons.append([types.InlineKeyboardButton('🔙 Назад', callback_data="admin-content"),
                    types.InlineKeyboardButton('📋 Меню', callback_data="admin")])
    return buttons


async def actual(cb: types.CallbackQuery):
    await cb.answer()
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
            SELECT type, id FROM users WHERE download_date='Не скачивалось админом';
            """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                connection.commit()
        buttons = create_buttons(data, 0, ceil(len(data) / 10) - 1)
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await cb.message.edit_text('Актуальный материал:\n'
                                   f'Страница {1}/{ceil(len(data) / 10)}', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


async def next_page(cb: types.CallbackQuery):
    await cb.answer()
    page = int(cb.data.split()[1]) + 1
    last_page = int(cb.data.split()[2])
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
                SELECT type, id FROM users WHERE download_date='Не скачивалось админом' AND id>{page * 10} AND id<={page * 10 + 11};
                """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                connection.commit()
        buttons = create_buttons(data, page, last_page)
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await cb.message.edit_text('Актуальный материал:\n'
                                   f'Страница {page + 1}/{last_page + 1}', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


async def back_page(cb: types.CallbackQuery):
    await cb.answer()
    page = int(cb.data.split()[1]) - 1
    last_page = int(cb.data.split()[2])
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            table_query = f"""
                SELECT type, id FROM users WHERE download_date='Не скачивалось админом' AND id>{page * 10} AND id<={page * 10 + 11};
                """
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                data = []
                for line in cursor.fetchall():
                    data.append(line)
                connection.commit()
        buttons = create_buttons(data, page, last_page)
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await cb.message.edit_text('Актуальный материал:\n'
                                   f'Страница {page + 1}/{last_page + 1}', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором бота!')


def reg_admin_actual(dp: Dispatcher):
    dp.register_callback_query_handler(actual, text='admin-content-actual')
    dp.register_callback_query_handler(next_page, Text(startswith='admin-content-actual-page-next'))
    dp.register_callback_query_handler(back_page, Text(startswith='admin-content-actual-page-back'))
