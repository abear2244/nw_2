import socket
import json
import argparse
import logging
import select
import struct
import time



def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', 
        dest="port", 
        type=int, 
        default='9999',
        help='port number to listen on')
    parser.add_argument('--loglevel', '-l', 
        dest="loglevel",
        choices=['DEBUG','INFO','WARN','ERROR', 'CRITICAL'], 
        default='INFO',
        help='log level')
    args = parser.parse_args()
    return args


## straght -- change this for sure  but this makes sense i would say 
def broadcast_message(source, message, clientList):
    for client in clientList:
        if client != source:
            try:
                client.send(message)
            except:
                client.close()
                clientList.remove(client)

def main():

    args = parseArgs()      

    # set up logging
    log = logging.getLogger("myLogger")
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    level = logging.getLevelName(args.loglevel)
    log.setLevel(level)
    log.info(f"running with {args}")
    
    log.debug("waiting for new clients...")   ## do u need this ???


    serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSock.bind(("",args.port))
    serverSock.listen()

    clientList = []

  
    try:
        while True:
            read_sockets, _, _ = select.select(clientList, [], [])
            for c_socket in read_sockets:
                if c_socket is serverSock:
                    client_sock, address = serverSock.accept()
                    log.info(f"New connection: {address}")
                    clientList.append(client_sock)
                else:
                    try:
                        packedLen = c_socket.recv(4, socket.MSG_WAITALL)
                        if not packedLen:
                            log.info("Client disconnected")
                            clientList.remove(c_socket)
                            c_socket.close()
                            continue
                        len = struct.unpack("!L", packedLen)[0]
                        jsonData = c_socket.recv(len, socket.MSG_WAITALL)
                        broadcast_message(c_socket, packedLen + jsonData, clientList)
                    except Exception as e:
                        log.error(f"Error receiving message: {e}")
                        clientList.remove(c_socket)
                        c_socket.close()
    except KeyboardInterrupt:
        log.info("Server shutting down...")
    except Exception as e:
        log.error(f"Unexpected error: {e}")
    finally:
        serverSock.close()
        for client in clientList:
            client.close()
        log.info("All sockets closed, server terminated.")


      

if __name__ == "__main__":
    exit(main())

