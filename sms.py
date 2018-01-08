#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: sms.py


################

import nexmo

key = '3ab7e80a'
secret = '29e759265059bb18'

client = nexmo.Client(key=key, secret=secret)

def send_sms(number, message):
  client.send_message({
    'from': 12015946703,
    'to': number,
    'text': message,
    'type': 'unicode'
  })

phone = 16267318573
text = 'A text message sent using the Nexmo SMS API'
#send_sms(phone, text)

