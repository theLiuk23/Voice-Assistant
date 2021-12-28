import pyttsx3
import speech_recognition as sr
from spotipy.oauth2 import SpotifyClientCredentials
from pygooglenews import GoogleNews
from configparser import ConfigParser
from pathlib import Path
import threading
import playsound
import webbrowser
import datetime
import random
import pywhatkit
import spotipy
import time
import sys
import re


### classes called by the programme ###

class Start(object):
    def Main(self):
        timers = ReadTxt().get_timers()
        if len(timers) is not 0:
            time = timers[0][1]
            time = [int(time[0] + time[1]), int(time[2] + time[3])]
            memo = timers[1][1]
            day = timers[2][1]
            SetTask().start_timer(memo, time, day)


class Speak(object):
    def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


class SaveTxt(object):
    # variables
    music_platform = 'youtube'
    config = ConfigParser()

    def Main(self, partition, settings_list, new_value):
        if type(settings_list) is not list or type(new_value) is not list:
            raise NameError('Both settings and values need to be passed in a list.')
        if len(settings_list) is not len(new_value):
            raise Exception('There must be the same number of elements in "settings_list" and in "new_value"')

        self.config.read('config.ini')
        self.music_platform = self.config['settings']['music_platform']
        for i in range(len(settings_list)):
            self.config.set(partition, settings_list[i - 1], new_value[i - 1])
        self.save()
        
    def save(self):
        try:
            with open('config.ini', 'w') as file:
                self.config.write(file)
        except Exception as e:
            print(e)
            Speak.speak('Non sono riuscita a salvare le nuove impostazioni.')
            return

    def add_partition(self, partition):
        if type(partition) is not str:
            raise Exception('Partition must be a string.')
        self.config.read('config.ini')
        self.config.add_section(partition)
        self.save()


class DeleteTxt(object):
    config = ConfigParser()
    def content(self, partition, content):
        if type(content) is not str:
            raise Exception('Content must be a string.')
        self.config.read('config.ini')
        self.config.remove_option(partition, content)
        self.save()

    def save(self):
        try:
            with open('config.ini', 'w') as file:
                self.config.write(file)
        except Exception as e:
            print(e)
            Speak.speak('Non sono riuscita a salvare le nuove impostazioni.')
            return
        if self.config.has_section('timers') == False:
            self.config.add_section('timers')
            with open('config.ini', 'w') as file:
                self.config.write(file)

    def partition(self, partition):
        self.config.read('config.ini')
        success = self.config.remove_section(partition)
        self.save()


class ReadTxt(object):
    config = ConfigParser()

    def get_music_platform(self):
        self.config.read('config.ini')
        music_platform = self.config.get('settings', 'music_platform')
        return music_platform

    def get_assistant_name(self):
        self.config.read('config.ini')
        assistant_name = self.config.get('settings', 'assistant_name')
        return assistant_name

    def get_timers(self):
        timer = []
        self.config.read('config.ini')
        for item in self.config.items('timers'):
            timer.append([item[0], item[1]])
        return timer


### classes callable from the users ###


class SearchMusic(object):
    def Main(self, command):
        music_platform = ReadTxt().get_music_platform()
        song = command.replace('riproduci', '')
        song = command.replace('riproduci ', '')
        song = command.split('su')[0]
        platform = command.split('su')[1].strip()

        if song is '' or song is ' ':
            raise Exception(r'Non hai specificato cosa riprodurre.')
        if platform == 'youtube':
            pywhatkit.playonyt(song)
            return
        elif platform == 'spotify':
            self.run_spotify(song, music_platform)
            return
        else:
            if music_platform == 'youtube':
                pywhatkit.playonyt(song)
            elif music_platform == 'spotify':
                self.run_spotify(song, music_platform)
            else:
                Speak.speak(f'La piattaforma musicale {music_platform} non è supportata. Prova con youtube o spotify.')
        # finally
        Speak.speak(f'Riproduco su {music_platform}, {song}')

    def run_spotify(self, song, platform):
        try:
            client_id = '4dabb5933c0d49058846c549c6a703ba'
            client_secret = '2aaa36256ccb43b88523498815b2416d'
            spotifyObject = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))
        except:
            Speak.speak("C'è stato un problema durante l'accesso all'account di Spotify. Forse è un errore temporaneo.")
            return
        try:
            searchResults = spotifyObject.search(song, 1, 0, 'track')
            link = searchResults['tracks']['items'][0]['external_urls']['spotify']
            webbrowser.open(link, 0)
        except:
            Speak.speak(f'Non ho trovato nessuna canzone su {platform}, chiamata {song}')
            return


class Answers(object):
    def Main(self, command):
        
        if command.__contains__('ciao'):
            Speak.speak(f'Ciao, sono {ReadTxt.get_assistant_name()}, come posso aiutarti?')
        elif command.__contains__('come stai') or command.__contains__('bene'):
            Speak.speak('Sono carico, fino a quando non mi spegni.')
        elif command.__contains__('ore'):
            hour = str(datetime.datetime.now().hour)
            minute = str(datetime.datetime.now().minute)
            Speak.speak(f'Sono esattamente le {hour} e {minute}.')
        elif command.__contains__('v*********') or command.__contains__('inculo'):
            Speak.speak(f'Vacci tu brutto stronzo di merda!')


class ChangeMusicPlatform(object):
    def Main(self, command):
        
        music_platform = ReadTxt().get_music_platform()
        if music_platform is None:
            raise ValueError('"Music platform" can\'t be None.')

        if command.__contains__('youtube'):
            music_platform = 'youtube'
        elif command.__contains__('spotify'):
            music_platform = 'spotify'

        Speak.speak(f'Ho cambiato la piattaforma musicale predefinita in {music_platform}.')
        SaveTxt().Main('settings', ["music_platform"], [music_platform])


class ReadNews(object):
    fonte = 'Google News'

    def get_num(self, command):
        numbers = {'prima':1, 'uno':1, 'un': 1, 'due': 2, 'tre':3, 'quattro':4, 'cinque':5, 'sei':6, 'sette':7, 'otto':8, 'nove':9, 'dieci':10}
        for word in command.split(' '):
            if numbers.__contains__(word):
                return numbers[word]
        try:
            return int(re.search(r'\d+', command).group())
        except:
            return 5

    def Main(self, command):
        num = self.get_num(command)
        index = 1
        if num == 1:
            Speak.speak(f'Ecco la prima notizia da {self.fonte}')
        else:
            Speak.speak(f'Ecco le prime {num} notizie da {self.fonte}')
        gn = GoogleNews(lang='it', country='IT')
        top = gn.top_news()
        for item in top['entries'][:num]:
            title = item['title'].split('-')[0] #removes the source from the end of the string
            Speak.speak(f'{index}, {title}')
            time.sleep(0.5)
            index = index + 1


class SetTask(object):
    orario = None
    memo = None
    timer_minutes = None
    day = None

    def ask_date(self, attempts):
        rec = sr.Recognizer()
        week_days = {'lunedì':0, 'martedì':1, 'mercoledì':2, 'giovedì':3, 'venerdì':4, 'sabato':5, 'domenica':6}
        if attempts == 0:
            Speak.speak('Certo. Che giorno?')
        if attempts == 3:
            return
        with sr.Microphone() as mic:
            try:
                rec.adjust_for_ambient_noise(mic)
                voice = rec.listen(mic)
                day = str(rec.recognize_google(voice, language='it-IT')).lower()
                if week_days.__contains__(day.lower()):
                    return week_days[day.lower()]
                else:
                    raise Exception('No day provided.')
            except:
               Speak.speak('Non ho capito che giorno. Ripeti per favore')
               self.ask_date(attempts + 1)

    def ask_time(self, attempts):
        rec = sr.Recognizer()
        if attempts == 0:
            Speak.speak('Ok, a che ora?')
        if attempts == 3:
            return
        with sr.Microphone() as mic:
            try:
                rec.adjust_for_ambient_noise(mic)
                voice = rec.listen(mic)
                time = str(rec.recognize_google(voice, language='it-IT')).lower()
                if time.__contains__(':'):
                    time_list = time.split(':')
                    if int(re.search(r'\d+', time_list[0]).group()) < 24:
                        self.orario = [int(re.search(r'\d+', time_list[0]).group()), int(time_list[1])]
                    else: raise Exception('Hour greater than 23')
                elif int(re.search(r'\d+', time).group()) < 24:
                    self.orario = [int(re.search(r'\d+', time).group()), 00]
                else:
                    raise Exception('No number provided')
            except Exception as e:
                print(e)
                Speak.speak('Non ho capito a che ora. Ripeti per favore')
                self.ask_time(attempts + 1)

    def set_task(self, day):
        today = datetime.datetime.today().weekday()
        remaining_days = int(day) - today
        self.day = day
        time = self.orario
        if time is None or today is None:
            raise Exception('Time or Date not provided. They are required.')
        SaveTxt().Main('timers', ['timer_memo', 'timer_day', 'timer_time'], [self.memo, str(day), str(time[0]) + str(time[1])])

        todays_minutes = int(datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
        timer_minutes = int(time[0]) * 60 + int(time[1]) + 1440 * int(remaining_days) - int(todays_minutes)
        if timer_minutes <= 0:
            DeleteTxt().partition('timers')
            SaveTxt().add_partition('timers')
        Speak.speak(f'Bene! Il timer si attiverà tra {timer_minutes} minuti')
        thread = threading.Thread(target=self.start_timer, args=(self.memo, self.orario, self.day))
        thread.start()

    def start_timer(self):
        time.sleep(int(self.timer) * 60)
        Speak.speak(f'Hey, ricordati di {self.memo}. Mi raccomando!')
        sound_file_location = str(Path(__file__).parent) + '\DieForYou.mp3'
        print(f'SOUND PATH: {sound_file_location}')
        DeleteTxt().partition('timers')
        playsound.playsound(sound_file_location)
        # sound doesn't work (?)

    def start_timer(self, memo, timer, day):
        remaining_days = int(day) - datetime.datetime.today().weekday()
        todays_minutes = int(datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
        timer_minutes = int(float(timer[0])) * 60 + int(float(timer[1])) + 1440 * int(remaining_days) - int(float(todays_minutes))
        if timer_minutes <= 0 or timer_minutes > 1440 * 7:
            DeleteTxt().partition('timers')
            return
        time.sleep(timer_minutes * 60)
        Speak.speak(f'Hey, ricordati di {memo}. Mi raccomando!')
        sound_file_location = str(Path(__file__).parent) + '\DieForYou.mp3'
        print(f'SOUND PATH: {sound_file_location}')
        DeleteTxt().partition('timers')
        playsound.playsound(sound_file_location)
        # sound doesn't work (?)

    def Main(self, command):
        self.memo = command.split('di ')[1]
        day = self.ask_date(0)
        self.ask_time(0)
        self.set_task(day)


class Stop(object):
    def Main(self, command):
        print(f'Closing the istance of the script')
        sys.exit(0)


class RandomNumber(object):
    random_range = []
    min = None
    max = None

    def Main(self, command):
        if not command.__contains__('numero a caso') and not command.__contains__('random') and not command.__contains__('randomico'):
            raise Exception('Il comando era impreciso o errato.')
        
        self.random_range = self.get_num_list(command)
        if self.random_range is []:
            raise Exception('You specified more than 2 numbers.')
        if self.random_range is None:
            self.min = 0
            self.max = 10
        else:
            self.random_range.sort()
            self.min = self.random_range[0]
            self.max = self.random_range[1]
        number = int(random.randrange(self.min, self.max))
        Speak.speak('Il numero magico è...')
        time.sleep(1)
        Speak.speak(str(number))


    def get_num_list(self, command):
        int_list = list(map(int, re.findall(r'\d+', command)))
        if len(int_list) == 0:
            return None
        if len(int_list) > 2:
            return []
        return int_list