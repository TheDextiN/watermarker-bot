import os
import telebot
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
import datetime
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('tg_token')

# Создайте директорию для временных файлов, если ее нет.
TEMP_PATH = 'temp/'
os.makedirs(TEMP_PATH, exist_ok=True)

# Инициализируем бота
bot = telebot.TeleBot(token)

# Функция для определения размеров текста
def get_text_size(text, font):
    draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    return draw.textsize(text, font)

# Функция для обработки фотографий и добавления водяного знака.
def process_photo(photo_file):
    # Загрузка фотографии.
    photo = Image.open(photo_file)

    # Добавление водяного знака.
    draw = ImageDraw.Draw(photo)
    font = ImageFont.load_default()
    watermark_text = "@melisad_sosedi"

    # Определение размеров текста без textsize
    text_width = len(watermark_text) * 8  # Подберите подходящее значение
    text_height = 12  # Подберите подходящее значение

    watermark_position = (photo.width - text_width, photo.height - text_height)
    draw.text(watermark_position, watermark_text, fill=(255, 255, 255, 64), font=font)

    # Сохранение обработанной фотографии.
    processed_file = TEMP_PATH + 'processed_photo.jpg'
    photo.save(processed_file)
    return processed_file

# Функция для обработки видео и добавления водяного знака.
def process_video(video_file):
    # Загрузка видео.
    video = VideoFileClip(video_file)

    # Добавление водяного знака.
    watermark_text = "@melisad_sosedi"
    watermarked_video = video.set_duration(video.duration)
    watermarked_video = watermarked_video.set_position(("right", "bottom"))

    # Сохранение обработанного видео.
    processed_file = TEMP_PATH + 'processed_video.mp4'
    watermarked_video.write_videofile(processed_file, codec="libx264")
    return processed_file

# Функция для обработки сообщений с медиафайлами.
@bot.message_handler(content_types=['photo', 'video'])
def process_media(message):
    if message.photo:
        # Если сообщение содержит фотографию.
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)
        with open(TEMP_PATH + 'photo.jpg', 'wb') as photo_file:
            photo_file.write(file)
        processed_file = process_photo(TEMP_PATH + 'photo.jpg')
    elif message.video:
        # Если сообщение содержит видео.
        file_info = bot.get_file(message.video.file_id)
        file = bot.download_file(file_info.file_path)
        with open(TEMP_PATH + 'video.mp4', 'wb') as video_file:
            video_file.write(file)
        processed_file = process_video(TEMP_PATH + 'video.mp4')

    # Отправляем обработанный медиафайл и текст в ответе.
    with open(processed_file, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

if __name__ == '__main__':
    bot.polling(none_stop=True)
