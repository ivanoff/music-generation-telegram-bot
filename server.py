import os
import telebot
import scipy
import subprocess
import logging
from datetime import datetime
from transformers import pipeline
from dotenv import load_dotenv

synthesiser = pipeline("text-to-audio", "facebook/musicgen-small")

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
FILES_DIRECTORY = './files'

log_filename = "server.log"

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me music prompt and I'll generate the sample")

@bot.message_handler(func=lambda message: True)
def send_file(message):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filenameWav = os.path.join(FILES_DIRECTORY, f"{timestamp}.wav")
    filename = os.path.join(FILES_DIRECTORY, f"{timestamp}.mp3")

    prompt = message.text.strip()

    filenamePrompt = os.path.join(FILES_DIRECTORY, os.path.normpath(prompt))
    if os.path.exists(filenamePrompt):
        with open(filenamePrompt, 'rb') as file:
            bot.send_document(message.chat.id, file)
    else:
        bot.reply_to(message, "Got it, starting to generate...")
        logging.info(f"{filename}: {prompt}")

        music = synthesiser(prompt, forward_params={"do_sample": True})
        scipy.io.wavfile.write(filenameWav, rate=music["sampling_rate"], data=music["audio"])
        subprocess.call(['ffmpeg', '-i', filenameWav, filename])
        os.remove(filenameWav)

        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, f"Файл {filename} не найден.")

bot.polling(none_stop=True)
