# Disto Laser Control With Bluez
# Author: Joshua Benjamin & Jackson Benfer
# Written for Python 3.6
#
# Dependencies:
# - You must install the pexpect library, typically with 'sudo pip install pexpect'.
# - You must have bluez installed and gatttool in your path (copy it from the
#   attrib directory after building bluez into the /usr/bin/ location).
#
import struct
import sys
import time
from datetime import datetime
import pexpect

# Get laser address from command parameters (sudo hciconfig lescan).

if len(sys.argv) != 4:
    print('Usage: sudo python laser.py <Address> <Time_Interval_Sec> <Ouput_File_Name>')
    print('Example: sudo python laser.py D3:00:C7:3D:C7:D5 5 output.txt')
    sys.exit(1)
addr = sys.argv[1]
SLEEP_SEC = float(sys.argv[2])
FILENAME = sys.argv[3]

if SLEEP_SEC < 2:
    print('Time_Interval_Sec must be >= 2')
    sys.exit(1)

f = open(FILENAME, "a")

print('File opened')

# Question and answer session

print('Is there anything you wish to say about this trial?')

j = 3
while j == 3:
    noteq = input("Type Yes or No: ").lower()
    if noteq == "yes" or noteq == "y":
        print("Write it down below, then press enter when you're done.")
        notes = input()
        print(notes, file=f)
        j = 1
    elif noteq == "no" or noteq == "n":
        j = 1
    else:
        j = 3

print('Is the laser firing on a floating target?')

fl = 3
while fl == 3:
    tarq = input("Type Yes or No: ").lower()
    if tarq == "yes" or tarq == "y":
        print("What is the difference (D_float) between the height of the water level and the target platform (put ? "
              "if unknown)?. ")
        tar = input("D_float= ")
        unitx = input("what are the units of D_float? ")
        tarr = str(tar)
        unitxx = str(unitx)
        print("D_float = ,%s ,%s " % (tarr, unitxx), file=f)
        print("What is the distance (D_base) from the laser to the bottom of the water column (put ? if unknown)?.")
        tard = input("D_base= ")
        unitz = input("what are the units of D_base? ")
        tarrd = str(tard)
        unitzz = str(unitz)
        print("D_base = ,%s ,%s" % (tarrd, unitzz), file=f)
        print("Note: when performing analysis, make sure to subtract the measurements and D_float from D_base")
        print("Note: when performing analysis, make sure to subtract the measurements and D_float from D_base", file=f)
        fl = 1
    elif tarq == "no" or tarq == "n":
        fl = 1
    else:
        fl = 3

print('Would you like to set a start time?')

now = datetime.now()

z = 3
shour = 250
sminute = 610

while z == 3:
    stimeq = input("Type Yes or No: ").lower()
    if stimeq == "yes" or stimeq == "y":
        print("Set a time")
        shourr = input("Set an hour (24-hour time): ")
        sminutee = input("Set a minute: ")
        shour = int(shourr)
        sminute = int(sminutee)
        print("Note: Measurements will begin automatically once the start time has passed.")
        z = 1
    elif stimeq == "no" or stimeq == "n":
        z = 1
    else:
        z = 3

print('Would you like to set an end time?')

x = 3
emonth = 0
eday = 0
ehour = 0
eminute = 0

while x == 3:
    etimeq = input("Type Yes or No: ").lower()
    if etimeq == "yes" or etimeq == "y":
        print("set the time")
        emonthh = input("set the month: ")
        edayy = input("Set the day: ")
        ehourr = input("Set the hour (24-hour time): ")
        eminutee = input("Set the minute: ")
        emonth = int(emonthh)
        eday = int(edayy)
        ehour = int(ehourr)
        eminute = int(eminutee)
        print("Turn on the laser to begin Measurements")
        print("Note: Measurements will end automatically once the end time has passed.")
        x = 1
    elif etimeq == "no" or etimeq == "n":
        print("Turn on the laser to begin Measurements")
        x = 1
    else:
        x = 3

print('Note: Given measurement units signify most significant unit.')
print('Note: Given measurement units signify most significant unit.', file=f)

# Run gatttool interactively.
gatcmd = 'gatttool -b %s -t random -I' % addr
gatt = pexpect.spawn(gatcmd)

# Connect to the device.
gatt.sendline('connect')
gatt.expect('Connection successful', timeout=120)

print('Connected')

# Enable Indications
gatt.sendline('char-write-cmd 0x000b 0200')
gatt.sendline('char-write-cmd 0x000f 0200')
gatt.sendline('char-write-cmd 0x0012 0200')

print('Indications Enabled')

tim = 3

while tim == 3:
    if now.hour == shour:
        if now.minute == sminute or sminute == 610:
            tim = 1

        else:
            now = datetime.now()
            SLEEP_M = ((sminute - now.minute) * 60) - now.second
            print("Waiting to begin measurements")
            time.sleep(SLEEP_M)
    elif shour != 250:
        now = datetime.now()
        SLEEP_H = ((shour - now.hour) * 3600) - now.minute * 60 - now.second
        print("Waiting for correct hour")
        time.sleep(SLEEP_H)
        now = datetime.now()
    else:
        tim = 1

print('Starting Measurements')

print('Date, Time, Measurement, Unit, DateTime (Use for Spreadsheet Analysis)')
print('Date,Time,Measurement,Unit,DateTime (Use for Spreadsheet Analysis)', file=f)

# Enter main loop.
while True:
    # Take Measurement
    now = datetime.now()

    gatt.sendline('char-write-cmd 0x0014 67')

    gatt.expect('handle = 0x000e value: ')
    gatt.expect('Indication')

    value = gatt.before

    print(value)

    value = value.replace(" ", "")
    value = value[:8]
    a = [value[6], value[7], value[4], value[5], value[2], value[3], value[0], value[1]]
    value = ''.join(a)
    number = struct.unpack('!f', value.decode('hex'))[0]

    gatt.expect('handle = 0x0011 value:')
    gatt.expect('\n')

    unit = gatt.before

    unit = unit.replace(" ", "")
    u = unit[1]

    unitText = "UNKNOWN_UNITS"

    if u == '0':
        unitText = "millimeters"
    elif u == '1':
        unitText = "10th millimeter meters"
    elif u == '2':
        unitText = "centimeters"
    elif u == '3':
        unitText = "10th millimeter"
    elif u == '4':
        unitText = "feet"
    elif u == '5':
        unitText = "feet inch 1/32"
    elif u == '6':
        unitText = "feet inch 1/16"
    elif u == '7':
        unitText = "feet inch 1/8"
    elif u == '8':
        unitText = "feet inch 1/4"
    elif u == '9':
        unitText = "inch"
    elif u == 'a':
        unitText = "inch 1/32"
    elif u == 'b':
        unitText = "inch 1/16"
    elif u == 'c':
        unitText = "inch 1/8"
    elif u == 'd':
        unitText = "feet inch 1/4"
    elif u == 'e':
        unitText = "yard"

    print('%s/%s/%s, %s:%s:%s, %f, %s, %s/%s/%s %s:%s:%s' % (
        now.month, now.day, now.year, now.hour, now.minute, now.second, number, unitText, now.month, now.day, now.year,
        now.hour, now.minute, now.second))
    print('%s/%s/%s,%s:%s:%s,%f,%s,%s/%s/%s %s:%s:%s' % (
        now.month, now.day, now.year, now.hour, now.minute, now.second, number, unitText, now.month, now.day, now.year,
        now.hour, now.minute, now.second), file=f)
    print()
    f.close()

    # gatt.sendline('char-write-cmd 0x0014 6F')

    endcap = 2

    while endcap == 2:
        if now.month == emonth and now.day == eday and now.hour == ehour and now.minute == eminute:
            print("End time reached.")
            sys.exit(1)
        else:
            endcap = 1
    now1 = datetime.now()
    now1 = now1.second - now.second
    time.sleep(SLEEP_SEC - now1)
    f = open(FILENAME, "a")
