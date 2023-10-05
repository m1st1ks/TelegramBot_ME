import datetime
import os.path
from random import randint

import validators
from aiogram import types, Dispatcher
from mysql.connector import connect, Error

from config import host, user, password, db_name
from create import bot


def generate(expansion):
    number = randint(100_000_000, 999_999_999)
    if not os.path.exists(f'cache/{number}.{expansion}'):
        return f'cache/{number}.{expansion}'
    else:
        generate(expansion)


async def download_for_users(user_id, user_name, types, url, status, upload_date, download_date, msg: types.Message):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as connection:
            insert_table_query = f"""
            INSERT INTO users VALUES(NULL, {user_id}, '{user_name}', '{types}', '{url}', '{status}', '{upload_date}', 
            '{download_date}');
            """
            with connection.cursor() as cursor:
                cursor.execute(insert_table_query)
                connection.commit()
    except Error as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Упс! Произошел при подключении к серверу... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def download_file(msg: types.Message, message):
    try:
        file_id = msg.document.file_id
        file = await bot.get_file(file_id)
        file_name = generate('png')
        await bot.download_file(file.file_path, file_name)
        await download_for_users(msg.from_user.id, f'@{msg.from_user.username}', 'File', file_name,
                                 'Не сохранен', datetime.datetime.now(), 'Не скачивалось админом', msg)
        await bot.edit_message_text(chat_id=msg.chat.id, message_id=message.message_id, text='Файл успешно скачен! ✅')
    except:
        await bot.send_message(msg.from_user.id, 'Упс! Произошел сбой на нашей стороне... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def download_photo(msg: types.Message, message):
    try:
        file_id = msg.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_name = generate('jpeg')
        await bot.download_file(file.file_path, file_name)
        await download_for_users(msg.from_user.id, f'@{msg.from_user.username}', 'Photo', file_name,
                                 'Не сохранен', datetime.datetime.now(), 'Не скачивалось админом', msg)
        await bot.edit_message_text(chat_id=msg.chat.id, message_id=message.message_id, text='Фото успешно скачено! ✅')
    except:
        await bot.send_message(msg.from_user.id, 'Упс! Произошел сбой при скачивании... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def download_video(msg: types.Message, message):
    try:
        file_id = msg.video.file_id
        file = await bot.get_file(file_id)
        file_name = generate('mp4')
        await bot.download_file(file.file_path, file_name)
        await download_for_users(msg.from_user.id, f'@{msg.from_user.username}', 'Video', file_name,
                                 'Не сохранен', datetime.datetime.now(), 'Не скачивалось админом', msg)
        await bot.edit_message_text(chat_id=msg.chat.id, message_id=message.message_id, text='Видео успешно скачено! ✅')
    except:
        await bot.send_message(msg.from_user.id, 'Упс! Произошел сбой при скачивании... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def url(msg: types.Message):
    try:
        await download_for_users(msg.from_user.id, f'@{msg.from_user.username}', 'Url', msg.text,
                                 'Не сохранен', datetime.datetime.now(), 'Не скачивалось админом', msg)
        await bot.send_message(msg.from_user.id, 'Cсылка успешно сохранена! ✅')
    except:
        await bot.send_message(msg.from_user.id, 'Упс! Произошел сбой при сохранении... 🙊 \n'
                                                 'Повторите попытку или свяжитесь с администратором @artem_lyashenka')


async def downloads(msg: types.Message):
    status = msg.media_group_id
    if status is None:
        if msg.photo:
            message = await bot.send_message(msg.from_user.id, 'Ждите, фото скачивается...')
            await download_photo(msg, message)
        elif msg.video:
            message = await bot.send_message(msg.from_user.id, 'Ждите, видео скачивается...')
            await download_video(msg, message)
        elif msg.document:
            message = await bot.send_message(msg.from_user.id, 'Ждите, файл скачивается...')
            await download_file(msg, message)
        elif validators.url(msg.text):
            await url(msg)
        else:
            await bot.send_message(msg.from_user.id, 'Ошибка... ❌')
            await bot.send_message(msg.from_user.id, 'Неизвестный формат материала!\n'
                                                     'Вы можете прислать <b>ТОЛЬКО</b> ссылку, фото или видео, документ',
                                   parse_mode='html')
    else:
        message = await bot.send_message(msg.from_user.id, 'Ждите, материал скачивается...')
        if msg.photo:
            await download_photo(msg, message)
        elif msg.video:
            await download_video(msg, message)
        elif msg.document:
            await download_file(msg, message)
        else:
            await bot.send_message(msg.from_user.id, 'Ошибка... ❌')
            await bot.send_message(msg.from_user.id, 'Неизвестный формат материала!\n'
                                                     'Вы можете прислать <b>ТОЛЬКО</b> ссылку, фото или видео, документ',
                                   parse_mode='html')


def reg_downloads(dp: Dispatcher):
    dp.register_message_handler(downloads, content_types=types.ContentTypes.ANY)
