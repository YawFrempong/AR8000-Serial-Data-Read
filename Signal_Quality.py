import serial
import struct
import time
import sys

ser = serial.Serial(port='COM9', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)


val = prev = prev_0 = prev_1 = prev_2 = prev_3 = prev_4 = prev_5 = prev_6 = prev_7 = prev_8 = b' '
packet_received = 0
frame_received = 0 
frame_received_temp_1 = 0
frame_received_temp_2 = 0
frame_diff = 0
frame_loss = 0
frame_loss_temp = 0
frame_total = 0
frame_capture = 0
corrupt_packets = 0
efficiency = 100
predicted_eff = 100
data_o = (0,0,0,0,0,0,0,0)
start = True
time_stamp = True
data = False

print("Sent Frames|Received Frames|Received Packets|Corrupt Packets|Frames Loss|Frames Loss Since Last Packets|Efficiency|Predicted Efficiency")
while True:
        #reads 1 byte at a time & detects the sequence: [3B FF FF FF FF FF FF FF FF FF]
        #then I know that this follows: [sync] [roll] [toggle2] [pitch] [yaw] [kill] [FF FF FF FF] [sync] [pot] [throttle] regradless of flight mode
        #it's only necessary to check once since the pattern will repeat until the controller is turned off or the reciever losses power
        #regradless, the sequence is check every 32 bytes so the data is synced no matter what happens and is more consistent than using time
        
        if(start == True):
                start_time = time.time()
                start = False
                
        if((ord(prev_8) == 59) and (ord(prev_7) == 255) and (ord(prev_6) == 255) and (ord(prev_5) == 255) and (ord(prev_4) == 255) and (ord(prev_3) == 255) and (ord(prev_2) == 255) and (ord(prev_1) == 255) and (ord(prev_0) == 255) and (ord(prev) == 255)):

        #if((prev_8 == "\x3b") and (prev_7 == "\xff") and (prev_6 == "\xff") and (prev_5 == "\xff") and (prev_4 == "\xff") and (prev_3 == "\xff") and (prev_2 == "\xff")  and (prev_1 == "\xff") and (prev_0 == "\xff") and (prev == "\xff
                data_buf = ser.read(22) #reads the rest of the packets
                frame_1_value = (ord(data_buf[1]))
                frame_2_value = (ord(data_buf[17])) 
                packet_received += 1 #counts the total number of packets
                frame_received += 2 #count the total number of frames(2 frames per 32 byte packet)
                frame_received_temp_1 += 2
                frame_received_temp_2 += 2
                
                if(frame_1_value != frame_2_value): #if there is a dropped frame between the start of a packet and the end of a packet then part of that packet is incomplete
                        corrupt_packets += 1
                if(packet_received > 1): #normal state
                        if(frame_1_value < frame_1_old): #byte frame counter ranges from 0-255 and restarts at zero after 255 is reached.                   
                                frame_diff = frame_1_value + (255-frame_1_old)
                        else:
                                frame_diff = frame_1_value - frame_1_old
                        frame_loss += frame_diff #since the frame counter can start from anywhere in the range of 0-255 we simply add the difference between the the first fade byte of the previous packet and the current packet
                        frame_loss_temp += frame_diff
                        frame_total = frame_received + frame_loss
                        
                frame_capture += frame_received_temp_1 + frame_loss_temp        

                if(frame_capture >= 50):
                        efficiency = 100-((float(frame_loss_temp)/frame_capture)*100)
                        frame_received_temp_1 = 0
                        frame_capture = 0
                        frame_loss_temp = 0
                frame_1_old = frame_1_value
                time_stamp = True
                data = True

        if(time_stamp == True):
                wait = time.time()
                time_stamp = False
                
        current = time.time()
        end_time = time.time()

        if((current - wait) >= 2):
                data = False
        if((end_time - start_time) >= 5.4):
                if(data == False):
                        predicted_eff = 0
                else:
                        predicted_eff = frame_received_temp_2
                        frame_received_temp_2 = 0
                        start = True
        
        data_o = (frame_total,frame_received,packet_received,corrupt_packets,frame_loss,frame_diff,efficiency,predicted_eff)
        sys.stdout.write("    %d             %d               %d                %d              %d                  %d                      %d             %d            \r"%data_o)         
        
        val = ser.read(1)
        if(val == b''):
                val = b' '
        prev_8 = prev_7
        prev_7 = prev_6 
        prev_6 = prev_5
        prev_5 = prev_4
        prev_4 = prev_3        
        prev_3 = prev_2
        prev_2 = prev_1
        prev_1 = prev_0
        prev_0 = prev
        prev = val
        #time.sleep(0.5)
        #print(prev,prev_0,prev_1,prev_2,prev_3,prev_4,prev_5,prev_6,prev_7,prev_8)

