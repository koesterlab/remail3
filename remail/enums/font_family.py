from enum import Enum


class FontFamily(str, Enum):
    ARIAL = "Arial"
    ROBOTO = "Roboto"
    GEORGIA = "Georgia"
    COURIER_NEW = "Courier New"
    TIMES_NEW_ROMAN = "Times New Roman"
    VERDANA = "Verdana"
    TAHOMA = "Tahoma"


__all__ = ["FontFamily"]
