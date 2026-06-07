from __future__ import annotations
import re
# import io
import enum
import numpy as np

def dotAndCommaSci(string: str) -> bool:
    if re.match(r"^[+-]?(?:0|[1-9]\d*)(?:[\,\.]\d*)?(?:[eE][+\-]?\d+)$",string)==None:
        return False
    else:
        return True

def dotAndCommaDcm(string: str) -> bool:
    if re.match(r"^\d*[.,]?\d*$",string)==None:
        return False
    else:
        return True

def checkDecimal(string: str) -> bool:
    try:
        float(string)
        return True
    except(ValueError,TypeError):
        return False

def checkInt(string: str) -> bool:
    try:
        int(string)
        return True
    except(ValueError,TypeError):
        return False

def checkInvCultInt(string: str) -> bool:
    if (re.match(r'^(\d+|\d{1,3}(,\d{3})*)(\.\d+)?$',string)!=None):
        string=string.replace(',','')
    return checkInt(string)

def checkWholeNum(string: str) -> bool:
    if(checkDecimal(string)):
        temp=float(string)
        if temp.is_integer():
            return True
        else:
            return False
    else:
        return False

def checkHex(string: str) -> bool:
    try:
        int(string,16)
        return True
    except(ValueError,TypeError):
        return False

class TypeEnum(enum.Enum):
    Int32=0
    Int64=1
    UInt32=2

def checkConvertType(inputValue, typeEnum: TypeEnum) -> bool:
    if typeEnum ==0:
        try:
            np.int32(inputValue)
            return True
        except:
            return False
    elif typeEnum==1:
        try:
            np.int64(inputValue)
            return True
        except:
            return False

    elif typeEnum == 2:
        try:
            np.uint32(inputValue)
            return True
        except:
            return False

