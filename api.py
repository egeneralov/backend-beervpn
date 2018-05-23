#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import socket

from flask import Flask, jsonify, request

from generator import generate_templates



app = Flask(__name__)

@app.route('/generate/openvpn/<client_name>/')
def generate_openvpn(client_name):
  if not os.path.isfile(
    '{}/{}_tcp.ovpn'.format(
      args.base_dir, client_name
    )
  ) or not os.path.isfile(
    '{}/{}_udp.ovpn'.format(
      args.base_dir, client_name
    )
  ):
    if generate_templates(
      client_name = client_name,
      country_name = request.args.get('country_name'),
      hostname = request.args.get('hostname'),
      organization = request.args.get('organization'),
      days = request.args.get('days'),
      verb = request.args.get('verb'),
      base_dir = args.base_dir,
      ip = socket.gethostbyname(socket.gethostname())
    ):
      return jsonify({
        'status': True
      })
  else:
    return jsonify({
      'status': True
    })

@app.route('/get/openvpn/<client_name>/')
def get_openvpn(client_name):
  answer = {'status': True}
  for ovpntype in ['tcp', 'udp']:
    with open(
      '{}/{}_{}.ovpn'.format(
        args.base_dir, client_name, ovpntype
      )
    ) as f:
      answer[ovpntype] = f.read()
  return answer


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--base_dir', default='/etc/openvpn/clients')
  args = parser.parse_args()
  app.run(host='0.0.0.0',port=8080,debug=True)


