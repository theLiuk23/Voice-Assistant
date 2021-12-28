import speech_recognition as sr
import pyttsx3
import commands
import string
import threading
import sys


# initializators
rec = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 210)
timer_thread = threading.Thread(target=commands.Start().Main)


# variables
voices = engine.getProperty('voices')
assistant_name = 'computer'
commands_filename = 'commands.txt'
commands_list = []
questions_list = []


# adds all the elements of commands.txt in commands_list
def LoadCommandList():
    with open(commands_filename) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        for line in lines:
            if line.__contains__('-'):
                continue
            args = line.split('/')
            commands_list.append([args[0], args[1]])


def LoadQuestionsList():
    for doubles in range(len(commands_list)):
        for words in enumerate(commands_list[doubles]):
            for num in str(words[0]):
                if num == '0':
                    questions_list.append(words[int(num) - 1])



# prints avaible languages in the os
# index = 0
# for voice in voices:
#    print(f'index-> {index} -- {voice.name}')
#    index +=1


def Speak(text):
    engine.say(text)
    engine.runAndWait()
    return True


def SearchCommand(command):
    for question in questions_list:
        for word in command.split(' '):
            if word == question:
                return commands_list[questions_list.index(word)][1]
    return ''


# finds in the commands.txt the equivalent method
def RunCommand(command):
    filename = SearchCommand(command)
    # no match
    if filename == '':
        Speak('Non credo di aver capito bene.')
        return

    # converts string to method and runs it
    classe = getattr(commands, filename)()
    thread = threading.Thread(target=classe.Main, args=(command,))
    thread.run()
    filename = ''


# main method - listening and running RunCommand(command)
def Listening():
    print('Sono pronto per aiutarti!')
    timer_thread.run()
    while True:
        with sr.Microphone() as mic:
            try:
                rec.adjust_for_ambient_noise(mic)
                voice = rec.listen(mic)
                command = str(rec.recognize_google(voice, language='it-IT')).lower()
                if command.startswith(assistant_name):
                    command = command.replace(assistant_name + ' ', '')
                    command.translate(str.maketrans('', '', string.punctuation))
                    print(f'COMANDO: {command}')
                    RunCommand(command)

            except sr.UnknownValueError:
                pass
            except KeyboardInterrupt:
                print('Interrupted manually')
                sys.exit(0)



if __name__ == "__main__":
    LoadCommandList()
    LoadQuestionsList()
    Listening()