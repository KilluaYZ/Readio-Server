import inspect
def printException(e):
    print(f"[ERROR]{__file__}::{inspect.getframeinfo(inspect.currentframe().f_back)[2]} \n {e}")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError,ValueError):
        pass
    return False

def checkRequestSingleKeyWithCondition(req:dict, keyName:str, condition:str) -> bool:
    """
    取出req[keyName], 其值会被替代为condition中的#?#检查
    """
    try:
        if keyName not in req:
            raise Exception("key不存在")
        val = req[keyName]
        condition = condition.replace("#?#",f"{val}")
        return eval(condition)

    except Exception  as e:
        printException(e)
        return False

def checkRequestMultipleKeysWithCondition(req:dict, keyNameList:list, condition:str) -> list:
    res = []
    for keyName in keyNameList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res

def checkRequestMultipleKeysWithCondition(req:dict, keyDefineList:list) -> list:
    res = []
    for keyName, condition in keyDefineList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res


def checkRequstIsNotNone(req:dict, keyName:str):
    if keyName not in req:
        return False
    
    if req[keyName] is None:
        return False
    
    return True


#req = {"name":"ziyang","phoneNumber":"18314266702","age":18}
#print(checksRequestSingleKeyWithCondition(req,"name","'#?#' < 20"))
#print(checksRequestSingleKeyWithCondition(req,"age","#?# < 20"))
#print(checksRequestSingleKeyWithCondition(req,"name","'#?#' == 'ziyang'"))
#print(checksRequestSingleKeyWithCondition(req,"name","'#?#' != None and len('#?#') > 5 and len('#?#') < 13"))

