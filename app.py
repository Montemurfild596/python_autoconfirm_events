from flask import Flask, request, abort
import time, wget, os, smtplib, mimetypes, requests
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
from pytz import UTC
from timepad.rest import ApiException
from timepad.api import DefaultApi
from timepad.configuration import Configuration
from timepad.api_client import ApiClient               
from email import encoders                            
from email.mime.base import MIMEBase          
from email.mime.text import MIMEText          
from email.mime.image import MIMEImage       
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio


configuration1 = Configuration()
configuration1.access_token = 'c08ef390e759340fc86bd903ca8906894b59b1a4'

api_instance = DefaultApi(ApiClient(configuration1))


app = Flask(__name__)

email_domens = ['@timepath.ru', '@pminst.ru']

@app.route('/webhook', methods = ['POST'])
def webhook():
    # метод обработки вебхука
    if request.method == 'POST':
        json_request = request.json
        try:
            email = json_request["email"]
            domain = str(email)[str(email).find('@'):]
            if domain in email_domens:    # если домен подходит
                if json_request["status_raw"] == 'pending':    # проверка статуса билета
                    str_order_id = json_request["order_id"]
                    event_id = json_request["event_id"]
                    api_instance.approve_event_order(event_id, int(str_order_id))    # подтверждение заказа с помощью метода timepad api
                elif json_request["status_raw"] == 'ok':    # проверка статуса билета
                    create_calendar_file_with_utc(json_request)
                    send_email(email, json_request["event_name"], 'Добрый день.\n\nВаша регистрация на событие подтверждена.', 'event_' + str(event_id) + '.ics')
            return ('success', 200)
        except ApiException as e:
            #print("Exception when calling DefaultApi->approve_event_order: %s\n" % e)
            return ('success', 200)
    else:
        return ('success', 200)

def send_email(address_to, msg_subj, msg_text, file):
    # отправка сообщения на указанный адрес
    
    # почта
    address_from = 'myaddress@gmail.com'

    # пароль
    password = 'abcdefg12345'

    # порт
    port = 465

    msg = MIMEMultipart()
    msg['From'] = address_from
    msg['To'] = address_to
    msg['Subject'] = msg_subj

    body = msg_text
    msg.attach(MIMEText(body, 'plain'))

    attach_file(msg, file)
    #process_attachement(msg, file)

    server = smtplib.SMTP_SSL('smtp.server.ru', port)
    server.starttls()
    server.login(address_from, password)
    server.send_message(msg)
    server.quit()

def attach_file(msg: MIMEMultipart, filepath):       
    # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)                   
    ctype, encoding = mimetypes.guess_type(filepath)        
    if ctype is None or encoding is not None:               
        ctype = 'application/octet-stream'                  
    maintype, subtype = ctype.split('/', 1)                 
                                           
    with open(filepath, 'rb') as fp:
        file = MIMEBase(maintype, subtype)              
        file.set_payload(fp.read())                     
        fp.close()
        encoders.encode_base64(file)                    
    file.add_header('Content-Disposition', 'attachment', filename=filename) 
    msg.attach(file)  

def file_extract(event_id_to_str):
    # скачивание файла события и парсинг информации в словарь
    d = dict()
    url = "https://timepath.timepad.ru/event/export_ical/" + event_id_to_str + "/"
    r = requests.get(url)

    with open('timepath_' + event_id_to_str + '.ics', 'wb') as outfile:
        outfile.write(r.content)
        print(r.content)
    
    event_file = open('timepath_' + event_id_to_str + '.ics', 'rb')
    event_file_cal = Calendar.from_ical(event_file.read())
    for component in event_file_cal.walk():
        if component.name == 'VEVENT':
            d = dict(summary = component.get('summary'), dtstart = component.get('dtstart').dt, dtend = component.get('dtend').dt, dtstamp = component.get('dtstamp').dt, location = component.get('location'))
    event_file.close()
    return d

def create_calendar_file_with_utc(json_request):
    # создание файла формата .ics с UTC
    d = file_extract(json_request['event_id'])
    dtstart = d.get('dtstart')
    dtend = d.get('dtend')
    dtstamp = d.get('dtstamp')

    cal = Calendar()
    cal.add('prodid', '-//Timepad Ltd.//NONSGML Timepad//RU')
    cal.add('version', '2.0')
    event = Event()
    
    event.add('summary', d.get('summary'))
    event.add('dtstart', datetime(dtstart.year, dtstart.month, dtstart.day, dtstart.hour, dtstart.minute, dtstart.second, tzinfo=UTC))
    event.add('dtend', datetime(dtend.year, dtend.month, dtend.day, dtend.hour, dtend.minute, dtend.second, tzinfo=UTC))
    event.add('dtstamp', datetime(dtstamp.year, dtstamp.month, dtstamp.day, dtstamp.hour, dtstamp.minute, dtstamp.second, tzinfo=UTC))
    event.add('location', json_request["event_city"] + ', ' + json_request["event_place"])
    cal.add_component(event)
    f = open('event' + json_request['event_name'] + '.ics', 'wb')
    f.write(cal.to_ical())
    f.close()
    

if __name__ == '__main__':
    app.run()