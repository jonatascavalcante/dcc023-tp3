#!/usr/bin/env python

###########################################
#               Redes - TP3               #
#               servent.py                #
#                                         # 
# Autor: Jonatas Cavalcante               #
# Matricula: 2014004301                   #
###########################################

import sys
import socket
import struct
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
					value = ' '.join(text)
					dictionary.update({ key : value })

	file.close()

	return dictionary


def connect_to_neighbor(neighbor, servent_request_socket):
	neighbor_ip = neighbor.split(":")[0]
	neighbor_port = int(neighbor.split(":")[1])
	neighbor_addr = (neighbor_ip, neighbor_port)

	servent_request_socket.connect(neighbor_addr)

	msg = message_utils.create_id_msg(0)
	servent_request_socket.send(msg)


def verify_if_has_key(key_values, key, client_ip, client_port, nseq, servent_request_socket):
	if key in key_values.keys():
		msg = message_utils.create_resp_msg(nseq, key_values[key])
		client_addr = (client_ip, client_port)
		servent_request_socket.connect(client_addr)
		servent_request_socket.send(msg)
		servent_request_socket.close()


def send_msg_to_neighbors(servent_request_socket, neighbor, addr, msg)
	neighbor_ip = neighbor.split(":")[0]
	neighbor_port = int(neighbor.split(":")[1])
	src_ip = addr.split(":")[0]
	src_port = int(addr.split(":")[1])

	if neighbor_ip != src_ip and neighbor_port != src_port:
		servent_request_socket.sendto(msg, (neighbor_ip, neighbor_port))


def send_msg_to_src(servent_request_socket, src_ip, src_port, resp_msg):
	client_addr = (src_ip, src_port)
	servent_request_socket.connect(client_addr)
	servent_request_socket.send(resp_msg)
	servent_request_socket.close()


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
	servert_addr = (message_utils.LOCALHOST, LOCALPORT)
	servent_response_socket.bind(servert_addr)

	for neighbor in neighbors:
		connect_to_neighbor(neighbor, servent_request_socket)

	received_msgs = list()
	client_port = 0

	servent_response_socket.listen(1)

	while True:
		con, addr = servent_response_socket.accept()
		msg_type = struct.unpack("!H", con.recv(2))

		if msg_type == message_utils.ID_MSG_TYPE:
			msg_port = struct.unpack("!H", con.recv(2))
			if msg_port == 0:
				servent_request_socket.connect(addr)
			else:
				client_port = msg_port
		
		elif msg_type == message_utils.KEYREQ_MSG_TYPE:
			nseq, key = message_utils.get_keyreq_msg_data(con)
			verify_if_has_key(key_values, key, message_utils.LOCALHOST, client_port, nseq, servent_request_socket)
			message_utils.treates_keyreq_msg(nseq, addr, client_port, key, servent_request_socket)
		
		elif msg_type == message_utils.TOPOREQ_MSG_TYPE:
			nseq = message_utils.get_toporeq_msg_data(con)
			info = message_utils.LOCALHOST + ":" + str(LOCALPORT)
			resp_msg = message_utils.create_resp_msg(nseq, info)
			send_msg_to_src(servent_request_socket, message_utils.LOCALHOST, client_port, resp_msg)
			message_utils.treates_toporeq_msg(con, addr, client_port, servent_request_socket, LOCALPORT)
		
		elif msg_type == message_utils.KEYFLOOD_MSG_TYPE:
			ttl, nseq, src_ip, src_port, key = message_utils.get_flood_msg_data(con)
			received_msg = (src_ip, src_port, nseq)
			if received_msg not in received_msgs:
				ttl -= 1
				received_msgs.append(received_msg)
				verify_if_has_key(key_values, key, src_ip, src_port, nseq, servent_request_socket)
				if ttl > 0:
					msg = message_utils.create_flood_message(message_utils.KEYFLOOD_MSG_TYPE, ttl, nseq, src_ip, src_port, key)
					for neighbor in neighbors:
						send_msg_to_neighbors(servent_request_socket, neighbor, addr, msg)
		
		elif msg_type == TOPOFLOOD_MSG_TYPE:
			ttl, nseq, src_ip, src_port, info = message_utils.get_flood_msg_data(con)
			received_msg = (src_ip, src_port, nseq)
			if received_msg not in received_msgs:
				ttl -= 1
				received_msgs.append(received_msg)
				info += servert_addr[0] + ":" + servert_addr[1]
				resp_msg = message_utils.create_resp_msg(nseq, info)
				send_msg_to_src(servent_request_socket, src_ip, src_port, resp_msg)
				if ttl > 0:
					msg = message_utils.create_flood_message(message_utils.TOPOFLOOD_MSG_TYPE, ttl, nseq, src_ip, src_port, info)
					for neighbor in neighbors:
						send_msg_to_neighbors(servent_request_socket, neighbor, addr, msg)
		
# Fim das declaracoes de funcoes

# Fluxo principal do programa

sys.exit(servent())
