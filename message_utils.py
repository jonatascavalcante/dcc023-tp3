#!/usr/bin/env python

###########################################
#               Redes - TP3               #
#		     message_utils.py             #
#                                         # 
# Autor: Jonatas Cavalcante               #
# Matricula: 2014004301                   #
###########################################

import struct


ID_MSG_TYPE = 4
KEYREQ_MSG_TYPE = 5
TOPOREQ_MSG_TYPE = 6
KEYFLOOD_MSG_TYPE = 7
TOPOFLOOD_MSG_TYPE = 8
RESP_MSG_TYPE = 9


def create_id_msg(port):
	type = struct.pack("!H", ID_MSG_TYPE)
	port = struct.pack("!H", port)

	msg = type + port

	return msg


def create_keyreq_msg(nseq, key):
	type = struct.pack("!H", KEYREQ_MSG_TYPE)
	nseq = struct.pack("!I", nseq)
	size = struct.pack("@H", len(key))

	msg = type + nseq + size + key.encode('ascii')

	return msg


def create_toporeq_msg(nseq):
	type = struct.pack("!H", TOPOREQ_MSG_TYPE)
	nseq = struct.pack("!I", nseq)

	msg = type + nseq

	return msg


def create_flood_message(msg_type, ttl, nseq, src_ip, src_port, info):
	
	if msg_type == KEYFLOOD_MSG_TYPE:
		type = struct.pack("!H", KEYFLOOD_MSG_TYPE)
	else:
		type = struct.pack("!H", TOPOFLOOD_MSG_TYPE)

	ttl = struct.pack("!H", ttl)
	nseq = struct.pack("!I", nseq)

	# TODO implementar o ip de origem em representacao binaria

	src_port = struct.pack("!H", src_port)
	size = struct.pack("@H", len(info))

	msg = type + ttl + nseq + src_ip + src_port + size + info.encode('ascii')

	return msg


def create_resp_msg(nseq, value):
	type = struct.pack("!H", RESP_MSG_TYPE)
	nseq = struct.pack("!I", nseq)
	size = struct.pack("@H", len(value))

	msg = type + nseq + size + value.encode('ascii')

	return msg


def receive_servent_msg(con, addr, nseq):
	msg_type = struct.unpack("!H", con.recv(2))
	msg_nseq = struct.unpack("!I", con.recv(4))

	if msg_type != 9 or msg_nseq != nseq:
		print("Mensagem incorreta recebida de " + addr)
		return
	else:
		msg_size = int(struct.unpack("@H", con.recv(2)))
		msg_value = con.recv(msg_size)
		print(msg_value.decode('ascii') + " " + addr)
		return


def treates_keyreq_msg(con, addr, port, socket):
	nseq = struct.unpack("!I", con.recv(4))
	size = int(struct.unpack("@H", con.recv(2)))
	key = con.recv(msg_size)

	msg = create_flood_message(KEYFLOOD_MSG_TYPE, 3, nseq, addr, port, key)
	socket.sendall(msg)


def treates_topreq_msg(con, addr, port, socket, local_port):
	nseq = struct.unpack("!I", con.recv(4))
	info = '127.0.0.1:' + str(local_port)

	msg = create_flood_message(TOPOFLOOD_MSG_TYPE, 3, nseq, addr, port, info)
	socket.sendall(msg)


def treates_servent_msgs(con, addr, socket, client_port, local_port):
	msg_type = struct.unpack("!H", con.recv(2))

	if msg_type == ID_MSG_TYPE:
		msg_port = struct.unpack("!H", con.recv(2)):
		if msg_port == 0:
			socket.con(addr)
		else:
			client_port = msg_port
	elif msg_type == KEYREQ_MSG_TYPE:
		# TODO verificar se o servent possui a chave e tratar
		treates_keyreq_msg(con, addr, client_port, socket)
	elif msg_type == TOPOREQ_MSG_TYPE:
		# TODO mandar msg resp pro client
		treates_topreq_msg(con, addr, client_port, socket, local_port)
	elif msg_type == KEYFLOOD_MSG_TYPE:
		# TODO
	elif msg_type == TOPOFLOOD_MSG_TYPE:
		# TODO
	else:
		return
