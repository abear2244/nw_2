"""
A skeleton from which you should write your client.
"""


import socket
import json
import argparse
import logging
import select
import sys
import time
import datetime
import struct

from message import UnencryptedIMMessage


def parseArgs():
    """
    parse the command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', 
        dest="port", 
        type=int, 
        default='9999',
        help='port number to connect to')
    parser.add_argument('--server', '-s', 
        dest="server", 
        required=True,
        help='server to connect to')       
    parser.add_argument('--nickname', '-n', 
        dest="nickname", 
        required=True,
        help='nickname')                
    parser.add_argument('--loglevel', '-l', 
        dest="loglevel",
        choices=['DEBUG','INFO','WARN','ERROR', 'CRITICAL'], 
        default='INFO',
        help='log level')
    args = parser.parse_args()
    return args


def main():
    args = parseArgs()

    # set up the logger
    log = logging.getLogger("myLogger")
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    level = logging.getLevelName(args.loglevel)
    
    log.setLevel(level)
    log.info(f"running with {args}")
    
    log.debug(f"connecting to server {args.server}")
    try:
        s = socket.create_connection((args.server,args.port))     ##b what does this do 
        log.info("connected to server")
    except:
        log.error("cannot connect to server")
        exit(1)

    # here's a nice hint for you...  what does this mean???  yes wtf is this dude
    readSet = [s] + [sys.stdin]

    while True:

        read_sockets, dummy_w, dummy_x = select.select(readSet, [], [])

        for socket in read_sockets:

            if socket is s:
                
                try:
                    
                    msg_len = s.recv(4, socket.MSG_WAITALL)

                    if not msg_len: ## should i change this duder ??  so can change this to somehtign else, but fine foe now
                        log.error("server closed, not proper len")
                        sys.exit(1)

                    int_len = struct.unpack("!L", msg_len)[0]

                    j_data = s.recv(int_len, socket.MSG_WAITALL).decode('utf-8')

                    msg = UnencryptedIMMessage()

                    msg.parseJSON(j_data)

                    print(msg)

                except Exception as e:

                    log.error(f"error in receiving msg: {e}")
                    sys.exit(1)  ## what is this, and how to exit 

            elif socket is sys.stdin:

                msg_text = sys.stdin.readline().strip()

                if msg_text == '':
                    print("input closed, exiting")
                    sys.exit(0)

                if msg_text:  ## what if not msg text - how do i accont for that other shit , honestley could get rid of this for int purpioses 

                    msg = UnencryptedIMMessage(args.nickname, msg_text)
                    packedSize, jsonData = msg.serialize()
                    s.sendall(packedSize + jsonData)


        

if __name__ == "__main__":
    exit(main())

