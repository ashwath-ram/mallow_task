from threading import Thread
from django.core.mail import send_mail
from django.conf import settings


def send_email(subject, message, recipient_list):
    thread = Thread(
        target=send_mail,
        args=(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list),
        kwargs={'fail_silently': False}
    )
    thread.start()


def get_denominations(amount):
    denominations = [500, 50, 20, 10, 5, 2, 1]
    result = {}
    for d in denominations:
        count = amount // d
        if count > 0:
            result[d] = count
            amount %= d

    return result