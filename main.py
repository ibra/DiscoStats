import click
from collections import defaultdict, OrderedDict
import csv
from datetime import datetime
import os
from prettytable import PrettyTable
import re


@click.command()
@click.option('--dir', default="package")
def main(dir):
    package_dir = os.path.join(os.getcwd(), dir)
    if(os.path.exists(package_dir) == False):
        print("Could not find the package directory! Make sure its in the project folder and is unzipped into one \"package\" folder.")
        return

    messages = {}
    words = []

    messagesPerDay = defaultdict(int)
    emojisUsed = defaultdict(int)
    mentionedUsers = defaultdict(int)
    cumulativeChars = 0

    messages_dir = os.path.join(dir, "messages")
    for path, _, files in os.walk(messages_dir):
        for name in files:
            if name.endswith(".csv"):
                with open(os.path.join(path, name), "r", encoding='cp437') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        date = re.match(
                            r'\d{4}-\d{2}-\d{2}', row[1])[0]
                        dateAndTime = re.match(
                            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', row[1])[0]

                        messages[dateAndTime] = row[2]
                        messagesPerDay[date] += 1

                        emojis = re.findall(r'<:\w+:[0-9]+>', row[2])
                        if emojis:
                            for match in emojis:
                                emojisUsed[match] += 1

                        mentions = re.findall(r'<@!*&*[0-9]+>', row[2])
                        if mentions:
                            for match in mentions:
                                mentionedUsers[match] += 1

                        cumulativeChars += len(row[2])
                        lineWords = re.findall(r'\w+', row[2])
                        for word in lineWords:
                            words.append(word)

    cumulativeMessages = sum(messagesPerDay.values())
    messages = OrderedDict(sorted(messages.items(
    ), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'), reverse=False))

    table = PrettyTable(['Stat', 'Value'])

    table.add_row(
        ['Cumulative Messages', f'{"{:,}".format(cumulativeMessages)} messages, {"{:,}".format(len(words))} words'])
    table.add_row(['Average Message Length',
                  f'{str(round(len(words)/cumulativeMessages, 2))} words, {str(round(cumulativeChars/cumulativeMessages, 2))} characters'])

    table.add_row(
        ["Chattiest Day", f'{max(messagesPerDay, key=messagesPerDay.get)} ({max(messagesPerDay.values())} messages)'])

    if len(emojisUsed) > 0:
        table.add_row(
            ["Most Used Emoji", f'{max(emojisUsed, key=emojisUsed.get)} ({max(emojisUsed.values())} uses)'])
    table.add_row(["Most Mentioned User",
                  f'{max(mentionedUsers, key=mentionedUsers.get)} ({max(mentionedUsers.values())} mentions)'])
    table.add_row(["First Discord Message", list(messages.items())[0][1]])

    print(table)
    print("Due to certain limitations on Discord's end, only id's can be printed for the values of some rows.")

if __name__ == '__main__':
    main()