#!/usr/bin/env python

###########################################
#               Redes - TP3               #
#				servent.py 				  #
#                                         # 
# Autor: Jonatas Cavalcante               #
# Matricula: 2014004301                   #
###########################################

import sys
import socket
import message_utils


def read_file(fileName):
	try:
		file = open(fileName, "r")
	except (OSError, IOError) as error:
		print("Erro ao abrir arquivo.")

	dictionary = {}
	for line in file:
		# linha nao vazia
		if not line.isspace():
			words = line.split()
			# primeira palavra da linha
			if words[0] != '#':
				first_character = str.strip(words[0][0])
				# verifica se o primeiro caracter nao e' #
				if first_character != '#':
					key = str.strip(words[0])
					text = words[1:]
					values = ' '.join(text)
					dictionary.update({ key : values })

	file.close()

	return dictionary


def connect_to_neighbor(neighbor, servent_request_socket):
	neighbor_ip = neighbor.split(":")[0]
	neighbor_port = int(neighbor.split(":")[1])
	neighbor_addr = (neighbor_ip, neighbor_port)

	servent_request_socket.connect(neighbor_addr)

	msg = message_utils.create_id_msg(0)
	servent_request_socket.send(msg)


def servent():
	params = len(sys.argv)

	if params < 3:
		print("Formato esperado: python servent.py <porto-local> <banco-chave-valor> [ip1: porto1 [ip2:porto2 ...]]")
		sys.exit()

	LOCALPORT = int(sys.argv[1])
	FILE = sys.argv[2]

	neighbors = list()
	for i in range(3, params):
		neighbors.append(sys.argv[i])

	key_values = {}
	key_values = read_file(FILE)

	servent_response_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servent_request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servert_addr = ('127.0.0.1', LOCALPORT)
	servent_response_socket.bind(servert_addr)

	for neighbor in neighbors:
		connect_to_neighbor(neighbor, servent_request_socket)

	received_msgs = list()
	client_port = 0

	servent_response_socket.listen(1)

	while True:
		con, addr = servent_response_socket.accept()
		treates_servent_msgs(con, addr, servent_request_socket, client_port)

# Fim das declaracoes de funcoes

# Fluxo principal do programa

sys.exit(servent())
