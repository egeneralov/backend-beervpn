#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import argparse
import re
import json

import telegram
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters




def create_ovpn_client_configuration(client_name):
  url = 'http://127.0.0.1:8080/generate/openvpn/{}/'.format(client_name)
  params = {
    'country_name': 'RU',
    'hostname': 'vpn.local',
    'organization': 'BeerVPN',
    'days': 365,
    'verb': 30
  }
  try:
    import requests
    r = requests.get(url, params=params).json()
    return r['status']
  except Exception as e:
    print(e)
    return False





class BeerVPN_bot:

  error = {
    404: 'К сожалению, ничего не найдено.',
    500: 'К сожалению, произошла ошибка.',
    401: 'К сожалению, доступ запрещён. Запрос на авторизацию отправлен.',
    403: 'Вы заблокированы.'
  }
  allowed_users = []
  blocked_users = []
  pending_users = []

  def __init__(self, **kwargs):
    for k in kwargs['telegram'].keys():
      logging.warning(
        'Updating {} via key: {}, with value: {}'.format(
          self.__class__, k, kwargs['telegram'][k]
        )
      )
      self.__setattr__(k, kwargs['telegram'][k])
    logging.warning('{}: kwargs result: {}'.format(self.__class__, self.__dict__))

    self.updater = Updater(token=self.token)
    self.dispatcher = self.updater.dispatcher
    self.queue = self.updater.job_queue
    self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
    self.dispatcher.add_handler(CommandHandler('generate', self.generate))
    self.dispatcher.add_handler(CommandHandler('init', self.init))
    self.dispatcher.add_handler(CommandHandler('allow', self.allow))
    self.dispatcher.add_handler(CommandHandler('start', self.start))
    self.updater.start_polling()

  def echo(self, bot, update):
    bot.send_message(
      chat_id=update.message.chat_id,
      text=update.message.text,
      parse_mode='Markdown'
    )

  def generate(self, bot, update):
    if not self.is_allowed(bot, update): return
    client = update.message.chat_id
    if create_ovpn_client_configuration(client):
      basedir = '/etc/openvpn/clients/'
      bot.send_document(
        chat_id=client,
        document=open(
          '{}/{}_udp.ovpn'.format(basedir, client),
          'rb'
        )
      )
      bot.send_document(
        chat_id=client,
        document=open(
          '{}/{}_tcp.ovpn'.format(basedir, client),
          'rb'
        )
      )
      message = '===Инструкция тут==='
    else:
      message = 'Произошла ошибка. Пните админа.'
    bot.send_message(chat_id=client, text=message)


  def start(self, bot, update):
    if not self.is_allowed(bot, update):
      message = 'Привет!\n'
      message += 'Я бот для проекта BeerVPN.\n'
      message += 'Просто ждите, пока админ разрешит вам доступ.\n'
    else:
      message = 'Для генерации своего сертификата: /generate\n'
      if update.message.chat_id in self.admins:
        message += 'Для просмотра пользователей с сертификатами: /list'
    bot.send_message(
      chat_id=update.message.chat_id,
      text=message,
      parse_mode='Markdown'
    )

  def allow(self, bot, update):
    if update.message.chat_id not in self.admins: return
    uid = int(
      update.message.text.replace('/allow ', '')
    )
    self.allowed_users.append(uid)
    rm = telegram.ReplyKeyboardRemove()
    usermsg = "Вам разрешён доступ ко мне!\n"
    usermsg += "Для генерации своего сертификата: /generate"
    bot.send_message(chat_id=uid, text=usermsg, reply_markup=rm)    
    bot.send_message(chat_id=update.message.chat_id, text="Access was granted to {}".format(uid), reply_markup=rm)    

  def init(self, bot, update):
    if update.message.chat_id in self.admins: return
    token = str(
      update.message.text.replace('/init ', '')
    )
    print( token == self.access_token )
    if token == self.access_token:
      self.admins.append(update.message.chat_id)
      self.allowed_users.append(update.message.chat_id)
      bot.send_message(chat_id=update.message.chat_id, text="You are admin!")    
    else:
      bot.send_message(chat_id=update.message.chat_id, text="Wrong token!")

  def block(self, bot, update):
    if not self.is_allowed(bot, update): return
    reply_markup = telegram.ReplyKeyboardRemove()
    return bot.send_message(chat_id=update.message.chat_id, text=update.message, reply_markup=reply_markup)    

  def is_allowed(self, bot, update):
    usr = update['message']['chat']
    uid = update['message']['chat']['id']
    if uid in self.blocked_users:
      bot.send_message(
        chat_id=uid,
        text=self.error[403],
        parse_mode='Markdown'
      )
      return False
    if not uid in self.allowed_users:
      bot.send_message(
        chat_id=uid,
        text=self.error[401],
        parse_mode='Markdown'
      )
      for admin in self.admins:
          custom_keyboard = [
            [
              telegram.KeyboardButton(text="/allow {}".format(uid)),
              telegram.KeyboardButton(text="/block {}".format(uid))
            ],
            [
              telegram.KeyboardButton(text="/clear".format(uid))
            ]
          ]
          reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
          message = "Grant access or block? {}\n".format(usr)
          message += "/allow {}\n".format(uid)
          message += "/block {}\n".format(uid)
          bot.send_message(
            chat_id=admin,
            text=message,
            parse_mode='Markdown',
            reply_markup=reply_markup
          )
      return False
    return True





def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'action',
    type=str,
  )
  return parser.parse_args()


if __name__ == '__main__':
  from config import config
  logging.basicConfig(**config['logging'])
  args = get_args()
  actions = {
    'tgbot': BeerVPN_bot,
  }
  if args.action not in actions.keys():
    raise NotImplemented('I can`t run this')
  actions[args.action](**config)







