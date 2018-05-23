#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import socket
import logging
import os

from generator import generate_templates



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('client_name', type=str)
  parser.add_argument('--base_dir', default='/etc/openvpn/clients')
  parser.add_argument('--country_name', default='RU')
  parser.add_argument('--hostname', default='localhost')
  parser.add_argument('--organization', default='TLD')
  parser.add_argument('--days', type=int, default=365)
  parser.add_argument('--verb', type=int, default=30)
  parser.add_argument('--ip', type=str, default=socket.gethostbyname(socket.gethostname()))
  args = parser.parse_args()
  
  if not os.path.isfile(
    '{}/{}_tcp.ovpn'.format(
      args.base_dir, args.client_name
    )
  ) or not os.path.isfile(
    '{}/{}_udp.ovpn'.format(
      args.base_dir, args.client_name
    )
  ):
    generate_templates(
      client_name = args.client_name,
      country_name = args.country_name,
      hostname = args.hostname,
      organization = args.organization,
      days = args.days,
      verb = args.verb,
      base_dir = args.base_dir,
      ip = args.ip
    )

