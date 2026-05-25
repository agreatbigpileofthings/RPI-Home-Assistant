import os

def speak(text):
    os.system(f'espeak-ng "{text}"')

speak("Welcome back Ryan")