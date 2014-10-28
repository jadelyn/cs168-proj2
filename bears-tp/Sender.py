import sys
import getopt
import time

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
        self.packets = {} # dictionary containing packets mapped to their sequence numbers
        self.acks = {} # dict mapping # acks per seq number
        self.lastSeqNo = float("inf")-1
        self.base = None
        self.N = 5
        self.dataSize = 1300

    # Main sending loop.
    def start(self):
        initialSeqNo = 0
        print self.packets
        
        startData = self.infile.read(self.dataSize)
        firstPacket = self.make_packet("start", initialSeqNo, startData)
        self.packets[0] = firstPacket
        self.send(firstPacket)
        startTime = time.clock()
        while (True):
            response = self.receive(.5 - (time.clock()-startTime))
            if response is None:
                self.send(firstPacket)
                startTime = time.clock()
            elif Checksum.validate_checksum(response):
                break

        self.base = 1
        

        for i in range(1, self.N):
            data = self.infile.read(self.dataSize)
            if len(data) < self.dataSize:
                packet = self.make_packet("end", i, data)
                self.packets[i] = packet
                self.lastSeqNo = i
                self.send(packet)
                break
            else:
                packet = self.make_packet("data", i, data)
                self.packets[i] = packet
                self.send(packet)
        startTime = time.clock()

        while True:
            receivedPacket = self.receive(.5 - (time.clock() - startTime))
            if receivedPacket is None:
                self.handle_timeout()
            elif not Checksum.validate_checksum(receivedPacket):
                pass
            else:
                msgType, seqNoStr, data, checkSum = self.split_packet(receivedPacket)
                seqNo = int(seqNoStr)
                if seqNo == self.lastSeqNo+1:
                    break
                if not seqNo in self.acks:
                    self.acks[seqNo] = 1
                    self.handle_new_ack(seqNo)
                else:
                    self.acks[seqNo] += 1
                    self.handle_dup_ack(seqNo)

    def handle_timeout(self):
        if self.lastSeqNo < self.base+self.N-1:
            for i in range(self.base, self.lastSeqNo+1):
                self.send(self.packets[i])
        else:
            for i in range(self.base, self.base+self.N):
                self.send(self.packets[i])

    def handle_new_ack(self, ack):
        msgType = None
        if ack == self.base + 1:
            del self.packets[self.base]
            self.base += 1

        elif ack > self.base + 1: 
            for i in range(self.base, ack):
                del self.packets[i]
            oldBase = self.base
            self.base = ack 
            for i in range(oldBase+self.N-1, self.base+self.N):
                thisPacketsData = self.infile.read(self.dataSize)
                if len(thisPacketsData) < self.dataSize:
                    self.lastSeqNo = i
                    thisPacket = self.make_packet("end", i, thisPacketsData)
                    packets[i] = thisPacket
                    startTime = time.clock()
                    self.send(thisPacket)
                    break
                else:
                    thisPacket = self.make_packet("data", i, thisPacketsData)
                    packets[i] = thisPacket
                    startTime = time.clock()
                    self.send(thisPacket)

      

    def handle_dup_ack(self, ack):
        if self.acks[ack] > 3:
            if self.lastSeqNo < self.base+self.N-1:
                for i in range(self.base, self.lastSeqNo+1):
                    self.send(self.packets[i])
            else:
                for i in range(self.base, self.base+self.N):
                    self.send(self.packets[i])


    def log(self, msg):
        if self.debug:
            print msg


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
