import math
VERSION = 1
#opcode
reserved = ["LET", "PRINT", "INPUT", "IF", "GOTO",
            "SLEEP", "END", "LIST", "REM", "READ",
            "WRITE", "APPEND", "RUN", "CLS", "CLEAR",
            "EXIT", "SAVE", "LOAD", "GOSUB", "RETURN"] #new save、load、gosub、return
#operand下面的優先度高(^^是xor)           
operators = [["==", "!=", ">", "<", ">=", "<="],
             ["."],
             [">>", "<<"],
             ["+", "-"],
             ["*", "/", "&", "|", "%", "^^"], 
             ["^"]] #new << >> ^^
#math function *24           
mathfunction = ["SIN","COS","TAN","SINH","COSH","TANH",
                "ASIN","ACOS","ATAN","ASINH","ACOSH","ATANH",
                "DEG","RAD","FLOOR","CEIL","ROUND","ABS",
                "EXP","LN","LOG10","LOG2","SQRT","FACT"] #new mathfunction
lines = {} #全部的command
maxLine = 0 #總長度
linePointer = 0
stopExecution = False
identifiers = {} #變數表
printReady = True
returnLine = []

def main():
    print(f"Tiny BASIC version {VERSION}\nby Chung-Yuan Huang")
    while True:
            try:
                if printReady:
                    print("OK.")
                nextLine = input() #input
                if len(nextLine) > 0: #有input
                    executeTokens(lex(nextLine)) #lex切割input再執行token
            except KeyboardInterrupt: #??
                pass
            except SystemExit: #離開系統
                print("Bye!")
                break
            except: #error
                print("Execution halted.")

def is_number(s): #是不是數字?
    try:
        float(s)
        return True
    except ValueError:
        return False

def getVarType(token): #取得型態?
    if len(token) > 1:
        if token[-1] == "$": #字串
            return "STRING"
    return "NUM"

def isValidIdentifier(token): #是不是變數?
    if len(token) == 0:
        return False
    if len(token) > 1:
        if token[-1] == "$": #判斷字串
            token = token[0:-1]
    if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz"): #第一碼為英文
        return False
    for c in token[1:]: #第一碼之後的字
        if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz0123456789"): #英文或數字
            return False
    return True
    
def lex(line): #分割command,一次讀一行
    #input: 10 let x = 1
    #input: 20 print "hello"
    inString = False
    tokens = []
    currentToken = ""
    line = line + " "
    for c in line: #分隔讀,一次讀一個
        if not(inString) and c in " ()\"": #讀到空格?
            if len(currentToken) != 0: #有currenttoken
                tokens.append([currentToken, "TBD"])
                #tokens[[10,TBD],[let,TBD],[x,TBD],[=,TBD],[1,TBD]]
                currentToken = ""
            if c == '"': #讀到字串開頭"
                inString = True
        elif inString and c == '"': #讀到字元結尾"
            tokens.append([currentToken, "STRING"])
            #tokens[[20,TBD],[print,TBD],[hello,STRING]]
            currentToken = "" #清空currenttoken
            inString = False
        else:
            currentToken += c

    for token in tokens: #讀每個tokens
        if token[1] != "TBD": #定義過的跳過
            continue
        value = token[0]
        if is_number(value): #是數字
            token[0] = float(token[0]) 
            token[1] = "NUM" #定義為Number
        elif value.upper() in reserved: #是保留的大寫
            token[0] = value.upper()
            token[1] = "RESVD" #定義為Reserved word
        elif value.upper() in mathfunction: 
            token[0] = value.upper()
            token[1] = "MATHF" 
#new 
        elif value.upper() == "ELSE": #是else
            token[0] = value.upper()
            token[1] = "ELSE" #定義為ELSE
        elif value.upper() == "THEN": #是then
            token[0] = value.upper()
            token[1] = "THEN" #定義為THEN
#end
        elif value == "=": #是等於符號
            token[1] = "ASGN" #定義為ASGN
        elif isValidIdentifier(token[0]): #是變數(ex:a,b,a0,a1)
            token[1] = "ID" #定義為Identifier
        else:
            for i in range(0, len(operators)): #是其他運算符號
                if token[0] in operators[i]:
                    token[1] = "OP" #定義為OP
        #tokens[[10,NUM],[let,RESVD],[x,ID],[=,ASGN],[1,NUM]]
        #tokens[[20,NUM],[print,RESVD],[hello,STRING]]
    return tokens

def executeTokens(tokens): #判斷opcode type
    global lines, maxLine, stopExecution, linePointer, printReady
    printReady = True
    #如果有行號，取出行號
    if tokens[0][1] == "NUM": #行號
        lineNumber = int(tokens.pop(0)[0]) #取出行號
        if len(tokens) != 0:
            lines[lineNumber] = tokens #把指令放入對應的行號
            if lineNumber > maxLine: #update maxline
                maxLine = lineNumber
        else:
            lines.pop(lineNumber, None) #刪除行號中的指令(格式不符)
        printReady = False
        return
    #判讀行號後第一個指令
    if tokens[0][1] != "RESVD": #不是opcode
        print(f"Error: Unknown command {tokens[0][0]}.") 
    else:
        command = tokens[0][0] #command=opcode
        if command == "REM": #保留?
            return
        elif command == "CLS": #enter*500
            print("\n"*500)
        elif command == "END": #end
            stopExecution = True
        elif command == "EXIT": #exit program
            quit()
        elif command == "CLEAR": #clear all command
            maxLine = 0
            lines = {}
            identifiers = {} 
        elif command == "LIST": #show all command
            i = 0
            while i <= maxLine:
                if i in lines: #對應的行號
                    line = str(i)
                    for token in lines[i]: #從lines[i]讀指令到token變數
                        tokenVal = ""
                        if token[1] == "NUM": #讀到數字型態
                            tokenVal = getNumberPrintFormat(token[0]) #tokenval=行號(int type)
                        elif token[1] == "STRING": #讀到字串型態
                            tokenVal = f"\"{token[0]}\""
                        else:
                            tokenVal = token[0] #tokenval=值
                        line += " " + str(tokenVal) #line紀錄一整行寫了甚麼
                    print(line)
                i = i + 1
        elif command == "PRINT": #print "hello"
            if not(printHandler(tokens[1:])): stopExecution = True #print完結束
        elif command == "LET": #let x = 10
            if not(letHandler(tokens[1:])): stopExecution = True #完成定義變數
        elif command == "INPUT": #input
            if not(inputHandler(tokens[1:])): stopExecution = True #宣告變數讓使用者輸入
        elif command == "GOTO": #goto 10
            if not(gotoHandler(tokens[1:])): stopExecution = True #跳到指定的行號
        elif command == "IF": #if x > 1 then x = 1
            if not(ifHandler(tokens[1:])): stopExecution = True #if的判斷
#new go function
        elif command == "SAVE": #save file.py
            if not(saveFunction(tokens[1:])): stopExecution = True #存檔
        elif command == "LOAD": #load file.py
            if not(loadFunction(tokens[1:])): stopExecution = True #讀檔
        elif command == "GOSUB": #gosub 200
            if not(gosubFunction(tokens[1:])): stopExecution = True #跳到副程式
        elif command == "RETURN": #return
            if not(returnFunction()): stopExecution = True #返回副程式
#end
        elif command == "RUN": #run
            linePointer = 0
            while linePointer <= maxLine: 
                if linePointer in lines: #執行每一行程式直到最後一行程式
                    executeTokens(lines[linePointer]) 
                    if stopExecution:
                        stopExecution = False
                        return
                linePointer = linePointer + 1 

def getNumberPrintFormat(num): #整數轉int type,小數不變
    if int(num) == float(num):
        return int(num)
    return num

def gotoHandler(tokens): #goto對應的行號
    global linePointer
    if len(tokens) == 0:
        print("Error: Expected expression.")
        return
    newNumber = solveExpression(tokens, 0) 
    if newNumber[1] != "NUM": #行號都是數字
        print("Error: Line number expected.")
    else:
        linePointer = newNumber[0] - 1 #pointer指向對應的行號的前一個
    return True

def inputHandler(tokens): #宣告一個變數讓使用者在之後輸入值
    varName = None
    if len(tokens) == 0: #input後沒有東西
        print("Error: Expected identifier.")
        return
    elif len(tokens) == 1 and tokens[0][1] == "ID": #input後為變數(長度為1)
        varName = tokens[0][0]
    else:
        varName = solveExpression(tokens, 0)[0] #input後進行運算
        if not(isValidIdentifier(varName)): #不是變數
            print(f"Error: {varName} is not a valid identifier.")
            return
    while True:
        print("?", end = '') #輸入值
        varValue = input() #取得使用者輸入的值
        if getVarType(varName) == "STRING": #是字串
            identifiers[varName] = [varValue, "STRING"] #把字串的值放入對應的變數表中
            break
        else:
            if is_number(varValue): #是數字
                identifiers[varName] = [varValue, "NUM"] #把數字放入對應的變數表中
                break
            else:
                print("Try again.") #再次輸入
    return True

def ifHandler(tokens): #判斷if的條件句與執行後面的陳述句
#change
    thenPos = None #紀錄then的位置
    elsePos = None #紀錄else的位置
    for i in range(0, len(tokens)): #找then
        if tokens[i][1] == "THEN":
            thenPos = i
            break
    for i in range(0, len(tokens)): #找else
        if tokens[i][1] == "ELSE":
            elsePos = i
            break
    if thenPos == None: #沒有then
        print("Error: Malformed IF statement.")
        return
    exprValue = solveExpression(tokens[0:thenPos], 0) #if的條件句(then前),進行運算
    # print(thenPos,elsePos)
    if exprValue == None: #沒有結果
        return
    elif exprValue[0] != 0: 
        if len(tokens[thenPos+1:elsePos-1]) == 0: #沒有陳述句(then後)
            print("Error: Malformed IF statement.")
            return      
        executeTokens(tokens[thenPos+1:elsePos-1]) #執行then條件句
    elif exprValue[0] == 0:     
        if elsePos != None: #有else
            executeTokens(tokens[elsePos+1:]) #執行else條件句  
    return True
#end

def letHandler(tokens): #定義變數
    varName = None
    varValue = None
    eqPos = None #紀錄=的位置
    for i in range(0, len(tokens)): #找=
        if tokens[i][1] == "ASGN":
            eqPos = i
            break
    if eqPos == None: #一定要有=
        print("Error: Malformed LET statement.")
        return
    #確認變數
    if eqPos == 1 and tokens[0][1] == "ID": #[[x,ID],[=,ASGN],[1,NUM]]
        varName = tokens[0][0] #varname=x
    else:
        if len(tokens[0:i]) == 0: #=號前面沒有東西(變數)
            print("Error: Expected identifier.")
            return
        varName = solveExpression(tokens[0:i], 0) #變數做運算
        if varName == None: #沒有變數
            stopExecution = True
            return
        varName = varName[0] #存放運算後的變數(不要型態)
        if not(isValidIdentifier(varName)): #不符合變數規則
            print(f"Error: {varName} is not a valid identifier.")
            return
    #確認值
    if len(tokens[i+1:]) == 0: #=號後面沒有東西(值)
        print("Error: Expected expression.")
        return
    varValue = solveExpression(tokens[i+1:], 0) #對值做運算
    if varValue == None: #沒有值
        return
    if getVarType(varName) != varValue[1]: #運算結果型態轉變(error)
        print(f"Error: Variable {varName} type mismatch.")
        return
    identifiers[varName] = varValue #放入變數表,identifiers[x]=1
    return True

def printHandler(tokens): #一個一個print
    if len(tokens) == 0: #沒有東西print
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0) #取得變數運算完的結果
    if exprRes == None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0]) #確認整數型態
    print(exprRes[0])
    return True

def getIdentifierValue(name): #從變數表回傳變數
    return identifiers[name]

#new save、load、gosub&return
def saveFunction(tokens): #執行save
    path = tokens[0][0]
    f = open(path, 'w')
    i = 0
    while i < linePointer: #讀取save之前的程式
        if i in lines: 
            line = str(i)
            for token in lines[i]: 
                tokenVal = ""
                if token[1] == "NUM": 
                    tokenVal = getNumberPrintFormat(token[0]) 
                elif token[1] == "STRING": 
                    tokenVal = f"\"{token[0]}\""
                else:
                    tokenVal = token[0] 
                line += " " + str(tokenVal) 
            # print(line)
            f.write(line) #寫入path
            f.write("\n")
        i = i + 1
    f.close()
    return True

def loadFunction(tokens): #執行load
    #把原本的clear
    global maxLine, lines, identifiers 
    maxLine = 0
    lines = {}
    identifiers = {} 
    #讀檔
    path = tokens[0][0] 
    f = open(path, 'r')
    for line in f.readlines():
        if line != " ": #不要讀空行
            executeTokens(lex(line)) #執行讀進來的每一行
    f.close
    return True

def gosubFunction(tokens): #gosub對應行號，再把現在的位址存起來
    global linePointer, returnLine, lines #跟goto一樣?
    if len(tokens) == 0:
        print("Error: Expected expression.")
        return
    newNumber = solveExpression(tokens, 0) 
    if newNumber[1] != "NUM": 
        print("Error: Line number expected.")
    else:
        if tokens[0][0] in lines: 
            returnLine.append(linePointer) #將現在的位址存起來留給return用 加到列表最後
            linePointer = newNumber[0] - 1 
    return True    
 
def returnFunction(): #回到儲存的行號
    global linePointer, returnLine
    if len(returnLine) != 0: #有東西
        linePointer = returnLine.pop() #返回位址 把最後一個pop掉
    return True
#end

def solveExpression(tokens, level): #運算變數再回傳值與型態[ans,'NUM']
    leftSideValues = []
    rightSideValues = []
    if level < len(operators): #決定運算元優先權
        for i in range(0, len(tokens)): #對每個tokens檢查
#change
            if not(tokens[i][1] in ["OP", "NUM", "STRING", "ID", "MATHF"]): #不是這些東西
#end
                print(f"Error: Unknown operand {tokens[i][0]}")
                return None
#new math function
            elif tokens[i][1] == "MATHF" : #數學函式
                #三角函數
                if tokens[i][0] == "SIN": #sin function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.sin(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "COS": #cos function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.cos(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "TAN": #tan function
                    Value = solveExpression(tokens[i+1:], 0)
                    if  Value[0] == 90 or Value[0] == 270: #90&270度沒有東西
                        return ["NO VALUE","NUM"]
                    else:
                        return [round(math.tan(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ASIN": #arcsin function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.asin(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ACOS": #arccos function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.acos(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ATAN": #arctan function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.atan(Value[0])),5),"NUM"]
                elif tokens[i][0] == "SINH": #sinh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.sinh(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "COSH": #cosh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.cosh(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "TANH": #tanh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.tanh(math.radians(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ASINH": #arcsinh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.asinh(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ACOSH": #arccosh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.acosh(Value[0])),5),"NUM"]
                elif tokens[i][0] == "ATANH": #arctanh function
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(math.degrees(math.atanh(Value[0])),5),"NUM"]
                #數字處理
                elif tokens[i][0] == "FLOOR": #無條件捨去
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.floor(Value[0]),"NUM"]
                elif tokens[i][0] == "CEIL": #無條件進位
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.ceil(Value[0]),"NUM"]
                elif tokens[i][0] == "ROUND": #四捨五入
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [round(Value[0]),"NUM"]
                elif tokens[i][0] == "ABS": #絕對值
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [abs(Value[0]),"NUM"]
                elif tokens[i][0] == "DEG": #弧度轉角度
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.degrees(Value[0]),"NUM"]
                elif tokens[i][0] == "RAD": #角度轉弧度
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.radians(Value[0]),"NUM"]
                #指數運算
                elif tokens[i][0] == "EXP": #e的幾次方
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.exp(Value[0]),"NUM"]
                elif tokens[i][0] == "LN": #以e為底取log
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.log(Value[0]),"NUM"]
                elif tokens[i][0] == "LOG10": #以10為底取log
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.log10(Value[0]),"NUM"]
                elif tokens[i][0] == "LOG2": #以2為底取log
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.log2(Value[0]),"NUM"]
                elif tokens[i][0] == "SQRT": #開根號
                    Value = solveExpression(tokens[i+1:], 0) 
                    return [math.sqrt(Value[0]),"NUM"] 
                elif tokens[i][0] == "FACT": #階乘
                    Value = solveExpression(tokens[i+1:], 0) 
                    if Value[0] - math.floor(Value[0]) != 0: #一定要整數
                        return ["NOT INTEGER","NUM"]
                    else:
                        return [math.factorial(int(Value[0])),"NUM"] 
#end
            elif tokens[i][1] == "OP" and tokens[i][0] in operators[level]: #是OP,做運算
                exprResL = None
                exprResR = None
                #分OP左右不斷遞迴下去
                if len(leftSideValues) != 0:
                    exprResL = solveExpression(leftSideValues, level)
                rightSideValues = tokens[i+1:]
                if len(rightSideValues) != 0:
                    exprResR = solveExpression(rightSideValues, level)
                if exprResL == None or exprResR == None:
                    return None
                #運算元
                if tokens[i][0] == "+": #+號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊的數字相加
                        return [float(exprResL[0]) + float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "-": #-號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊數字相減
                        return [float(exprResL[0]) - float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "/": #/號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊數字相除
                        return [float(exprResL[0]) / float(exprResR[0]), "NUM"] 
                    else:
                        print("Error: Operand type mismatch.")
                        return None 
                elif tokens[i][0] == "*": #*號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊數字相乘
                        return [float(exprResL[0]) * float(exprResR[0]), "NUM"] 
                    else:
                        print("Error: Operand type mismatch.")
                        return None     
                elif tokens[i][0] == "^": #^號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左邊數字的右邊次方
                        return [float(exprResL[0]) ** float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "%": #%號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右數字相除取餘數
                        return [float(exprResL[0]) % float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                #判斷大小
                elif tokens[i][0] == "==": #==號,相等
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] == exprResR[0], "NUM"] #左右兩邊數字是否相等
                elif tokens[i][0] == "!=": #!=號,不相等
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] != exprResR[0], "NUM"] #左右兩邊數字是否不相等
                elif tokens[i][0] == "<=": #<=號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] <= exprResR[0], "NUM"] #左邊數字是否小於等於右邊
                elif tokens[i][0] == "<": #<號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] < exprResR[0], "NUM"] #左邊數字是否小於右邊
                elif tokens[i][0] == ">": #>號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] > exprResR[0], "NUM"] #左邊數字是否大於右邊
                elif tokens[i][0] == ">=": #>=號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] >= exprResR[0], "NUM"] #左邊數字是否大於等於右邊
                #邏輯運算
                elif tokens[i][0] == "&": #&號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊做and運算
                        return [(exprResL[0]) and (exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "|": #|號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊做or運算
                        return [(exprResL[0]) or (exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
#new operator
                elif tokens[i][0] == "^^": #^號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左右兩邊做xor運算(數字對數字)
                        return [int(exprResL[0]) ^ int(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None        
                #平移
                elif tokens[i][0] == ">>": #>>號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #右移
                        return [int(exprResL[0]) >> int(exprResR[0]), "NUM"] 
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "<<": #<<號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM": #左移
                        return [int(exprResL[0]) << int(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
#end
                #小數點?
                elif tokens[i][0] == ".": #.號
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        value1 = exprResL[0] #整數部分
                        if exprResL[1] == "NUM":
                            value1 = str(getNumberPrintFormat(value1)) #檢查型態(整數轉int)
                        value2 = exprResR[0] #小數部分
                        if exprResR[1] == "NUM":
                            value2 = str(getNumberPrintFormat(value2)) #檢查型態(小數不變)
                        return [value1 + value2, "STRING"]
            else: #不是OP(NUM,STRING,ID)
                leftSideValues.append(tokens[i]) #直接放到left
        return solveExpression(leftSideValues, level + 1) #遞迴
    else: #不在所有運算元中
        if len(tokens) > 1: #還沒分割到最簡
            print("Error: Operator expected.")
            return None
        elif tokens[0][1] == "ID":
            if tokens[0][0] in identifiers: #在變數裡面(存在變數表中)
                return getIdentifierValue(tokens[0][0])
            else: #不存在變數表
                print(f"Error: Variable {tokens[0][0]} not initialized.")
                return None
        return tokens[0] #直接回傳tokens

main()
