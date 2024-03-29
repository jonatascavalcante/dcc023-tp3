#!/usr/bin/env python3

###########################################
#               Redes - TP3               #
#               servent.py                #
#                                         #
# Autores: Jonatas Cavalcante             #
#          Mateus Hilario Lima            #
#                                         #
# Matriculas: 2014004301                  #
#             2015033437                  #
###########################################

import sys
import socket
import struct
import message_utils
import select
import queue

def read_file(file_name):
	try:
		file = open(file_name, "r")
	except (OSError, IOError) as error:
		print("Erro ao abrir arquivo.")

	# Monta o dicionario chave-valor com base no arquivo
	dictionary = {}
	for line in file:
		if not line.isspace(): # Linha nao vazia
			words = line.split()
			if words[0] != '#': # Primeira palavra da linha
				first_character = str.strip(words[0][0])
				if first_character != '#': # Verifica se o primeiro caracter nao e' #
					key = str.strip(words[0])
					text = words[1:]
					value = ' '.join(text)
					dictionary.update({ key : value })

	file.close()

	return dictionary


def set_servent_socket(servert_addr):
	# Realiza a configuracao do socket do servent principal
	servent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servent_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	servent_socket.setblocking(0)
	servent_socket.bind(servert_addr)

	return servent_socket


def connect_to_neighbor(connection_socket, neighbor):
	# Conecta o servent ao vizinho
	neighbor_ip = neighbor.split(":")[0]
	neighbor_port = int(neighbor.split(":")[1])
	neighbor_addr = (neighbor_ip, neighbor_port)

	connection_socket.connect(neighbor_addr)
	connection_socket.setblocking(0)

	# Envia mensagem ID para o vizinho
	msg = message_utils.create_id_msg(0)
	connection_socket.send(msg)


def send_msg_to_client(msg, src_ip, src_port):
	# Configura o socket pra enviar a resposta
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_addr = (src_ip, src_port)
	client_socket.connect(client_addr)
	client_socket.send(msg)
	client_socket.close()


def flood_msg(msg, connection):
	for input in inputs:
		# Envia a mensagem para todos vizinhos, exceto o que enviou a mensagem
		if input is not servent_socket and input is not connection:
			input.send(msg)


def verify_if_has_key(key_values, key, nseq, port, connection, ttl):
	# Verifica se possui a chave consultada
	if key in key_values.keys():
		msg = message_utils.create_resp_msg(nseq, key_values[key])
		send_msg_to_client(msg, message_utils.LOCALHOST, port)
	else:
		# Transmite a mensagem keyflood a todos os vizinhos, se TTL maior que 0
		if ttl > 0:
			msg = message_utils.create_flood_message(message_utils.KEYFLOOD_MSG_TYPE, 
				ttl, nseq, port, key)
			flood_msg(msg, connection)

# Fim das declaracoes de funcoes

# Fluxo principal do programa

params = len(sys.argv)

if params < 3:
	print("Formato esperado: python servent.py <porto-local> <banco-chave-valor> [ip1: porto1 [ip2:porto2 ...]]")
	sys.exit()

# Obtem dados da porta e do arquivo da entrada
LOCALPORT = int(sys.argv[1])
FILE = sys.argv[2]

# Adiciona os vizinhos passados por parametro
neighbors = list()
for i in range(3, params):
	neighbors.append(sys.argv[i])

# Monta o dicionario de par chave-valor do servent corrente 
key_values = {}
key_values = read_file(FILE)

# Configura socket principal que recebe conexoes/mensagens
servert_addr = (message_utils.LOCALHOST, LOCALPORT)
servent_socket = set_servent_socket(servert_addr)
servent_socket.listen()

received_msgs = list() 		# Lista das mensagens ja recebidas
connected_servents = list()	# Lista dos servents conectados
connected_clients = {}		# Lista com os clientes conectados
inputs = [servent_socket]	# Sockets que vamos ler
outputs = [] 				# Sockets que vamos escrever
message_queues = {} 		# Filas de mensagens enviadas

# Percorre a lista de vizinhos do servent e conecta a cada um deles
for neighbor in neighbors:
	connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connect_to_neighbor(connection_socket, neighbor)
	inputs.append(connection_socket)
	message_queues[connection_socket] = queue.Queue()

while inputs:

	try:
		# Aguarda pelo menos um dos sockets estar pronto para ser processado
		readable, writable, exceptional = select.select(inputs, outputs, inputs)

		for current_socket in readable:
			if current_socket is servent_socket:
				connection, client_address = current_socket.accept()
				connection.setblocking(0)
				inputs.append(connection)

				# Fornece a conexão para enfileirar os dados que desejamos enviar
				message_queues[connection] = queue.Queue()

			else:
				# Obtem o tipo da mensagem recebida
				msg_type = struct.unpack("!H", current_socket.recv(2))[0]

				if msg_type:
					# Trata o recebimento de mensagem do tipo ID
					if msg_type == message_utils.ID_MSG_TYPE:
						msg_port = struct.unpack("!H", current_socket.recv(2))[0]
						if msg_port == 0:
							connected_servents.append(current_socket.getpeername())
						else:
							connected_clients.update({ current_socket.getpeername() : msg_port })
					
					# Trata o recebimento de mensagem do tipo keyreq
					elif msg_type == message_utils.KEYREQ_MSG_TYPE:
						nseq, key = message_utils.get_keyreq_msg_data(current_socket)
						client_port = connected_clients[current_socket.getpeername()]
						verify_if_has_key(key_values, key, nseq, client_port, current_socket, 3)
					
					# Trata o recebimento de mensagem do tipo toporeq
					elif msg_type == message_utils.TOPOREQ_MSG_TYPE:
						nseq = message_utils.get_toporeq_msg_data(current_socket)
						info = message_utils.LOCALHOST + ":" + str(LOCALPORT)
						resp_msg = message_utils.create_resp_msg(nseq, info)

						client_port = connected_clients[current_socket.getpeername()]
						send_msg_to_client(resp_msg, message_utils.LOCALHOST, client_port)
						
						# Transmite a mensagem topoflood a todos os vizinhos
						msg = message_utils.create_flood_message(message_utils.TOPOFLOOD_MSG_TYPE, 
								3, nseq, client_port, info)
						flood_msg(msg, current_socket)
						
					# Trata o recebimento de mensagem do tipo keyflood
					elif msg_type == message_utils.KEYFLOOD_MSG_TYPE:
						ttl, nseq, src_ip, src_port, key = message_utils.get_flood_msg_data(current_socket)
						received_msg = (src_ip, src_port, nseq)

						# Verifica se ja recebeu essa mensagem antes
						if received_msg not in received_msgs:
							ttl -= 1
							received_msgs.append(received_msg)
							# Verifica se possui a chave consultada
							verify_if_has_key(key_values, key, nseq, src_port, current_socket, ttl)
					
					# Trata o recebimento de mensagem do tipo topoflood
					elif msg_type == message_utils.TOPOFLOOD_MSG_TYPE:
						ttl, nseq, src_ip, src_port, info = message_utils.get_flood_msg_data(current_socket)
						received_msg = (src_ip, src_port, nseq)
						# Verifica se ja recebeu essa mensagem antes
						if received_msg not in received_msgs:
							ttl -= 1
							received_msgs.append(received_msg)
							info += " " + servert_addr[0] + ":" + str(servert_addr[1])

							# Envia a mensagem resp para o client
							resp_msg = message_utils.create_resp_msg(nseq, info)
							send_msg_to_client(resp_msg, message_utils.LOCALHOST, src_port)

							if ttl > 0:
								# Transmite a mensagem a todos os vizinhos, exceto o que mandou a msg
								msg = message_utils.create_flood_message(message_utils.TOPOFLOOD_MSG_TYPE, 
									ttl, nseq, src_port, info)
								flood_msg(msg, current_socket)

					# Adiciona um canal de saida para resposta
					if current_socket not in outputs:
						outputs.append(current_socket)
				
				else:
					# Deixa de escutar por input na conexao
					if current_socket in outputs:
						outputs.remove(current_socket)
					inputs.remove(current_socket)
					current_socket.close()

					# Remove a fila de mensagem
					del message_queues[current_socket]

		# Gerencia saidas
		for current_socket in writable:
			try:
				next_msg = message_queues[current_socket].get_nowait()
			except queue.Empty:
				# Nenhuma mensagem aguardando, logo para de checkar
				outputs.remove(current_socket)
			else:
				current_socket.send(next_msg)

	except KeyboardInterrupt: # Encerra execucao no caso de Ctrl-C
		for current_socket in inputs:
			current_socket.close()
		servent_socket.close()
		sys.exit()
