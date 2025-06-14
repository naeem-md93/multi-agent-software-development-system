from datetime import datetime


def get_now():
    return datetime.today().strptime("%Y-%m-%d %H:%M:%S")
