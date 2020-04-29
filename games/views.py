from django.shortcuts import render
import pandas as pd
from datetime import datetime
from collections import Counter
from nltk.corpus import stopwords
import functools
import operator
import re
import random

import emoji


def home(request):
    return render(request, 'games/home.html', {})


def play(request):
    parsedData = []
    conversationPath = '/Users/fergalpowell/PycharmProjects/kittyandpooh/static/home/resources/kittyandpooh.txt'
    with open(conversationPath, encoding=" utf-8 ") as fp:
        fp.readline()

        messageBuffer = []
        date, time, author = None, None, None

        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if startsWithDateTime(
                    line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author,
                                       '  '.join(
                                           messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(
                    line)

    df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
    df.head()

    df['Message'] = df['Message'].replace({'~': ''}, regex=True)
    df['Message'] = df['Message'].str.lower().apply(lambda x: splitEmojis(x))

    answerOneTotal = df.Message.str.lower().str.count("love you").sum()
    answerOnePooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count("love you").sum()
    answerOneKitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count("love you").sum()

    answerTwoTotal = df.Message.str.lower().str.count("hate you").sum()
    answerTwoPooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count("hate you").sum()
    answerTwoKitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count("hate you").sum()

    answerThreeTotal = df.Message.str.lower().str.count("kill you").sum()
    answerThreePooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count("kill you").sum()
    answerThreeKitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count("kill you").sum()

    answerFourTotal = df.Message.str.lower().str.count("annoying").sum()
    answerFourPooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count("just stop").sum()
    answerFourKitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count("just stop").sum()

    answerFiveTotal = df.Message.str.lower().str.count("sorry").sum()
    answerFivePooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count("miss you").sum()
    answerFiveKitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count("miss you").sum()

    return render(request, 'games/play.html', {
        'answerOneTotal': answerOneTotal,
        'answerOnePooh': answerOneKitty,
        'answerOneKitty': answerOnePooh,
        'answerTwoTotal': answerTwoTotal,
        'answerTwoPooh': answerTwoKitty,
        'answerTwoKitty': answerTwoPooh,
        'answerThreeTotal': answerThreeTotal,
        'answerThreePooh': answerThreeKitty,
        'answerThreeKitty': answerThreePooh,
        'answerFourTotal': answerFourTotal,
        'answerFourPooh': answerFourKitty,
        'answerFourKitty': answerFourPooh,
        'answerFiveTotal': answerFiveTotal,
        'answerFivePooh': answerFiveKitty,
        'answerFiveKitty': answerFivePooh,
    })


def getDataPoint(line):
    splitLine = line.split(' - ')  # splitLine = ['18/06/17, 22:47', 'Loki: Why do you have 2 numbers, Banner?']

    dateTime = splitLine[0]  # dateTime = '18/06/17, 22:47'

    date, time = dateTime.split(', ')  # date = '18/06/17'; time = '22:47'

    message = ' '.join(splitLine[1:])  # message = 'Loki: Why do you have 2 numbers, Banner?'

    if startsWithAuthor(message):  # True
        splitMessage = message.split(': ')  # splitMessage = ['Loki', 'Why do you have 2 numbers, Banner?']
        author = splitMessage[0]  # author = 'Loki'
        message = ' '.join(splitMessage[1:])  # message = 'Why do you have 2 numbers, Banner?'
    else:
        author = None
    return date, time, author, message


def splitEmojis(data):
    row_split_emoji = emoji.get_emoji_regexp().split(data)
    return " ".join(row_split_emoji)


def startsWithAuthor(s):
    patterns = [
        '([\w]+):',                        # First Name
        '([\w]+[\s]+[\w]+):',              # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
        '([+]\d{2} \d{4} \d{7})'           # Mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def startsWithDateTime ( s ):
    pattern = '^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False
