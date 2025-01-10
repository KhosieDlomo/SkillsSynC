import pyrebase
import click
import os
from dotenv import load_dotenv

load_dotenv()

firebaseConfig = {

  'apiKey':os.getenv('API_KEY'),

  'authDomain':os.getenv('AUTHDOMAIN'),

  'projectId': os.getenv('PROJECTID'),

  'storageBucket':os.getenv('STORAGEBUCKET'),

  'messagingSenderId': os.getenv('MESSAGESENDERID'),

  'appId': os.getenv('APPID'),

  'measurementId': os.getenv('MEASUREMENTID') 

};
