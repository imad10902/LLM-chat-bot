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