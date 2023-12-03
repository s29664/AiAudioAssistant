import os
import json
import time
from queue import Queue
from threading import Thread

from Properties import Properties
from Recorder import Recorder
from Logger import Logger

import pygame
import openai
from vosk import Model, KaldiRecognizer
from gtts import gTTS

CONFIG_PATH = "./resources/config.ini"
conf = Properties(CONFIG_PATH)

openai.api_key = conf.API_TOKEN
logger = Logger(config=conf, printing=True)

execute = Queue(maxsize=1)
recordings = Queue(maxsize=2)
start_time = time.time()


def record_microphone():
    mic_reader = Recorder(conf)
    mic_reader.continuous_record_microphone(execute, recordings)


def hear_command():
    mic_reader = Recorder(conf)
    return mic_reader.record_microphone(conf.COMMAND_TIME_FRAME)


def play_audio(path):
    pygame.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()


def text_to_speech(command, language='en'):
    tts = gTTS(text=command, lang=language)
    try:
        tts.save(conf.TMP_AUDIO_PATH)
    except PermissionError as e:
        print(f"Could not save recording: {e}")
    play_audio(conf.TMP_AUDIO_PATH)
    os.remove(conf.TMP_AUDIO_PATH)


def ask_question_gpt_request(command_pl, command_en):
    response = openai.chat.completions.create(
        model=conf.MODEL,
        messages=[
            {"role": "system", "content": conf.SYSTEM_QUESTION_PROMPT},
            {"role": "user", "content": "Speech to Text with Polish model: " + command_pl},
            {"role": "user", "content": "Speech to Text with English model: " + command_en},
        ]
    )
    content = response.choices[0].message.content
    return content


def translate_gpt_request(command):
    response = openai.chat.completions.create(
        model=conf.MODEL,
        messages=[
            {"role": "system", "content": conf.SYSTEM_TRANSLATE_PROMPT},
            {"role": "user", "content": "Text to translate: " + command},
        ]
    )
    content = response.choices[0].message.content
    return content


def setup_audio_transcription_models():
    base_model_pl = Model(model_path=conf.POLISH_MODEL_PATH)
    base_model_en = Model(model_path=conf.ENGLISH_MODEL_PATH)

    model_pl = KaldiRecognizer(base_model_pl, conf.FRAME_RATE)
    model_en = KaldiRecognizer(base_model_en, conf.FRAME_RATE)

    model_pl.SetWords(True)
    model_en.SetWords(True)

    return model_pl, model_en


def get_transcription(model, frame):
    model.AcceptWaveform(b''.join(frame))
    result = model.Result()
    return json.loads(result)["text"]


def prepare_command(raw_text, activation):
    activation_size = len(activation)
    start_poz = raw_text.find(activation)
    command = raw_text[start_poz:start_poz + activation_size] if start_poz != -1 else None
    return command


def translation_process(model):
    recordings.get(), recordings.get()
    print(f"Translation needed!")
    play_audio(conf.ACTIVATE_SOUND_PATH)
    command = hear_command()
    play_audio(conf.RESPONSE_SOUND_PATH)

    text = get_transcription(model, command)

    if text:
        logger.log("translate", text)
        response = translate_gpt_request(text)
        logger.log("response", response)

        country_code, text = response[:2].lower(), response[3:]
        text_to_speech(command=text, language=country_code)
        play_audio(conf.RESPONSE_SOUND_PATH)


def question_process(model_pl, model_en):
    recordings.get(), recordings.get()
    print(f"Command heard!")
    play_audio(conf.ACTIVATE_SOUND_PATH)
    command = hear_command()
    play_audio(conf.RESPONSE_SOUND_PATH)

    text_pl = get_transcription(model_pl, command)
    text_en = get_transcription(model_en, command)

    if text_pl or text_en:
        logger.log("command_PL", text_pl)
        logger.log("command_EN", text_en)

        response = ask_question_gpt_request(text_pl, text_en)
        logger.log("response", response)

        country_code, text = response[:2].lower(), response[3:]
        text_to_speech(command=text, language=country_code)
        play_audio(conf.RESPONSE_SOUND_PATH)


def find_substring(text: str, substrings: list):
    for substring in substrings:
        if text.find(substring) != -1:
            return True
    return False


def speech_recognition():
    model_pl, model_en = setup_audio_transcription_models()
    while not execute.empty():
        frames = recordings.get()
        local_time = time.time()

        text_pl = get_transcription(model_pl, frames)
        text_en = get_transcription(model_en, frames)

        print(f"PL heard: {text_pl}")
        print(f"EN heard: {text_en}")

        if find_substring(text_pl, conf.PL_QUESTION_TRIGGERS):
            question_process(model_pl, model_en)

        elif find_substring(text_en, conf.EN_QUESTION_TRIGGERS):
            question_process(model_pl, model_en)

        elif find_substring(text_pl, conf.PL_TRANSLATION_TRIGGERS):
            translation_process(model_pl)

        elif find_substring(text_en, conf.EN_TRANSLATION_TRIGGERS):
            translation_process(model_en)
        print(f"Time: {time.time() - local_time:.2f} s\n")


""" START PROCESS """

execute.put(True)
logger.log("start", "Execution started")

try:
    listen = Thread(target=record_microphone)
    listen_with_offset = Thread(target=record_microphone)
    listen.start()
    time.sleep(conf.STAND_BY_TIME_FRAME / 2)
    listen_with_offset.start()
    transcribe = Thread(target=speech_recognition)
    transcribe.start()

except KeyboardInterrupt:
    logger.log("end", "Execution interrupted")
    raise
