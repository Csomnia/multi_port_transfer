import socket
import select

# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.bind(('localhost', 13009))
# while True:
#     data, addr = s.recvfrom(8192)
#     print(data, addr)


def merge_file(cut_dict, file_name='merge.txt'):
    file_parts = len(cut_dict.keys())
    f = open(file_name, 'wb')
    for i in range(file_parts):
        f.write(cut_dict[i])
    f.flush()
    f.close()
    return


def event_loop(handlers):
    while True:
        # print 'in loop'
        want_recv = [h for h in handlers if h.wants_to_receive()]
        want_send = [h for h in handlers if h.wants_to_send()]
        if not want_recv:
            break
        can_recv, can_send, _ = select.select(want_recv, want_send, [])
        for h in can_recv:
            h.handle_receive()

        # if can_send:
        #     for h in can_send:
        #         h.handle_send()
        # else:
        #     break
        # for i in handlers:
        #     print("part :", i.part, "recv: ", i.counter)
    return


class EventHandler:
    def fileno(self):
        raise NotImplemented('must implement')

    def wants_to_receive(self):
        return False

    def handle_receive(self):
        pass

    def wants_to_send(self):
        return False

    def handle_send(self):
        pass


class UDPClient(EventHandler):
    def __init__(self, addr, part):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)
        self.part = part
        self.recv_flag = True
        self.data = ''
        self.counter = 0
        
    def fileno(self):
        return self.sock.fileno()

    def wants_to_receive(self):
        return self.recv_flag

    def handle_receive(self):
        data, addr = self.sock.recvfrom(10240)
        print(data)
        self.counter += 1
        if data.startswith("EOFPART"):
            print("done with part %s" % self.part)
            # self.sock.close()
            self.recv_flag = False
        else:
            self.data += data


class mainClient:
    def __init__(self, remote_addr, local_ports):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_addr = remote_addr
        self.local_ports = local_ports

    def start(self):

        ports_info = ' '.join(str(i) for i in self.local_ports)
        while True:
            self.sock.sendto(ports_info, self.remote_addr)
            msg, addr = self.sock.recvfrom(10240)
            if msg == 'server_kenw_ports':
                break

        clients_list = []
        for i in range(len(self.local_ports)):
            print("para: ", self.remote_addr, self.local_ports[i])
            new_client = UDPClient(('localhost', self.local_ports[i]),
                                   i)
            clients_list.append(new_client)

        self.sock.sendto('client_ready', self.remote_addr)

        event_loop(clients_list)
        merge_dict = {}
        for i in clients_list:
            # print i.data
            merge_dict[i.part] = i.data

        merge_file(merge_dict, file_name='remo.txt')


if __name__ == '__main__':
    receive_ports_list = [14001, 14002, 14003, 14004]
    test = mainClient(('localhost', 14000), receive_ports_list)
    test.start()
