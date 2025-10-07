import escpos.printer
from escpos.escpos import Escpos
import os

from typing import Literal, TypedDict

class PrinterConfig(TypedDict):
    line_width: int
    x_offset: int
    x_margin: int
    y_offset: int
    y_margin: int


class TextConfig(TypedDict):
    size: int
    bold: bool
    underline: bool
    align: Literal["left", "center", "right"]


class BasePrinter(Escpos):
    __DEFAULT_CONFIG = {
        "line_width": 999,
        "x_offset": 0,
        "x_margin": 0,
        "y_offset": 0,
        "y_margin": 0,
    }
    __DEFAULT_TEXT_CONFIG = {"size": 1, "underline": False, "align": "left"}

    def __init__(self, config: PrinterConfig = None):
        if config is None:
            config = BasePrinter.__DEFAULT_CONFIG
        config = {**BasePrinter.__DEFAULT_CONFIG, **config}
        self.config = config

        # self.set(custom_size=True,align='left',bold=False,underline=False,height=1,width=1)

    def __update_config(self, config: PrinterConfig):
        self.config = {**self.config, **config}

    def raw_print(self):
        pass

    def bar(self):
        self.line(
            "="
            * int(
                self.config["line_width"]
                - (self.config["x_margin"] + self.config["x_offset"])
            )
        )

    def line(self, text: str = "", text_config: TextConfig = None):
        if text_config is None:
            text_config = BasePrinter.__DEFAULT_TEXT_CONFIG

        sz = text_config.get("size", 1)
        lspace = " " * int((self.config["x_margin"] + self.config["x_offset"]) / sz)
        # max_width = int(self.config["line_width"] / sz)
        max_width = int(
            (
                self.config["line_width"]
                - (self.config["x_margin"] + self.config["x_offset"])
            )
            / sz
        )

        text = text.strip()
        if len(text) - 1 > max_width:
            print("WARNING: txt to long")
        text = text[:max_width]

        self.set(custom_size=True, width=sz, height=sz, underline=False)
        # self.text(text+"\n")
        # return

        if text_config.get("align") == "left":
            # self.text(lspace + text + "\n")
            self.text(lspace)
            self.set(
                custom_size=True,
                width=sz,
                height=sz,
                underline=text_config.get("underline", False),
            )
            self.text(text + "\n")

        if text_config.get("align") == "center":
            space = (max_width - len(text)) // 2
            self.text(" " * space + lspace)
            self.set(
                custom_size=True,
                width=sz,
                height=sz,
                underline=text_config.get("underline", False),
            )
            self.text(text + "\n")

        if text_config.get("align") == "right":
            space = max_width - len(text)
            self.text(" " * space + lspace)
            self.set(
                custom_size=True,
                width=sz,
                height=sz,
                underline=text_config.get("underline", False),
            )
            self.text(text + "\n")


class USBPrinter(escpos.printer.Usb, BasePrinter):
    def __init__(self, venderID=0x483, productID=0x5743, config: PrinterConfig = None):
        super().__init__(venderID, productID)
        BasePrinter.__init__(self, config)

        self.close()

        self.__usb_args = {"idVendor": venderID, "idProduct": productID}

    def connect(self):
        self.open(self.__usb_args)
        return self


class NETPrinter(escpos.printer.Network, BasePrinter):
    def __init__(self, host, port = 9100, timeout = 0.5, config: PrinterConfig = None):
        super().__init__(host, port, timeout)
        BasePrinter.__init__(self, config)

        self.close()

    def connect(self):
        self.open()
        return self


class SERPrinter(escpos.printer.Serial, BasePrinter):
    pass

class FilePrinter(escpos.printer.File, BasePrinter):
    class FilePrinterNotFound(Exception): 
        def __str__(self): return "Printer not found"    
    class FilePrinterNoAccess(Exception): 
        def __str__(self): return "Can't access pritner"    

    def __init__(self, file='/dev/usb/lp0', config:PrinterConfig = None):
        # super().__init__(file)
        Escpos.__init__(self)
        self.devfile = file
        self.auto_flush = False
        BasePrinter.__init__(self, config)

        self.close()
    
    def open(self):
        exists = os.path.exists(self.devfile)
        if not exists: raise FilePrinter.FilePrinterNotFound

        self.device = open(self.devfile, "wb") 
        if self.device is None: raise FilePrinter.FilePrinterNoAccess

    # def close(self):
    #     super().close()
    #     self.devfile = None


if __name__ == "__main__":
    p = FilePrinter()
    p.open()
    p.line("=====")
    p.line("✓, ✔, ∨, √")
    p.line("x, ×, ⓧ")
    p.line(" ☒ ☑ ")

    p.cut()
    p.close() 
    # p.open()
    # p.open()
