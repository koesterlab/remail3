from enum import Enum


class FontFamily(str, Enum):
    """Enum for font families."""

    ARIAL = "Arial"
    ROBOTO = "Roboto"
    GEORGIA = "Georgia"
    COURIER_NEW = "Courier New"
    TIMES_NEW_ROMAN = "Times New Roman"
    VERDANA = "Verdana"
    TAHOMA = "Tahoma"
