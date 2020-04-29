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

    messagesByDay = getMessagesByDay(df)

    poohMessagesByDate = getMessagesByDate(df.loc[df['Author'] == 'Fergal', 'Date'])
    kittyMessagesByDate = getMessagesByDate(df.loc[df['Author'] == 'Janice', 'Date'])

    totalMessageByDate = getTotalMessageByDate(poohMessagesByDate, kittyMessagesByDate)

    poohFreqWords = getFrequentWords(df.loc[df['Author'] == 'Fergal', ['Author', 'Message']], 10)
    poohFreqLabel, poohFreqCount = populateLabelCount(poohFreqWords)

    kittyFreqWords = getFrequentWords(df.loc[df['Author'] == 'Janice', ['Author', 'Message']], 10)
    kittyFreqLabel, kittyFreqCount = populateLabelCount(kittyFreqWords)

    poohFreqEmojis = getFrequentEmojis(df.loc[df['Author'] == 'Fergal', 'Message'])
    poohFreqEmojiLabel, poohFreqEmojiCount = populateLabelCount(poohFreqEmojis)

    kittyFreqEmojis = getFrequentEmojis(df.loc[df['Author'] == 'Janice', 'Message'])
    kittyFreqEmojiLabel, kittyFreqEmojiCount = populateLabelCount(kittyFreqEmojis)

    poohFreqNicknames = getFrequentNicknames(df.loc[df['Author'] == 'Fergal', 'Message'])
    poohFreqNickLabel, poohFreqNickCount = populateLabelCount(poohFreqNicknames)

    kittyFreqNicknames = getFrequentNicknames(df.loc[df['Author'] == 'Janice', 'Message'])
    kittyFreqNickLabel, kittyFreqNickCount = populateLabelCount(kittyFreqNicknames)

    top50Words = getFrequentWords(df[['Author', 'Message']], 150)
    for index, word in enumerate(top50Words):
        new_word = list(word)

        if index < 10:
            new_word.append(10)
        elif 10 <= index < 20:
            new_word.append(9)
        elif 20 <= index < 30:
            new_word.append(8)
        elif 30 <= index < 50:
            new_word.append(7)
        elif 50 <= index < 80:
            new_word.append(6)
        elif 80 <= index < 110:
            new_word.append(5)
        elif 110 <= index < 140:
            new_word.append(4)
        elif 140 <= index < 160:
            new_word.append(3)
        elif 160 <= index < 180:
            new_word.append(2)
        elif 180 <= index < 200:
            new_word.append(1)

        if len(new_word) < 5:
            new_word_pooh = df.loc[df['Author'] == 'Fergal', 'Message'].str.lower().str.count(new_word[0]).sum()
            new_word_kitty = df.loc[df['Author'] == 'Janice', 'Message'].str.lower().str.count(new_word[0]).sum()
            if new_word_pooh > new_word_kitty:
                new_word.insert(3, new_word_kitty)
            else:
                new_word.insert(2, new_word_pooh)

        top50Words[index] = tuple(new_word)

    random.shuffle(top50Words)

    return render(
        request, 'home/home.html', {
            'data': df,
            'FergalByDay': list(messagesByDay['Fergal'].values()),
            'JaniceByDay': list(messagesByDay['Janice'].values()),
            'TotalByDay': list(messagesByDay['Total'].values()),
            'FergalFreqLabel': poohFreqLabel,
            'FergalFreqCount': poohFreqCount,
            'JaniceFreqLabel': kittyFreqLabel,
            'JaniceFreqCount': kittyFreqCount,
            'FergalFreqNickLabel': poohFreqNickLabel,
            'FergalFreqNickCount': poohFreqNickCount,
            'JaniceFreqNickLabel': kittyFreqNickLabel,
            'JaniceFreqNickCount': kittyFreqNickCount,
            'FergalFreqEmojiLabel': poohFreqEmojiLabel,
            'FergalFreqEmojiCount': poohFreqEmojiCount,
            'JaniceFreqEmojiLabel': kittyFreqEmojiLabel,
            'JaniceFreqEmojiCount': kittyFreqEmojiCount,
            'FergalMessageDate': poohMessagesByDate['dates'],
            'FergalMessageCount': poohMessagesByDate['numMessages'],
            'JaniceMessageDates': kittyMessagesByDate['dates'],
            'JaniceMessageCount': kittyMessagesByDate['numMessages'],
            'TotalMessageCount': totalMessageByDate,
            'Top50Words': top50Words
        }
    )


def populateLabelCount(data):
    label, count = [], []
    for t in data:
        label.append(str(list(t)[0]))
        count.append(list(t)[1])
    return label, count


def getMessagesByDate(data):
    dates, numMessages, counter = [], [], 0

    for index, row in enumerate(data.iteritems()):
        if index == 0:
            dates.append(row[1])
            counter += 1
        elif not row[1] in dates:
            numMessages.append(counter)
            dates.append(row[1])
            counter += 1

        elif index + 1 == len(data):
            counter += 1
            numMessages.append(counter)
        else:
            counter += 1

    return {'dates': dates, 'numMessages': numMessages}


def getTotalMessageByDate(pooh, kitty):
    totalDates = []
    totalCount = []
    for index, date in enumerate(kitty['dates']):
        for index2, date2 in enumerate(pooh['dates']):
            if date == date2:
                totalDates.append(date)
                totalCount.append(kitty['numMessages'][index] + pooh['numMessages'][index2])
    return totalCount


def getMessagesByDay(data):
    result = {
        'Fergal': {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0},
        'Janice': {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0},
        'Total': {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
    }
    for index, row in data.iterrows():
        author = row['Author']
        day = str(datetime.strptime(row['Date'], '%d/%m/%Y').weekday())
        result[author][day] += 1
        result['Total'][day] += 1

    return result


def getFrequentEmojis(data):
    filtered_words = data.apply(lambda x: [item for item in x if item in emoji.UNICODE_EMOJI])
    filtered_data_frame = filtered_words.to_frame(name='words')
    filtered_words.reset_index(drop=True, inplace=True)  # As needed
    filtered_data_frame['message'] = [' '.join(map(str, l)) for l in filtered_data_frame['words']]

    return Counter(" ".join(filtered_data_frame['message']).split()).most_common(10)


def splitEmojis(data):
    row_split_emoji = emoji.get_emoji_regexp().split(data)
    return " ".join(row_split_emoji)


def getFrequentWords(data, size):
    stop = stopwords.words('english')
    custom_stop = ['i\'m', 'i’m', '...', '..',  '\u200d', 'it’s', 'it\'s', 'im', 'get', 'come', 'never', 'youre', 'still', 'actually', 'time', 'anything',
                   'come', 'well', 'send' 'it’s', 'don’t', 'that’s', 'maybe', 'need', '<media', 'omitted>', 'yes',
                   'like', 'tomorrow', 'see', 'thats', 'yesss', 'long', 'know', 'wait', 'use', 'things', 'back',
                   'want', 'go', 'think', 'much', 'today', '~~', '~']
    stop.extend(custom_stop)

    filtered_words = data['Message'].str.lower().str.split().apply(lambda x: [item for item in x if item not in stop])\
        .apply(lambda x: [item for item in x if item not in emoji.UNICODE_EMOJI])
    filtered_data_frame = filtered_words.to_frame(name='words')
    filtered_words.reset_index(drop=True, inplace=True)  # As needed
    filtered_data_frame['message'] = [' '.join(map(str, l)) for l in filtered_data_frame['words']]
    filtered_data_frame['author'] = data['Author']

    result = Counter(" ".join(filtered_data_frame['message']).split()).most_common(size)
    keys = []
    for t in result:
        keys.append(t[0])
    if size == 150:
        poohCount = Counter(" ".join(filtered_data_frame.loc[filtered_data_frame['author'] == 'Fergal', 'message']).split()).most_common(300)
        kittyCount = Counter(" ".join(filtered_data_frame.loc[filtered_data_frame['author'] == 'Janice', 'message']).split()).most_common(300)
        for index, t in enumerate(poohCount):
            if t[0] in keys:
                result[keys.index(t[0])] = result[keys.index(t[0])] + (t[1],)
        for index, t in enumerate(kittyCount):
            if t[0] in keys:
                result[keys.index(t[0])] = result[keys.index(t[0])] + (t[1],)
    return result


def getFrequentNicknames(data):
    nicknames = ['kitty', 'mistress', 'jasmine', 'jan', 'janyo', 'baby', 'bear', 'kat', 'cat', 'girl', 'korillakuma',
                 'pooh', 'riceball', 'daddy', 'master', 'doggy', 'fergal', 'janice', 'ming', 'sum', 'girlfriend',
                 'boyfriend']
    filtered_words = data.str.lower().str.split().apply(lambda x: [item for item in x if item in nicknames])

    filtered_data_frame = filtered_words.to_frame(name='words')
    filtered_words.reset_index(drop=True, inplace=True)  # As needed
    filtered_data_frame['message'] = [' '.join(map(str, l)) for l in filtered_data_frame['words']]

    return Counter(" ".join(filtered_data_frame['message']).split()).most_common(10)


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

