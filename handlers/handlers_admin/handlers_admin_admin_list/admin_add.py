from os import remove
from mysql.connector import connect, Error
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from create import bot
from config import host, user, password, db_name, creator_id, admin_id


class AdminAddFSM(StatesGroup):
    join_id = State()
    join_username = State()
    join_role = State()


async def add_to_db(admin_id, admin_username, role, msg: types.Message):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            insert_table_query = f"""
            INSERT INTO admins VALUES(NULL, {admin_id}, '{admin_username}', '{role}');
            """
            with connection.cursor() as cursor:
                cursor.execute(insert_table_query)
                connection.commit()
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('👨‍💻 Список админов', callback_data="admin-admin_list")
        button2 = types.InlineKeyboardButton('🗂 Контент', callback_data="admin-content")
        markup.add(button1, button2)
        await bot.send_message(msg.from_user.id, f'{role} {admin_username} добавлен!', reply_markup=markup)
    except Error as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                 'Cвяжитесь с администратором @artem_lyashenka')


async def add(cb: types.CallbackQuery):
    await AdminAddFSM.join_id.set()
    await cb.answer()
    await cb.message.edit_text('Введите id пользователя(он доступен в профиле):')


async def join_id(msg: types.Message):
    await AdminAddFSM.next()
    text = msg.text
    if text == str(creator_id) or text == str(admin_id):
        text = '000000000'
    with open(f'cache/{msg.from_user.id}_add.txt', 'a', encoding='utf-8') as f:
        f.write(f'{text}\n')
    await bot.send_message(msg.from_user.id, 'Введите username админа.\n'
                                             'Пример: @artem_lyashenka')


async def join_username(msg: types.Message):
    await AdminAddFSM.next()
    text = msg.text
    with open(f'cache/{msg.from_user.id}_add.txt', 'a', encoding='utf-8') as f:
        f.write(f'{text}\n')
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton('Moderator')
    button2 = types.KeyboardButton('Admin')
    markup.add(button1, button2)
    await bot.send_message(msg.from_user.id, 'Выберите роль пользователя: \n\n'
                                             '<b>Moderator</b> - Модератор. Может скачивать фотографии.\n\n'
                                             '<b>Admin</b> - Админ. Может скачивать фотографии, изменять список '
                                             'админов.\n\n'
                                             '<b>Creator</b> - Создатель. Имеет полную власть над ботом и исходный код).',
                           parse_mode='html',
                           reply_markup=markup)


async def join_role(msg: types.Message, state: FSMContext):
    await state.finish()
    text = msg.text
    with open(f'cache/{msg.from_user.id}_add.txt', 'a', encoding='utf-8') as f:
        f.write(f'{text}\n')
    with open(f'cache/{msg.from_user.id}_add.txt', 'r') as f:
        data = []
        for line in f:
            data.append(line[:-1])
    remove(f'cache/{msg.from_user.id}_add.txt')
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(msg.from_user.id, 'Готово! ✅', reply_markup=markup)
    await add_to_db(int(data[0]), data[1], data[2], msg)


def reg_admin_add(dp: Dispatcher):
    dp.register_callback_query_handler(add, text='admin-admin_list-change_list-add')

    dp.register_message_handler(join_id, state=AdminAddFSM.join_id)
    dp.register_message_handler(join_username, state=AdminAddFSM.join_username)
    dp.register_message_handler(join_role, state=AdminAddFSM.join_role)
