'''
不能识别：
    1. 百分数

可以识别：
    1. 包括亿、千亿、万亿等；
    2. 整点的时间不进行转换；
    3. 单独出现的一位数字不进行转换，例如：一心一意，天下第一关；
    4. 叠字出现的数字位不进行转换，例如：亿万，千千万万；
    5. 包含小数点时，小于5位的不进行转换，例如：十二点零五，三点零九（重要是为了避免时间的误转，所以类似三点零五这种小数也不转换了）；
    6. 支持大数缩写的转换，例如：二十八亿，三点六万，转写成 28亿，3.6万
    7. 支持对口语表达的转换，例如：二万五，转写成 25000，而不是 20005
'''


import re

UNIT = {
    "十": 10,
    "百": 100,
    "千": 1000,
    "万": 10000,
    "亿": 100000000,
    "点": "."
}

NUM = {
    "零": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9
}

def normal_num(shuzi):
    shuzi = re.sub('零', '0', shuzi)
    shuzi = re.sub("一", '1', shuzi)
    shuzi = re.sub('二', '2', shuzi)
    shuzi = re.sub('两', '2', shuzi)
    shuzi = re.sub('三', '3', shuzi)
    shuzi = re.sub('四', '4', shuzi)
    shuzi = re.sub('五', '5', shuzi)
    shuzi = re.sub('六', '6', shuzi)
    shuzi = re.sub('七', '7', shuzi)
    shuzi = re.sub('八', '8', shuzi)
    shuzi = re.sub('九', '9', shuzi)
    shuzi = re.sub('点', '.', shuzi)
    return shuzi

def transfer_base(shuzi):
    shuzi = str(shuzi)
    UNIT_qian = {
        "十": 10,
        "百": 100,
        "千": 1000
    }

    Arab_Digit = []
    for i in shuzi:
        if i in UNIT_qian:
            Arab_Digit.append(int(shuzi[shuzi.find(i) - 1]) * UNIT_qian[i])
    Final_Number = 0
    for i in Arab_Digit:
        Final_Number = Final_Number + i

    if shuzi[-1] in UNIT_qian:
        return Final_Number
    else:
        return Final_Number + int(shuzi[-1])

def transfer_wan(shuzi):
    shuzi = str(shuzi)
    if len(shuzi.split('万')) > 1:
        if shuzi.split('万', 1)[-1] != '':
            shuzi_high = shuzi.split('万')[0]
            shuzi_low = shuzi.split('万')[-1]
        else:
            shuzi_high = shuzi.split('万')[0]
            shuzi_low = 0
    else:
        shuzi_high = shuzi.split('万')[0]
        shuzi_low = 0

    return transfer_base(shuzi_high) * 10000 + transfer_base(shuzi_low)

def transfer_yi(shuzi):
    shuzi = str(shuzi)
    if shuzi.split('亿', 1)[-1] != '':               #判断是否是整数亿
        shuzi_high = shuzi.split('亿')[0]
        shuzi_low = shuzi.split('亿')[-1]
    else:
        shuzi_high = shuzi.split('亿')[0]
        shuzi_low = 0

    if shuzi_high.find('万') != -1:                  #判断亿位之前是否包含"万"字
        shuzi_yi_high = transfer_wan(shuzi_high)*100000000
        shuzi_yi_low = transfer_wan(shuzi_low)
        result = shuzi_yi_high + shuzi_yi_low
    else:
        result = transfer_wan(shuzi_high) * 10000 + transfer_wan(shuzi_low)

    return result

def transfer_int(shuzi):
    if shuzi.find('亿') != -1:
        result = transfer_yi(shuzi)
    elif shuzi.find('万') != -1:
        result = transfer_wan(shuzi)
    else:
        result = transfer_base(shuzi)

    return result

def number_transfer(shuzi):
    inter_num_string = normal_num(shuzi)
    #print(inter_num_string)

    if inter_num_string.find('.') != -1:
        #print(inter_num_string.split('.'))
        float_number = float("0." + inter_num_string.split('.')[-1])
        #print(float_number)
        int_string = inter_num_string.split('.')[0]
        #print(int_string)
        #print(transfer_int(int_string))
        transfer_result = transfer_int(int_string) + float_number
    else:
        transfer_result = transfer_int(inter_num_string)

    return transfer_result

def numberComplt(shuzi):
    comp = ''
    if shuzi[-1] in UNIT or shuzi[-2] == "十":
        pass
    else:
        for unit in UNIT:
            if shuzi[-2] == unit:
                shuzi = shuzi +comp
            else:
                comp = unit
    return shuzi


sentence = "我一心一意数个数，我一点都不知道，十二点十五，三千七百八十二。我再数个数，三亿五千六百二十万七千一百零四点一八。两万五，四点五万，三千七，四十八万，五十六亿，千万不能算错。一件小事，千依百顺。十二点一刻，三点十五，两点零四。三点一四一五九二六。"

Number = ""
Digits = []
for char in sentence:
    if (char in NUM) or (char in UNIT):
        Number = Number + char
    else:
        if Number == "":
            pass
        else:
            Digits.append(Number)
            Number = ""

Digits_transferred = []
for digit in Digits:
    if digit.find("点") == -1:
        Judge = []
        if len(digit) != 1:
            for a in digit:
                if a in UNIT:
                    judge = 1
                else:
                    judge = 0
                Judge.append(judge)
            if 0 in Judge:
                Digits_transferred.append(digit)
            else:
                pass
    elif digit[-1] != "点":
        if digit[-1] == "亿" or digit[-1] == "万":
            Digits_transferred.append(digit)
        elif len(digit) > 4:
            try:
                if digit.rindex("十") < digit.rindex("点"):
                    Digits_transferred.append(digit)
            except:
                Digits_transferred.append(digit)

print("These are all SHUZI from sentence: ", Digits)
#print("Remove single digit from SHUZI: ", Digits_transferred)

for digit in Digits_transferred:
    result = numberComplt(digit)
    Digits_transferred[Digits_transferred.index(digit)] = result

#print("There are all digits need to be transferred: ", Digits_transferred)

for shuzi in Digits_transferred:
    if shuzi[-1] == "万" or shuzi[-1] == "亿":
        shuziUnit = shuzi[-1]
        shuziNum = shuzi[:-1]
        shuziResult = str(number_transfer(shuziNum)) + shuziUnit
    else:
        shuziResult = number_transfer(shuzi)
    Digits_transferred[Digits_transferred.index(shuzi)] = shuziResult

print("These are all transferred Number:", Digits_transferred)