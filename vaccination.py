import datetime
import time
import urllib
import requests
import json

from db_operation import VaccinationDB

db = VaccinationDB()

TOKEN = "5391829456:AAGkJzvwpQ46XW2YRH-TcSv16gCtd4TN-ko"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_request(url):
    response = requests.get(url)
    data = response.content.decode('utf-8')
    return data


def get_json_data(url):
    data = get_request(url)
    json_data = json.loads(data)
    return json_data


def get_update(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += '&offset={}'.format(offset)
    json_data = get_json_data(url)
    return json_data


def send_reply(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_request(url)


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def get_next_dates():
    dates = []
    for day in range(3):
        date = str(datetime.datetime.today() + datetime.timedelta(days=day+1)).split(' ')[0]
        dates.append(date)
    return dates


def get_slots(date):
    slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00', '02:00-03:00', '03:00-04:00', '04:00-05:00']
    check = db.check_slot(date).fetchone()
    if check:
        slots = set(slots)
        slots.difference_update(set(check))
        slots = list(slots)
    return slots[:3]


def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
        except KeyError:
            chat = update["my_chat_member"]["chat"]["id"]
            send_reply("Unknown Error from user end",chat)

        try:
            record = db.get_items(chat).fetchone()
            if text.lower() == "book":
                if record:
                    message = "Your Appointment is already booked!.. {} , Your {} vaccination apppointment is booked successfully for {}'o clock on {} at {} \n Send <Cancel | cancel> to delete".format(
                        record[1], record[3], record[5], record[4], record[2])
                    send_reply(message, chat)
                else:
                    db.add_item(owner_id=chat)
                    send_reply("Please Enter Name:", chat)
            else:
                if record[1] == None:
                    send_reply("Please Enter location:", chat)
                    db.update_item(owner_id=chat, column='name', data=text)
                elif record[2] == None:
                    keyboard = build_keyboard(["Corona", "Polio", "Rabiz"])
                    send_reply("Select Service:", chat, keyboard)
                    db.update_item(owner_id=chat, column='location', data=text)
                elif record[3] == None:
                    keyboard = build_keyboard(get_next_dates())
                    send_reply("Select Date :", chat, keyboard)
                    db.update_item(owner_id=chat, column='service', data=text)
                elif record[4] == None:  # elif record[4] == None:   lets check slot
                    keyboard = build_keyboard(get_slots(record[4]))
                    send_reply("Select Slot :", chat, keyboard)
                    db.update_item(owner_id=chat, column='date', data=text)
                elif text.lower() == "cancel":
                    db.delete_item(chat)
                    send_reply("Your appointment is cancelled", chat)
                elif text.lower() == "\start":
                    continue
                else:
                    if record[5]:
                        message = "Your Appointment is already booked!.. {} , Your {} vaccination apppointment is booked successfully for {}'o clock on {} at {} \n Send <Cancel | cancel> to delete".format(
                            record[1], record[3], record[5], record[4], record[2])
                        send_reply(message, chat)
                    else:
                        db.update_item(owner_id=chat, column='slot', data=text)
                        record=db.get_items(owner=chat).fetchone()
                        message = "Congratulations!!.. {} , Your {} vaccination apppointment is booked successfully for {}'o clock on {} at {}".format(
                            record[1], record[3], record[5], record[4], record[2])
                        send_reply(message, chat)
        except:
            send_reply("No appointment found \nPlease enter <Book | book> to book an appointment", chat)


def main():
    get_next_dates()
    db.setup()
    last_update_id = None
    while True:
        updates = get_update(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
