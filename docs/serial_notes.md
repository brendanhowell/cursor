# Some Tips for Serial Ports

on linux you can set the serial port with `stty`

`stty -F /dev/ttyS0 1200 cs8 -cstopb -parenb`

Note: you may have to run this again if the port is reset after your command or program runs
