from datetime import datetime


def get_now():
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")
