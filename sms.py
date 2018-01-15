#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: sms.py


################

import nexmo

key = 'd1258708'
secret = 'ea2d3fe59f49fb64'

client = nexmo.Client(key=key, secret=secret)

def send_sms(number, message):
  client.send_message({
    'from': 16018666656,
    'to': number,
    'text': message,
    'type': 'unicode'
  })

#phone = 16267318573
#text = 'A text message sent using the Nexmo SMS API'
#send_sms(phone, text)

