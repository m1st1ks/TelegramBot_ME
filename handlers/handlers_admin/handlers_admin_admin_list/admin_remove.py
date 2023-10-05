from mysql.connector import connect, Error
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from create import bot
from config import host, user, password, db_name


class AdminRemoveFSM(StatesGroup):
    join_id = State()


async def remove_to_db(id, msg: types.Message):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            remove_table_query = f'''
            DELETE FROM admins WHERE id={id} AND role!='Creator'
            '''
            table_query = f"""
                        SELECT * FROM admins;
                        """
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton('🔙 Назад', callback_data="admin-admin_list")
            button2 = types.InlineKeyboardButton('📋 Меню', callback_data="admin")
            markup.add(button1, button2)
            with connection.cursor() as cursor:
                cursor.execute(table_query)
                for line in cursor.fetchall():
                    if id == line[0]:
                        await bot.send_message(msg.from_user.id, f'{line[3]} {line[2]} удален!', reply_markup=markup)
                        break
                cursor.execute(remove_table_query)
                connection.commit()
    except Error as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                 'Cвяжитесь с администратором @artem_lyashenka')


async def remove(cb: types.CallbackQuery):
    await AdminRemoveFSM.join_id.set()
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
        await cb.message.edit_text(text, parse_mode='html')
    except Error as e:
        print(e)
        await bot.send_message(cb.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                'Повторите попытку или свяжитесь с администратором @artem_lyashenka')

    await bot.send_message(cb.from_user.id, 'Введите порядковый номер админа:\n'
                                            'Введите 0, если не хотите никого удалять')


async def join_id(msg: types.Message, state: FSMContext):
    await state.finish()
    text = msg.text
    await bot.send_message(msg.from_user.id, 'Готово! ✅')
    await remove_to_db(int(text), msg)


def reg_admin_remove(dp: Dispatcher):
    dp.register_callback_query_handler(remove, text='admin-admin_list-change_list-remove')

    dp.register_message_handler(join_id, state=AdminRemoveFSM.join_id)
