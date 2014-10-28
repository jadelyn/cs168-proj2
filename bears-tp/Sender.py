import sys
import getopt

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
        packets = {} # dictionary containing packets mapped to their sequence numbers
        acks = {} # dict mapping # acks per seq number


    # Main sending loop.
    def start(self):
        initialSeqNo = 0
        N = 5
        dataSize = 1300
        startData = self.infile.read(dataSize)
        firstPacket = self.make_packet("start", initialSeqNo, startData)
        self.send(firstPacket)
        startTime = time.clock()
        while (True):
            response = self.receive(.5 - (time.clock()-startTime))
            if response is None:
                self.send(firstPacket)
                startTime = time.clock()
            elif Checksum.validate_checksum(response):
                break

        base = 1

        for i in range(1, N):
            data = self.infile.read(dataSize)
            if len(data) < dataSize:
                packet = self.make_packet("end", i, data)
                self.send(packet)
                break
            else:
                packet = self.make_packet("data", i, data)
                self.send(packet)
        startTime = time.clock()

        while True:
            receivedPacket = self.receive(.5 - (time.clock() - startTime))
            if receivedPacket is None:
                self.handle_timeout()
            elif not Checksum.validate_checksum(receivedPacket):
                pass
            else:
                msgType, seqNo, data, checkSum = self.split_packet(receivedPacket)
                if not seqNo in acks:
                    acks[seqNo] = 1
                    self.handle_new_ack(seqNo)
                else:
                    acks[seqNo]++
                    self.handle_dup_ack(seqNo)




    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        msgType = None
        if seqNo == base + 1:
            packets.remove(base)
            base++

        else if seqNo > base + 1: 
            for i in range(base, seqNo-1):
                packets.remove(i)
            base = seqNo 

        thisPacketsData = self.infile.read(dataSize)
        if len(thisPacketsData) < dataSize:
            msgType = "end"
        else:
            msgType = "data"
        thisPacket = self.make_packet(msgType, base + N - 1, thisPacketsData)
        packets[base+N-1] = thisPacket
        self.send(thisPacket)
        startTime = time.clocK()


    def handle_dup_ack(self, ack):
        pass

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
