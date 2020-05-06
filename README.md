# DVMN telegram notification bot
This a simple telegram bot designed to send notifications in 
you telegram chat in case if your task from [dvmn](https://dvmn.org)
is checked.

### How to Install

Python3 should be already installed. Then use pip (or pip3,
if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
To run this program you need to copy your [API devman](https://dvmn.org/api/docs/)
token and save it in **.env** file which you should create
in the same directory with **main.py** file.
Also you need to save in the same **.env** file your telegram
bot API key and your telegram chat id.
Your **.env** file should look like this:
```
TOKEN=your devman API token
T_API_TOKEN=your telegram bot API key
CHAT_ID=your telegram chat ID
```

### Project Goals
The code is written for educational purposes on online-course 
for web-developers [dvmn.org](https://dvmn.org).