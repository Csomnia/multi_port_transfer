import socket
import threading
import os
import time


PER_SEND_SIZE = 10240


def cut_file(file_name, parts):

    file_size = os.path.getsize(file_name)
    chunk_size = (file_size / parts) + (file_size % parts)

    file_dict = {}
    f = open(file_name, 'rb')
    file_no = 0
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        file_dict[file_no] = chunk
        file_no += 1
    f.close()
    return file_dict


def merge_file(cut_dict, file_name='timg.jpg'):
    file_parts = len(cut_dict.keys())
    f = open(file_name, 'wb')
    for i in range(file_parts):
        f.write(cut_dict[i])
    f.flush()
    f.close()
    return


class EventHandler:
    def fileno(self):
        raise NotImplemented('must implement')

    def want_to_receive(self):
        pass

    def handle_receive(self):
        pass

    def want_to_send(self):
        pass

    def handle_send(sel):
        pass


class multiPortServer(EventHandler):

    def __init__(self, address, data):
        self.data = data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(address)

    def fileno(self):
        return self.sock.fileno()

    def wants_to_send(self):
        return self.data > 0

    def handle_send(self):
        #send_size = self.sock.sendto(, addr)
        self.data = self.data[send_size:]


class subServer(threading.Thread):
    def __init__(self, addr, data, remo_addr, file_part):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)
        self.data = data
        self.addr = addr
        self.remo_addr = remo_addr
        self.file_part = file_part
        self.counter = 0

    def run(self):
        # send part number for client threads.
        # while True:
        #     self.sock.sendto("PART:"+str(self.file_part))
        #     msg, addr = self.sock.recvfrom(4)
        #     if msg == 'ack':
        #         break

        # start file part transfer.
        while len(self.data) > 0:
            send_size = self.sock.sendto(self.data[:PER_SEND_SIZE], self.remo_addr)
            self.counter += 1
            self.data = self.data[send_size:]
            #time.sleep(0.001)
            
        # send ending mark.

        self.sock.sendto('EOFPART', self.remo_addr)
        self.sock.close()

        
class mainServer:
    def __init__(self, local_addr, local_ports):
        self.local_addr = local_addr
        self.local_ports = local_ports
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(local_addr)

    def start(self):
        
        self.ports = []
        while True:
            ports, remo_addr = self.sock.recvfrom(1024)
            print('server recv port : ', ports)
            self.ports = [int(i) for i in ports.split()]
            if self.ports:
                self.sock.sendto('server_kenw_ports', addr)
                break

        dataset = cut_file('timg.jpg', len(self.ports))

        ths = []
        for i in range(len(self.ports)):
            port = self.ports[i]                # port that subServer send to
            local_port = self.local_ports[i]   # port that subServer bind to
            t = subServer(('', local_port), dataset[i], (remo_addr[0], port), i)
            #t.setDaemon(True)
            ths.append(t)

        while True:
            msg, addr = self.sock.recvfrom(1024)
            if msg == 'client_ready':
                break

        for i in ths:
            i.start()
        for i in ths:
            i.join()

if __name__ == '__main__':
    test = mainServer(('', 14000), [13001, 13002, 13003, 13004])
    test.start()
