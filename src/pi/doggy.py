#! /usr/bin/env python3
import argparse
import serial
import websockets
import asyncio
import random
import math
import requests
import json

test_modes = ["off", "random", "counter", "wave"]

def counter(i):
	return str(i % 100)

def wave(i):
	return str(int(50*math.sin(i/5)) + 50)

def rand(i):
	return str(random.randint(0, 100))

def create_dog(args):
	URL = "http://" + args.uri + "/rsrc/dog"
	print(URL)
	r = requests.post(url=URL)
	msg = json.loads(r.text)
	if args.verbose:
		print("Created dog", msg["id"])

	URL = "http://" + args.uri + "/rsrc/ing/" + msg["id"]
	print(URL)
	r = requests.post(url=URL, json={"fileName": "outdata.csv", "log": False})

	return msg["id"]

async def socket(args, uri, wait, next_line, send):
	if args.verbose:
		print("Connecting to ws", uri)
	async with websockets.connect(uri) as ws:
		if send is None:
			send = ws.send
		if args.verbose:
			print("Connection established")
		while True:
			await wait()
			try:
				line = next_line()
				line = line.decode("UTF-8").strip()
				if args.verbose:
					print(line)
				await send(line)
			except:
				pass


async def main(args):
	if args.verbose:
		print("Started up in main mode")
	ser = None
	if args.test == test_modes[0]:
		ser = serial.Serial(args.serial, 9600)

	async def ser_wait():
		while ser.in_waiting == 0:
			pass
	async def no_wait():
		await asyncio.sleep(1)

	wait = ser_wait if ser else no_wait

	if args.test == test_modes[0]:
		next_line = ser.readline
	if args.test == test_modes[1]:
		next_line = rand
	elif args.test == test_modes[2]:
		next_line = counter
	elif args.test == test_modes[3]:
		next_line = wave

	async def no_send(data):
		return

	send = None if ser else no_send

	while True:
		if args.verbose:
			print("Attempting connection")
		try:
			if args.uri:
				ws_uri = "ws://" + args.uri
				dog_id = create_dog(args)
				ws_uri += f"/ws/ing/{dog_id}/1"
				if args.verbose:
					print("Using websocket")
				await socket(args, ws_uri, wait, next_line, send)
			else:
				if args.verbose:
					print("No websocket provided")
				while True:
					await wait()
					line = next_line()

					print(line)
		except Exception as e:
			if args.verbose:
				print("Exception occured. Connection closed due to", e)
				print("Trying connection again in 5 seconds")
			await asyncio.sleep(5)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Read given serial port.')
	parser.add_argument('-s', '--serial', help='serial port (ex: /dev/ttyACM0)', type=str, default="/dev/ttyACM0")
	parser.add_argument('-u', '--uri', help='the uri to connect to', type=str)
	parser.add_argument('-v', '--verbose', help='set verbose print', action='store_true')
	parser.add_argument('--test', help='set to test modes (default is "off")', choices=test_modes, default=test_modes[0])

	args = parser.parse_args()

	asyncio.run(main(args))
