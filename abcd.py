import app
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC



def create_calendar_file_with_utc1(a):
    #TODO создание файла формата .ics с UTC
    d = app.file_extract(a)
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
    event.add('location', d.get('location'))
    cal.add_component(event)
    f = open(a + '.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

d = app.file_extract('2502914')
print(d)
create_calendar_file_with_utc1('2502914')