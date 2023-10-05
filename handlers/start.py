from aiogram import types, Dispatcher

from create import bot


async def start(msg: types.Message):
    await msg.bot.set_my_commands([
        types.BotCommand('start', 'Запуск бота'),
        types.BotCommand('help', 'Обучение и ссылки'),
        types.BotCommand('profile', 'Ваш профиль'),
        types.BotCommand('admin', 'Управление ботом')])
    text = '''
    Привет! Вы можете прислать мне интересный инфоповод/инсайд или просто арт, сгенерированный нейросетью. 

В общем все, что может, на ваш взгляд, быть нам интересно. Мы все прочитаем и опубликуем 😎
    '''
    await bot.send_message(msg.from_user.id, text, parse_mode='html')


async def help(msg: types.Message):
    text = '''
    <b>Не знаешь, что делать?</b>
    
Ты можешь отправить нам любой материал, который посчитаешь нужным, в формате: <b>Ссылка/Фото или видео/Документ</b>.
Другие форматы я не смогу прочитать 😓
    '''
    await bot.send_message(msg.from_user.id, text, parse_mode='html')


def reg_start(dp: Dispatcher):
    dp.register_message_handler(start, commands='start')
    dp.register_message_handler(help, commands='help')
