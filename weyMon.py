from _winreg import *
from Tkinter import *
import threading
import time
import ast
import os

#######################################
##### pyregistry by Thejaswi Raya #####
#######################################

mapping = {
    "HKCR":HKEY_CLASSES_ROOT,
    "HKCU":HKEY_CURRENT_USER,
    "HKLM":HKEY_LOCAL_MACHINE,
    "HKU":HKEY_USERS,
    "HKPD":HKEY_PERFORMANCE_DATA,
    "HKCC":HKEY_CURRENT_CONFIG,
    "HKDD":HKEY_DYN_DATA
    }
 
def readSubKeys(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(mapping[hkey], regPath)
    subKeys = []
    noOfSubkeys = QueryInfoKey(reg)[0]
    for i in range(0, noOfSubkeys):
        subKeys.append(EnumKey(reg, i))
    CloseKey(reg)
    return subKeys
 
def readValues(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(mapping[hkey], regPath)
    values = {}
    noOfValues = QueryInfoKey(reg)[1]
    for i in range(0, noOfValues):
        values[EnumValue(reg, i)[0]] = EnumValue(reg, i)[1]
    CloseKey(reg)
    return values
 
def pathExists(hkey, regPath):
    try:
        reg = OpenKey(mapping[hkey], regPath)
    except WindowsError:
        return False
    CloseKey(reg)
    return True

#######################################
########## weyMon Section #############
#######################################

window = Tk()
window.title("weyMon")

isActive = IntVar()
modeCheck = Checkbutton(window, text="Active",variable=isActive)
modeCheck.grid(row=0,column=0,sticky="w",pady=(5,0))

revertText = StringVar()
revertSelect = Label(window,textvariable=revertText,width=30,bg="white")
revertSelect.grid(row=0,column=3,pady=(5,0),padx=5)

################################
changedFrame = Frame(window,bd=5)
changedFrame.grid(row=1,column=0,columnspan=3)

changedList = Listbox(changedFrame,width=80,height=10)
changedList.pack(side="left",fill="y")
changedList.insert(0,"CHANGED:")

changedScroll = Scrollbar(changedFrame,orient="vertical")
changedScroll.config(command=changedList.yview)
changedScroll.pack(side="right",fill="y")
changedList.config(yscrollcommand=changedScroll.set)
################################
missingFrame = Frame(window,bd=5)
missingFrame.grid(row=2,column=0,columnspan=3)

missingList = Listbox(missingFrame,width=80,height=10)
missingList.pack(side="left",fill="y")
missingList.insert(0,"MISSING:")    

missingScroll = Scrollbar(missingFrame,orient="vertical")
missingScroll.config(command=missingList.yview)
missingScroll.pack(side="right",fill="y")
missingList.config(yscrollcommand=missingScroll.set)
################################
newFrame = Frame(window,bd=5)
newFrame.grid(row=3,column=0,columnspan=3)

newList = Listbox(newFrame,width=80,height=10)
newList.pack(side="left",fill="y")
newList.insert(0,"NEW:")

newScroll = Scrollbar(newFrame,orient="vertical")
newScroll.config(command=newList.yview)
newScroll.pack(side="right",fill="y")
newList.config(yscrollcommand=newScroll.set)
################################
snapFrame = Frame(window,bd=5)
snapFrame.grid(row=1,column=3,rowspan=3)

snapList = Listbox(snapFrame,width=30,height=30)
snapList.pack(side="left",fill="y")

snapScroll = Scrollbar(snapFrame,orient="vertical")
snapScroll.config(command=snapList.yview)
snapScroll.pack(side="right",fill="y")
snapList.config(yscrollcommand=snapScroll.set)
################################

allChecks = {
    "HKLM":[
        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunServices",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunServicesOnce",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\\Folder\\Hidden\\SHOWALL",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\\Folder\\HideFileExt",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\\Folder\\Hidden\\SHOWALL",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\\Folder\\SuperHidden\\UncheckedValue",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\Userinit",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Shell",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Svchost",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\TerminalServer\\Install\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options",
        "Software\\Classes\\exefile\\shell\\runas\\command",
        "Software\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU",
        "System\\CurrentControlSet\\services",
        "System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp",
        "System\\Internet Communication Management\\Internet Communication"
        ],
    "HKCU":[
        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunServices",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunServicesOnce",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders\\Start Menu",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.txt\\OpenWithList",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\WindowsUpdate",
        "Software\\Mirabilis\\ICQ\\Agent\\Apps\\test",
        "Control Panel\\Desktop"
        ],
    "HKCR":[
        "Shell\\shell\\explore\\command"
        ]
    }

hkeys = []
initial = {}
revertBit = 0

def getValues():
    values = {}
    for hkey in hkeys:
        for check in allChecks[hkey]:
            temp = readValues(hkey,check)
            if temp != -1 and temp != {}:
                values.update({hkey+"\\"+check:temp})
    return values

def setInit():
    global initial
    temp = open("snapshots/"+revertText.get(),"r")
    initial = ast.literal_eval(temp.read())
    temp.close()
    
def clearAll():
    changedList.delete(1,END)
    missingList.delete(1,END)
    newList.delete(1,END)
    
def snapshot():
    fileName = time.strftime("%Y_%m_%d_(%H%M%S).txt")
    if fileName not in snapList.get(0,END):
        temp = open("snapshots/"+fileName,"w")
        temp.write(str(getValues()))
        temp.close()
        snapList.insert(0,fileName)
        revertText.set(fileName)
        setInit()
        clearAll()

def changeRevert(item):
    revertText.set(item)
    setInit()

def delete(item):
    snapList.delete(snapList.get(0,END).index(item))
    os.remove("snapshots/"+item)
    if snapList.get(0,END) == ():
        snapshot()
    elif revertText.get() == item:
        revertText.set(snapList.get(0))
        setInit()

def revert():
    global revertBit
    clearAll()
    revertBit = 1

################################
snapButton = Button(window,text="Snapshot",command=snapshot)
snapButton.grid(row=0,column=1,sticky="e",pady=(5,0))

revertButton = Button(window,text="Revert",command=revert)
revertButton.grid(row=0,column=2,sticky="e",pady=(5,0))

snapList.bind("<Return>",lambda event:changeRevert(snapList.get(snapList.curselection())))
snapList.bind("<Delete>",lambda event:delete(snapList.get(snapList.curselection())))
################################

def setup():
    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")
        snapshot()
    elif os.listdir("snapshots") == []:
        snapshot()
    else:
        snapshots = os.listdir("snapshots")
        for snap in snapshots:
            snapList.insert(0,snap)
        revertText.set(snapList.get(0))
        setInit()
        
def getHKeys():
    for key in mapping.keys():
        if pathExists(key,"") and key in allChecks.keys():
            hkeys.append(key)

def copy(dictionary):
    temp = {}
    for path in dictionary.keys():
        temp2 = {}
        for value in dictionary[path].keys():
            temp2.update({value:dictionary[path][value]})
        temp.update({path:temp2})
    return temp

def showChanged(paths):
    if revertBit:
        for path in paths:
            hkey = path[:path.index("\\")]
            keyval = path[path.index("\\")+1:]
            key = OpenKey(mapping[hkey],keyval,0,KEY_ALL_ACCESS)
            for value in paths[path]:
                SetValueEx(key,value,0,REG_SZ,initial[path][value])
            CloseKey(key)
        return
    for path in paths:
        changedList.insert(END,"    "+path)
        for value in paths[path]:
            changedList.insert(END,"        {}:        {}    =>    {}".format(value,initial[path][value],paths[path][value]))
    
def showMissing(paths):
    if revertBit:
        for path in paths:
            hkey = path[:path.index("\\")]
            keyval = path[path.index("\\")+1:]
            key = CreateKey(mapping[hkey],keyval)
            for value in paths[path]:
                SetValueEx(key,value,0,REG_SZ,initial[path][value])
            CloseKey(key)
        return
    for path in paths:
        missingList.insert(END,"    "+path)
        for value in paths[path]:
            missingList.insert(END,"        {}:        {}".format(value,paths[path][value]))
    
def showNew(paths):
    if revertBit:
        for path in paths:
            hkey = path[:path.index("\\")]
            keyval = path[path.index("\\")+1:]
            key = OpenKey(mapping[hkey],keyval,0,KEY_ALL_ACCESS)
            for value in paths[path]:
                DeleteValue(key,value)
            CloseKey(key)
        return
    for path in paths:
        newList.insert(END,"    "+path)
        for value in paths[path]:
            newList.insert(END,"        {}:        {}".format(value,paths[path][value]))

def monitor():
    global revertBit
    tempInitial = copy(dict(initial))
    values = getValues()
    if values != tempInitial:
        if isActive.get():
            revertBit=1
        changed = {}
        new = {}
        for path in values.keys():
            tempChanged = {}
            tempNew = {}
            for value in values[path].keys():
                if path not in tempInitial:
                    new.update({path:values[path]})
                    break
                elif value not in tempInitial[path]:
                    tempNew.update({value:values[path][value]})
                elif values[path][value] != tempInitial[path][value]:
                    tempChanged.update({value:values[path][value]})
                    tempInitial[path].pop(value)
                else:
                    tempInitial[path].pop(value)
                if tempInitial[path] == {}:
                    tempInitial.pop(path)
            if tempChanged != {}:
                changed.update({path:tempChanged})
            if tempNew != {}:
                new.update({path:tempNew})
        clearAll()
        if changed != {}:
            showChanged(changed)
        if new != {}:
            showNew(new)
        if tempInitial != {}:
            showMissing(tempInitial)
        if revertBit:
            revertBit=0
    else:
        clearAll()
    threading.Timer(5,monitor).start()

if __name__ == "__main__":
    getHKeys()
    setup()
    monitor()
    window.mainloop()
