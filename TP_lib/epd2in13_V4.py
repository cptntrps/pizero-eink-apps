"""
Adapter for official Waveshare epd2in13_V4 driver
"""
import sys
import os

# Add current directory to path to import epdconfig
sys.path.insert(0, os.path.dirname(__file__))

from . import epdconfig

# Import official driver
class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = 122
        self.height = 250
        self.FULL_UPDATE = 0
        self.PART_UPDATE = 1
        
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)
    
    def ReadBusy(self):
        while(epdconfig.digital_read(self.busy_pin) == 1):
            epdconfig.delay_ms(10)

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xf7)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.ReadBusy()
    
    def TurnOnDisplayPart(self):
        self.send_command(0x22)
        self.send_data(0xff)
        self.send_command(0x20)
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        
        self.send_command(0x45)
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E)
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F)
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
    
    def init(self, mode=None):
        if (epdconfig.module_init() != 0):
            return -1
        
        self.reset()
        
        self.ReadBusy()
        self.send_command(0x12)
        self.ReadBusy() 

        self.send_command(0x01)      
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
    
        self.send_command(0x11)       
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3c)
        self.send_data(0x05)

        self.send_command(0x21)
        self.send_data(0x00)
        self.send_data(0x80)
    
        self.send_command(0x18)
        self.send_data(0x80)
        
        self.ReadBusy()
        
        return 0

    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if(imwidth == self.width and imheight == self.height):
            img = img.convert("1")
        elif(imwidth == self.height and imheight == self.width):
            img = img.rotate(90, expand=True).convert("1")
        else:
            return [0x00] * (int(self.width/8) * self.height)

        buf = bytearray(img.tobytes("raw"))
        return buf
        
    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)  
        self.TurnOnDisplay()
    
    def display_fast(self, image):
        self.send_command(0x24)
        self.send_data2(image) 
        self.TurnOnDisplay_Fast()

    def displayPartial(self, image):
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)  

        self.send_command(0x3C)
        self.send_data(0x80)

        self.send_command(0x01) 
        self.send_data(0xF9) 
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        
        self.send_command(0x24)
        self.send_data2(image)  
        self.TurnOnDisplayPart()

    def displayPartBaseImage(self, image):
        self.send_command(0x24)
        self.send_data2(image)  
                
        self.send_command(0x26)
        self.send_data2(image)  
        self.TurnOnDisplay()
    
    def Clear(self, color=0xFF):
        if self.width%8 == 0:
            linewidth = int(self.width/8)
        else:
            linewidth = int(self.width/8) + 1
        
        self.send_command(0x24)
        self.send_data2([color] * int(self.height * linewidth))  
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)
        self.send_data(0x01)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
        
    def module_exit(self):
        epdconfig.module_exit()
