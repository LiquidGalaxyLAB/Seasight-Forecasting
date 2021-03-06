
import configparser
import os

config = configparser.ConfigParser()
configFilePath = r'app.conf'
config.read(configFilePath)

lg_IP = config['INSTALLATION']['lg_IP']
lg_pass = config['INSTALLATION']['lg_pass']
project_location = config['INSTALLATION']['project_location']

folder_target = '/var/www/html/SF'

command = "sshpass -p {} ssh {} mkdir {}".format(lg_pass, lg_IP, folder_target)
print(command)
os.system(command)

command = "sshpass -p {} scp $HOME/{}Seasight-Forecasting/django/seasight_forecasting/static/logos/Logos.png {}:/var/www/html/SF/Logos.png".format(lg_pass, project_location, lg_IP)
print(command)
os.system(command)