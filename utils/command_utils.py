import datetime

def validate_arguments(args):
    if len(args) == 1:
        return nextday() 
    if len(args) == 2:
        selected_day = datetime.datetime.strptime(args[1], '%Y-%m-%d').date()
        return selected_day

def nextday():
    today = datetime.date.today()
    if today.weekday() == 4:
        return (today + datetime.timedelta(days=3))
    return today + datetime.timedelta(days=1)