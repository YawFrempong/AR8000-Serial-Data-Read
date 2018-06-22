import serial
import time
import sys
import struct

def align_serial(ser):

    data = None
    ser.read(1)
    dt = 0
    dt_threshold = 0.005
    while dt < dt_threshold:
        start = time.time()
        ser.read()
        dt = time.time()-start
    ser.read(31)


ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
data = None
status_0 = " "
status_1 = " "
status = " "
try:
    print("Aile  Flap Elev  Rudd Mix  Pot  Thro Status")
    #I assigned mix and pot on the controller to the AUX 1 and 2 channel. By default the controller would send flight mode and gear

    align_serial(ser)
    
    while True:
        data_buf = ser.read(32)
        j1_l, j1_r, j1_d, j1_u, j2_l, j2_r, j2_d, j2_u = False, False, False, False, False, False, False, False

        #check if flight mode changes packet alignment = (3B FF FF FF FF FF FF FF FF FF) maybe different in your case. Check on a serial monitor before hand or just stay on one flight mode
        #gets data and maps it to a range or -0.6 to 0.6 or 1-0 or 0,1,2 depending on the button
        #_hex is just the raw decimal value. Map the value to whatever you want
        if( (((ord(data_buf[22]) << 8) | ord(data_buf[23])) == 15359) and (((ord(data_buf[24]) << 8) | ord(data_buf[25])) == 65535) and (((ord(data_buf[26]) << 8) | ord(data_buf[27])) == 65535) and (((ord(data_buf[28]) << 8) | ord(data_buf[29])) == 65535) and (((ord(data_buf[30]) << 8) | ord(data_buf[31])) == 65535)): #flight mode 1
            
            aile_hex = (ord(data_buf[2]) << 8) | ord(data_buf[3])
            aile = (-1*(float((aile_hex - 2391))/1362)*1.2)+0.6
            
            flap_hex = (ord(data_buf[4]) << 8) | ord(data_buf[5])
            flap = (float(-1*(flap_hex - 11964))/1364)*2

            elev_hex = (ord(data_buf[6]) << 8) | ord(data_buf[7])
            elev = (-1*(float((elev_hex - 4439))/1362.0)*1.2)+0.6

            rudd_hex = (ord(data_buf[8]) << 8) |ord(data_buf[9])
            rudd = (-1*(float((rudd_hex - 6487))/1362.0)*1.2)+0.6

            mix_hex = (ord(data_buf[10]) << 8) | ord(data_buf[11])
            mix = ((-1*(mix_hex - 13994))/(1364))

            pot_hex = (ord(data_buf[18]) << 8) | ord(data_buf[19])
            pot = (float((pot_hex - 41302))/(1364.0))

            thro_hex = (ord(data_buf[20]) << 8) | ord(data_buf[21])
            thro = (-1*(float(thro_hex - 342)/(1364.0))*1.2)+0.6
        
        else:
            
            aile_hex = (ord(data_buf[18]) << 8) | ord(data_buf[19])
            aile = (-1*(float((aile_hex - 2391))/1362)*1.2)+0.6

            flap_hex = (ord(data_buf[20]) << 8) | ord(data_buf[21])
            flap = (float(-1*(flap_hex - 11964))/1364)*2

            elev_hex = (ord(data_buf[22]) << 8) | ord(data_buf[23])
            elev = (-1*(float((elev_hex - 4439))/1362.0)*1.2)+0.6

            rudd_hex = (ord(data_buf[24]) << 8) |ord(data_buf[25])
            rudd = (-1*(float((rudd_hex - 6487))/1362.0)*1.2)+0.6

            mix_hex = (ord(data_buf[26]) << 8) | ord(data_buf[27])
            mix = ((-1*(mix_hex - 13994))/(1364))

            pot_hex = (ord(data_buf[2]) << 8) | ord(data_buf[3])
            pot = (float((pot_hex - 41302))/(1364.0))

            thro_hex = (ord(data_buf[4]) << 8) | ord(data_buf[5])
            thro = (-1*(float(thro_hex - 342)/(1364.0))*1.2)+0.6

        #cast the value to its max/min if wrong calibration causes values over the max or min
        if(aile > 0.6):
            aile = 0.6
            j2_r = True
            j2_l = False

        elif(aile < -0.6):
            aile = -0.6
            j2_r = False
            j2_l = True

                
        if(elev > 0.6):
            elev = 0.6
            j2_d = True
            j2_u = False

        elif(elev < -0.6):
            elev = -0.6
            j2_d = False
            j2_u = True
 
            
        if(rudd > 0.6):
            rudd = 0.6
            j1_r = True
            j1_l = False

        elif(rudd < -0.6):
            rudd = -0.6
            j1_r = False
            j1_l = True

            
        if(thro > 0.6):
            thro = 0.6
            j1_d = True

        data_o = (aile, flap, elev, rudd, mix, pot, thro, status_0, status_1)

        #error system that tells you if you have the wrong calibration. Not really necessary if you just calibrate your controller correctly
        if(j1_l):
            if(j1_l and j1_d):
                status_0 = "Calibrate Joystick 1: Right and Up  "
            elif(j1_l and j1_u):
                status_0 = "Calibrate Joystick 1: Right and Down" 
            else:
                status_0 = "Calibrate Joystick 1: Right         "
        elif(j1_r):
            if(j1_r and j1_d):
                status_1 = "Calibrate Joystick 1: Left and Up   " 
            elif(j1_r and j1_u):
                status_0 = "Calibrate Joystick 1: Left and Down "
            else:
                status_0 = "Calibrate Joystick 1: Left          "
        elif(j1_d):
            status_0 =     "Calibrate Joystick 1: Up            "
        elif(j1_u):
            status_0 =     "Calibrate Joystick 1: Down          "
        else:
            status_0 =     "Null                                "
        if(j2_l):
            if(j2_l and j2_d):
                status_1 = "Calibrate Joystick 2: Right and Up  "
            elif(j2_l and j2_u):
                status_1 = "Calibrate Joystick 2: Right and Down" 
            else:
                status_1 = "Calibrate Joystick 2: Right         "
        elif(j2_r):
            if(j2_r and j2_d):
                status_1 = "Calibrate Joystick 2: Left and Up   " 
            elif(j2_r and j2_u):
                status_1 = "Calibrate Joystick 2: Left and Down "
            else:
                status_1 = "Calibrate Joystick 2: Left          "
        elif(j2_d):
            status_1 =     "Calibrate Joystick 2: Up            "
        elif(j2_u):
            status_1 =     "Calibrate Joystick 2: Down          "
        else:
            status_1 =     "Null                                "

        
        sys.stdout.write("%.1f   %d   %.1f   %.1f   %d   %.1f   %.1f   %s   %s\r"%data_o)

        sys.stdout.flush()

    ser.write(data_buf)
except(KeyboardInterrupt, SystemExit):
    ser.close()
except(Exception) as ex:
    print ex
    ser.close()
