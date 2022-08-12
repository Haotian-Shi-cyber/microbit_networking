from microbit import *
import random
import radio
import math
import microbit

# convert decimal to binary for message
def decimal_to_binary(msgnum):
    b = ''
    while True:
        s = msgnum // 2
        y = msgnum % 2
        b = b + str(y)
        if s == 0:
            break
        msgnum = s
    # if it is less than 5 bit, make it 5 bit then by adding 0
    len_b = 5
    while len(b) < len_b:
        b = b + '0'
    # b now is binary repre of msgnum
    # remember the order is reversed
    return b

#  convert decimal to binary for id address
def Id_decimal_to_binary(id):
    b = ''
    while True:
        s = id // 2
        y = id % 2
        b = b + str(y)
        if s == 0:
            break
        id = s
    # if it is less than 5 bit, make it 5 bit then by adding 0
    len_b = 4
    while len(b) < len_b:
        b = b + '0'
    # b now is binary repre of msgnum
    # remember the order is reversed
    return b    
    
# convert binary to decimal
def binary_to_decimal(msgnum):
    # convert to decimal
    b = 0
    for x in range(5):
        try:
            num = int(msgnum[x])
            b = b + num * pow(2,x)
        except:
            break;
        
    # display.scroll(str(b))
    return b

# calculate parity bit
def cal_parity(a):
    count = 0
    for x in a:
        if x == '1':
            count = count + 1
    bits = decimal_to_binary(count)
    # get bits[0] because reverse order
    parity = bits[0]
    return parity
   
# radio on
radio.on()
radio.config(power=0)

lastmsg = "A"

sent_parity_bit = 0
received_parity_bit = 0
cal_parity_bit = 0
msgnum = 1
myId = 1
destId = 2

# send message through radio or wires
while True:
    display.clear()
    if button_a.is_pressed():
        
        #random letter
        msgnum = msgnum + random.randint(1,25)
        if msgnum > 26:
            msgnum = msgnum - 26
        msgbody = "%c" % (msgnum + 64)

        #decode to binary for wire transmition
        decoded_value1 = decimal_to_binary(msgnum)
        display.show(msgbody)
        sleep(1500)
        lastmsg = msgbody
        wired_message = decoded_value1

        #calculate parity bit
        sent_parity_bit = cal_parity(decoded_value1)

        # radio final message
        radio_message = str(destId) + msgbody + str(sent_parity_bit)

        # wire final message, no parity bit since it is checked in the function
        wire_message = str(destId) + msgbody
        
        ###
        #send through radio
        radio.send(radio_message)
        sleep(300)
        ###
        
        ###
        #send through wires, suppose we want to recreate rs232 asynchronous protocol, use uart module
        #initialise parameters
        microbit.uart.init(parity=uart.EVEN, tx=pin1, rx=pin2)
        uart.write(wire_message)
        ###
        
    # system parameters setup
    # tilting left to setup myId address
    if accelerometer.get_x() < -500:
        display.show(str(myId))
        if button_b.is_pressed():
            myId = myId + 1
            if myId == 10:
                myId = 1
            display.show(str(myId))
            sleep(100)
    
    # tilting right to setup destId address
    if accelerometer.get_x() > 500:
        display.show(str(destId))
        if button_b.is_pressed():
            destId = destId + 1
            if destId == 10:
                destId = 1
            display.show(str(destId))
            sleep(100)
            
    # receive message through radio
    msgin = radio.receive()
    if msgin is not None:
        display.scroll(msgin)
        msgdest = int(msgin[0])
        msgbody = msgin[1]
        received_parity_bit = int(msgin[2])
        # calculate parity from received msgbody
        value = ord(msgbody) - 64
        decoded_value2 = decimal_to_binary(value)
        cal_parity_bit = cal_parity(decoded_value2)
        # if destination matches our Id and parity bit matches
        if msgdest == myId and int(cal_parity_bit) == received_parity_bit:
            display.show(msgbody)
            sleep(1500)
        else:
            # destination is not me, forward it
            if msgbody[0] is not lastmsg[0]:
                lastmsg = msgbody
                # try to send it through wire
                ###
                send_msg = str(msgdest) + msgbody
                microbit.uart.init(parity=uart.EVEN, tx=pin1, rx=pin2)
                uart.write(send_msg)
                ###
        
    # read pin2
    # receive message from uart
    if uart.any():
        msgin = uart.read()
        msgin_str = str(msgin,'UTF-8')
        rec_msgbody = msgin_str[1]
        if int(msgin_str[0]) == myId:
            display.show(rec_msgbody)
            sleep(1500)
        else:
	# id doesn’t match
            # add parity for radio
            # need to convert it to binary first
            value = ord(rec_msgbody) - 64
            value = decimal_to_binary(value)
            msgin_radio = msgin_str + cal_parity(value)
            display.scroll(msgin_radio)
            radio.send(str(msgin_radio))
