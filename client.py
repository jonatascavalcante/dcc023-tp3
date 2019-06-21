#!/usr/bin/env python

###########################################
#               Redes - TP3               #
#				client.py 				  #
#                                         # 
# Autor: Jonatas Cavalcante               #
# Matricula: 2014004301                   #
###########################################

import sys
import socket
import message_utils


def analyse_command(command, client_request_socket, nseq):
	tokens = command.split()
	first_char = tokens[0]
	
	if len(first_char) == 1:
		if first_char == '?':
			key = tokens[1]
			msg = message_utils.create_keyreq_msg(nseq, key)
			client_request_socket.send(msg)
			return True
		elif first_char == 'T':
			msg = message_utils.create_toporeq_msg(nseq)
			client_request_socket.send(msg)
			return True
		elif first_char == 'Q':
			client_request_socket.close()
			sys.exit()
	
	print("Comando desconhecido")
	return False

	
def client():

	if len(sys.argv) < 2:
		print("Formato esperado: python client.py <porto-local> ip: porto")
		sys.exit()

	CLIENT_PORT = sys.argv[1]
	SERVENT_ADDR = sys.argv[2]
	SERVENT_IP = SERVENT_ADDR.split(":")[0]
	SERVENT_PORT = int(SERVENT_ADDR.split(":")[1])

	client_request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_response_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	servent_addr = (SERVENT_IP, SERVENT_PORT)
	client_request_socket.connect(servent_addr)
	client_addr = ('127.0.0.1', CLIENT_PORT)
	client_response_socket.bind(client_addr)

	# Cria e envia mensagem ID dizendo que e' client
	msg = message_utils.create_id_msg(CLIENT_PORT)
	client_request_socket.send(msg)

	nseq = 0

	while True:
		command = input()
		if ( analyse_command(command, client_request_socket, nseq) ):
			last_nseq = nseq
			nseq += 1
			client_response_socket.listen(1)
			client_response_socket.setdefaulttimeout(4)
			qtd_msgs = 0
			while True:
				con, addr = client_response_socket.accept()
				try:
					message_utils.receive_servent_msg(con, addr, last_nseq)
					qtd_msgs += 1
					con.close()
				except socket.timeout:
					if qtd_msgs == 0:
						print("Nenhuma resposta recebida")
				

# Fim das declaracoes de funcoes

# Fluxo principal do programa

sys.exit(client())
