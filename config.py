# from dotenv import load_dotenv
# import os
# load_dotenv()



class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = "this-is-a-super-secret-key"
    OPENAI_KEY = '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'

config = {
    'LOCAL': DevelopmentConfig,
    'DEV': DevelopmentConfig,
    'PROD': DevelopmentConfig,
}