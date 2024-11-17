import asyncio
import random
from googletrans import Translator
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from gtts import gTTS
import os
from config__lesson import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
translator = Translator()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")
    await message.answer("Могу выполнять команды, которые перечислены в /help.")


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("Бот может сохранять на диске сброшенное в чат изображение.")
    await message.answer("/echo Бот может повторять сброшенное после команды в чат сообщение.")
    await message.answer("/text_to_voice Бот возвращает сброшенный в чат после команды текст в виде сообщения.")
    await message.answer("/translate Бот переводит сброшенное после команды в чат сообщение.")


# Убедимся, что папка img существует:
if not os.path.exists('img'):
    os.makedirs('img')


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    # Получаем информацию о фотографии
    photo = message.photo[-1]  # Берем самое большое изображение
    file_id = photo.file_id
    file = await bot.get_file(file_id)

    # Загружаем файл на локальный диск
    await bot.download_file(file.file_path, f'img/{file.file_path.split("/")[-1]}')

    await message.answer("Изображение успешно сохранено!")


@dp.message(Command("echo")) #Эхо бот
async def echo_message(message: types.Message):
    # Получаем текст после команды /echo
    user_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not user_text:
        await message.reply("Пожалуйста, укажите текст после команды /echo.")
    else:
        # Отправляем обратно текст пользователя
        await message.reply(user_text)



@dp.message(Command("text_to_voice"))
async def text_to_voice(message: types.Message):
    # Получаем текст после команды /text_to_voice
    text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not text:
        await message.reply("Пожалуйста, укажите текст после команды /text_to_voice, который нужно озвучить.")
        return

    try:
        # Генерация речи с помощью gTTS
        tts = gTTS(text=text, lang='ru')  # Укажите 'ru' для русского языка
        audio_file = "voice_message.mp3"
        tts.save(audio_file)

        # Отправка аудиофайла пользователю
        voice = FSInputFile(audio_file)
        await message.answer_audio(voice)

        # Удаление временного файла
        os.remove(audio_file)
    except Exception as e:
        await message.reply("Произошла ошибка при обработке текста в голос. Попробуйте ещё раз.")
        print(f"Ошибка: {e}")


# Обработчик команды /translate
@dp.message(Command("translate"))
async def translate_command(message: types.Message):
    # Извлекаем текст после команды /translate
    text_to_translate = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not text_to_translate:
        await message.reply("Пожалуйста, укажите текст после команды /translate для перевода на английский.")
        return

    try:
        # Перевод текста на английский язык
        translated_text = translator.translate(text_to_translate, src='auto', dest='en').text
        await message.reply(f"Перевод на английский:\n{translated_text}")
    except Exception as e:
        await message.reply("Произошла ошибка при переводе текста. Попробуйте позже.")
        print(f"Ошибка перевода: {e}")

# Обработчик для всех сообщений
@dp.message()
async def echo_message(message: Message):
    if message.text.lower() == 'test':
        await message.answer('Пока тестируем данную команду')
    else:
        await message.send_copy(chat_id=message.chat.id)



# Обработчик ошибок
@dp.errors()
async def error_handler(event: types.ErrorEvent):
    print(f"An error occurred: {event.exception}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())