import configparser
import os


def split_to_list(text, sep=','):
    result = text.split(sep)
    if '' in result:
        result.remove('')
    return result


class Properties:

    def __init__(self, config_path):
        self.config = configparser.ConfigParser()

        with open(config_path, 'r', encoding='utf-8') as file:
            self.config.read_file(file)

    """ TRIGGERS """

    @property
    def PL_QUESTION_TRIGGERS(self):
        return split_to_list(self.config['TRIGGERS'].get('pl_question'))

    @property
    def EN_QUESTION_TRIGGERS(self):
        return split_to_list(self.config['TRIGGERS'].get('en_question'))

    @property
    def PL_TRANSLATION_TRIGGERS(self):
        return split_to_list(self.config['TRIGGERS'].get('pl_translation'))

    @property
    def EN_TRANSLATION_TRIGGERS(self):
        return split_to_list(self.config['TRIGGERS'].get('en_translation'))

    """ MODELS """

    @property
    def POLISH_MODEL_PATH(self):
        return os.path.dirname(__file__) + "\\resources\\models\\" + self.config['MODELS'].get('pl_model')

    @property
    def ENGLISH_MODEL_PATH(self):
        return os.path.dirname(__file__) + "\\resources\\models\\" + self.config['MODELS'].get('eng_model')

    @property
    def SYSTEM_QUESTION_PROMPT(self):
        path = os.path.dirname(__file__) + self.config['MODELS'].get('system_question_prompt_path')
        with open(path, 'r', encoding='utf-8') as file:
            prompt = file.read().replace('\n', ' ')
        return prompt

    @property
    def SYSTEM_TRANSLATE_PROMPT(self):
        path = os.path.dirname(__file__) + self.config['MODELS'].get('system_translate_prompt_path')
        with open(path, 'r', encoding='utf-8') as file:
            prompt = file.read().replace('\n', ' ')
        return prompt

    """ AUDIO """

    @property
    def STAND_BY_TIME_FRAME(self):
        return int(self.config['AUDIO'].get('record_seconds'))

    @property
    def COMMAND_TIME_FRAME(self):
        return int(self.config['AUDIO'].get('record_seconds_command'))

    @property
    def TMP_AUDIO_PATH(self):
        return os.path.dirname(__file__) + self.config['AUDIO'].get('tmp_speach')

    @property
    def ACTIVATE_SOUND_PATH(self):
        return os.path.dirname(__file__) + self.config['AUDIO'].get('activate_sound')

    @property
    def RESPONSE_SOUND_PATH(self):
        return os.path.dirname(__file__) + self.config['AUDIO'].get('response_sound')


    """ RECORDING """

    @property
    def CHANNELS(self):
        return int(self.config['RECORDING'].get('channels'))

    @property
    def FRAME_RATE(self):
        return int(self.config['RECORDING'].get('frame_rate'))

    @property
    def SAMPLE_SIZE(self):
        return int(self.config['RECORDING'].get('sample_size'))

    @property
    def CHUNK(self):
        return int(self.config['RECORDING'].get('chunk'))

    """ DATABASE """

    @property
    def LOG_TO_DATABASE(self):
        ignore_database = self.config['POSTGRES'].get('ignore_database')
        return ignore_database.lower() not in ('y', 'yes', 'true')

    @property
    def DATABASE(self):
        return self.config['POSTGRES'].get('database')

    @property
    def USER(self):
        return self.config['POSTGRES'].get('user')

    @property
    def PASSWORD(self):
        return self.config['POSTGRES'].get('password')

    @property
    def PORT(self):
        return self.config['POSTGRES'].get('port')

    @property
    def HOST(self):
        return self.config['POSTGRES'].get('host')

    @property
    def LOG_TABLE_NAME(self):
        return self.config['POSTGRES'].get('log_table')

    """ OPENAI """

    @property
    def API_TOKEN(self):
        return self.config['OPENAI'].get('api_key')

    @property
    def MODEL(self):
        return self.config['OPENAI'].get('model')
