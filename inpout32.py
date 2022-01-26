'''
Parallel port access by inpout32.dll

Just two calls:

    Inp32(portaddress) -> returns data

    Out32(portaddress, data[0-255])

LPT1 port addresses are 0x378 data, 0x379 status, 0x37a control

Pin No(DB25) Signal name    Direction Register-bit Inverted 
    1           nStrobe         Out     Control-0       Yes 
    2           Data0           In/Out  Data-0          No 
    3           Data1           In/Out  Data-1          No  
    4           Data2           In/Out  Data-2          No  
    5           Data3           In/Out  Data-3          No  
    6           Data4           In/Out  Data-4          No  
    7           Data5           In/Out  Data-5          No  
    8           Data6           In/Out  Data-6          No  
    9           Data7           In/Out  Data-7          No  
    10          nAck            In      Status-6        No  
    11          Busy            In      Status-7        Yes  
    12          Paper-Out       In      Status-5        No  
    13          Select          In      Status-4        No  
    14          Linefeed        Out     Control-1       Yes  
    15          nError          In      Status-3        No  
    16          nInitialize     Out     Control-2       No  
    17          nSelect-Printer Out     Control-3       Yes  
    18-25       Ground

Logic levels look like TTL and suit 3.3V CMOS (put 1k in inputs for safety)

'''

import ctypes

#Example of strobing data out with nStrobe pin (note - inverted)
#Get 50kbaud without the read, 30kbaud with
read = []
for n in range(4):
    ctypes.windll.inpout32.Out32(0x37a, 1)
    ctypes.windll.inpout32.Out32(0x378, n)
    read.append(ctypes.windll.inpout32.Inp32(0x378))   #Dummy read to see what is going on
    ctypes.windll.inpout32.Out32(0x37a, 0)

print read

