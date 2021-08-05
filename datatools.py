
gearHistory = []
rpmHistory = []
spdHistory = []

"""
fix functions will return the last valid value, 
should they encounter an incorrect one.
"""
def resetHistory():
    global gearHistory, rpmHistory, spdHistory
    gearHistory = []
    rpmHistory = []
    spdHistory = []

def fixGear(val):
    global gearHistory
    raise NotImplementedError()

def fixRPM(val):
    global rpmHistory
    if not val:
        return 0
    ival = int(val)
    ival = ival/100
    if ival < 1: # prevent invalid reads
        val = rpmHistory[-1]

    if rpmHistory and ival-int(rpmHistory[-1])/100 > 3: #prevent jumps larger than 3
       val = rpmHistory[-1]    
    if rpmHistory and int(rpmHistory[-1])/100-ival > 1: #prevent drops larger than 1
       val = rpmHistory[-1]

    rpmHistory.append(val)
    if len(rpmHistory) > 10:
        rpmHistory.pop(0)
    return val
    
def fixSPD(val):
    global spdHistory
    if not val:
        return 0
    ival = int(val)
    ival = ival

    if spdHistory and ival-int(spdHistory[-1]) > 3:
       val = spdHistory[-1]    
    if spdHistory and int(spdHistory[-1])-ival > 1:
       val = spdHistory[-1]

    spdHistory.append(val)
    if len(spdHistory) > 10:
        spdHistory.pop(0)
    return val