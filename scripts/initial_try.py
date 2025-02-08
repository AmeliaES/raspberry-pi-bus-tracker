# -*- coding: utf-8 -*-
import RGB1602
import time
import math
colorR = 64
colorG = 128
colorB = 64

lcd=RGB1602.RGB1602(16,2)

rgb1 = (148,0,110) 
rgb2 = (255,0,255) 
rgb3 = (144,249,15) 
rgb4 = (0,128,60) 
rgb5 = (255,209,0)
rgb6 = (248,248,60)
rgb7 = (80,80,145) 
rgb8 = (255,0,0)
rgb9 = (0,255,0)

rgb_pink = (252, 3, 128)

# set the cursor to column 0, line 1
lcd.setCursor(0, 0)

lcd.printout("Hello world!")
  
lcd.setCursor(0, 1)
  
lcd.printout("    Raspberry Pi")
  
lcd.setRGB(rgb_pink[0],rgb_pink[1],rgb_pink[2]);


    