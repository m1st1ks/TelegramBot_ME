from mysql.connector import connect, Error
from aiogram import types, Dispatcher

from create import bot
from config import host, user, password, db_name


async def profile(msg: types.Message):
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
                text = ''
                for line in cursor.fetchall():
                    if msg.from_user.id == line[0]:
                        text += 'Ваш профиль:\n\n' \
                                f'<b>Id:</b> {msg.from_user.id}\n' \
                                f'<b>Username:</b> @{msg.from_user.username}\n' \
                                f'<b>Role:</b> {line[1]}'
                        break
                else:
                    text += 'Ваш профиль:\n\n' \
                            f'<b>Id:</b> {msg.from_user.id}\n' \
                            f'<b>Username:</b> @{msg.from_user.username}\n' \
                            f'<b>Role:</b> user'
                connection.commit()
        await bot.send_message(msg.from_user.id, text, parse_mode='html')
    except Error as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором бота!')


def reg_profile(dp: Dispatcher):
    dp.register_message_handler(profile, commands='profile')
