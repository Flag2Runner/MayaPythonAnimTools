# commandPort -n "localhost:7001" -stp "mel"
import maya.cmds as mc

########################################
#             Facilities               #
########################################

class Vector:
    def __init__(self, *args):
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]
        
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z )
    
    #operator - overload
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z )
    
    # operator * overload
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vector(self.x/scalar, self.y/scalar, self.z/scalar)
    
    def GetLength(self):
        return (self.x ** 2 + self.y ** 2 + self.z **2) ** 0.5
    
    def GetNormalized(self):
        return self/self.GetLength()
    
    def __str__(self):
        return f"<{self.x},{self.y},{self.z}>"

def GetObjPos(obj):
    pos = mc.xform(obj, t=True, q=True, ws=True)
    return Vector(pos[0], pos[1], pos[2])

def SetObjPos(obj, pos: Vector):
    mc.setAttr(obj + ".translate", pos.x, pos.y, pos.z, type = "float3")

def CreateControllerForJnt(jnt, size = 10,  colorR = 0, colorG = 0, colorB = 0):
    ctrlName = "ac_" + jnt
    ctrlGrpName = ctrlName + "_grp"

    mc.circle(n=ctrlName, nr=(1,0,0), r = size)
    mc.group(ctrlName, n = ctrlGrpName)
    mc.setAttr(ctrlName + ".overrideEnabled", True)
    mc.setAttr(ctrlName +".overrideRGBColors", 1)
    mc.setAttr(ctrlName +".overrideColorRGB", colorR,colorG,colorB) # 1 = 255

    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(ctrlName, jnt) 

    return ctrlName, ctrlGrpName

def CreateBox(name, size = 10,colorR = 0, colorG = 0, colorB = 0):
    #curve -d 1 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;
    p = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    mc.curve(n=name, d=1, p = p)
    mc.setAttr(name + ".overrideEnabled", True)
    mc.setAttr(name +".overrideRGBColors", 1)
    mc.setAttr(name +".overrideColorRGB", colorR,colorG,colorB) # 1 = 255
    mc.setAttr(name + ".scale", size,size,size, type = "float3")
    mc.makeIdentity(name, apply = True)

def CreatePlus(name, size = 10, colorR = 0, colorG = 0, colorB = 0):
    p = ((0.5,0,1),(0.5,0,0.5),(1,0,0.5),(1,0,-0.5),(0.5,0,-0.5),(0.5,0,-1),(-0.5,0,-1),(-0.5,0,-0.5),(-1,0,-0.5),(-1,0,0.5),(-0.5,0,0.5),(-0.5,0,1),(0.5,0,1))
    mc.curve(n=name, d=1, p = p) 
    
    mc.setAttr(name + ".overrideEnabled", True)
    mc.setAttr(name +".overrideRGBColors", 1)
    mc.setAttr(name +".overrideColorRGB", colorR,colorG,colorB) # 1 = 255

    mc.setAttr(name + ".rx", 90)
    mc.setAttr(name +".scale", size,size,size, type = "float3")
    mc.makeIdentity(name, apply = True)
    

class ThreeJntChain:
    def __init__(self):
        self.root = ""
        self.middle = ""
        self.end = ""  
        self.ctrlSize = 10
        self.colorR = 1
        self.colorG = 1
        self.colorB = 1

    def AutoFindJntsBasedOnSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.middle = mc.listRelatives(self.root, c=True, type = "joint")[0]
        self.end = mc.listRelatives(self.middle, c=True, type = "joint")[0]

    def RigThreeJntChain(self):
        size = self.ctrlSize


        rootCtrl, rootCtrlGrp = CreateControllerForJnt(self.root, size,self.colorR,self.colorG,self.colorB)
        middleCtrl, middleCtrlGrp = CreateControllerForJnt(self.middle, size,self.colorR,self.colorG,self.colorB)
        endCtrl, endCtrlGroup = CreateControllerForJnt(self.end, size,self.colorR,self.colorG,self.colorB)

        mc.parent(middleCtrlGrp, rootCtrl)
        mc.parent(endCtrlGroup, middleCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        CreateBox(ikEndCtrl, size, self.colorR,self.colorG,self.colorB)
        ikEndCtrlGrp = ikEndCtrl + "_grp"
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n = ikHandleName, sj = self.root, ee = self.end , sol = "ikRPsolver")

        ikMidCtrl = "ac_ik_" + self.middle
        mc.spaceLocator(n= ikMidCtrl)
        mc.setAttr(ikMidCtrl + ".overrideEnabled", True)
        mc.setAttr(ikMidCtrl +".overrideRGBColors", 1)
        mc.setAttr(ikMidCtrl +".overrideColorRGB", self.colorR,self.colorG,self.colorB) # 1 = 255

        rootJntPos = GetObjPos(self.root)
        endJntPos = GetObjPos(self.end)
        poleVec = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVec = Vector(poleVec[0],poleVec[1],poleVec[2])

        armVec = endJntPos - rootJntPos
        halfArmLenth = armVec.GetLength()
        
        poleVecPos = rootJntPos + poleVec * halfArmLenth + armVec/2
        ikMidCtrlGrp = ikMidCtrl + "_grp"
        mc.group(ikMidCtrl, n = ikMidCtrlGrp)
        mc.setAttr(ikMidCtrl + ".scale" ,self.ctrlSize, self.ctrlSize, self.ctrlSize, type = "float3")
        SetObjPos(ikMidCtrl, poleVecPos)

        mc.poleVectorConstraint(ikMidCtrl, ikHandleName)
        mc.parent(ikHandleName, ikEndCtrl)

        ikfkBlendCtrl = "ac_" + self.root + "_ikfkBlend"
        CreatePlus(ikfkBlendCtrl, size/5, self.colorR,self.colorG,self.colorB)
        ikfkBlendCtrlGpr = ikfkBlendCtrl + "_grp"
        mc.group(ikfkBlendCtrl, n = ikfkBlendCtrlGpr)

        dir = 1
        if rootJntPos.x < 0:
            dir = -1

        ikfkBlendPos = rootJntPos + Vector(dir * halfArmLenth/4, halfArmLenth/4 ,0)
        SetObjPos(ikfkBlendCtrlGpr, ikfkBlendPos)

        ikfkBlendAttr = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln = ikfkBlendAttr, k = True, at = "float", min = 0, max = 1)
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikHandleName + ".ikBlend")


        ikfkReverse = "reverse_" + self.root + "_ikfkblend"
        mc.createNode("reverse", n = ikfkReverse)

        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikfkReverse + ".inputX")
        mc.connectAttr(ikfkBlendCtrl +"." + ikfkBlendAttr, ikEndCtrlGrp + ".v")
        mc.connectAttr(ikfkBlendCtrl +"." + ikfkBlendAttr, ikMidCtrlGrp + ".v")
        mc.connectAttr(ikfkReverse + ".outputX", rootCtrlGrp + ".v")

        mc.connectAttr(ikfkReverse + ".outputX", endOrientConstraint + ".w0")
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, endOrientConstraint + ".w1")

        #group everything together and name it properly
        topGrpName = self.root + "_rig_grp"
        mc.group(rootCtrlGrp,ikEndCtrlGrp,ikfkBlendCtrlGpr,ikMidCtrlGrp, n = topGrpName )

        #hide useless stuff - ikHandle.
        mc.setAttr(ikHandleName + ".v", 0)

########################################
#             UI                       #
########################################
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QColorDialog
from PySide2.QtGui import QDoubleValidator, QColor, QPainter, QPalette, QPixmap

class ColorPickerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor(0,0,0)
        self.masterLayout = QVBoxLayout()   
        self.setLayout(self.masterLayout)
        self.button = QPushButton()
        self.button.clicked.connect(self.ButtonPressed)
        self.setAutoFillBackground(True)
        self.masterLayout.addWidget(self.button)
        self.setFixedSize(200,50)
        self.colorD = QColorDialog()

    def ButtonPressed(self, event):
        self.colorD.setCurrentColor(self.color)
        self.color = QColor(self.colorD.getColor())
        print(self.color)
        
        self.button.setStyleSheet(f"background-color : yellow")

        print(f"Button {self.color.getRgbF()}")
        
    def paintEvent(self, event):
        self.colorD = QColorDialog(self.color) 
        self.button.setStyleSheet(f"background-color : {self.color.name()}")

        

class ThreeJntChainWiget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Three Joint Chain")
        self.setGeometry(0,0,300,300)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        hintLabel = QLabel("Please Select the root of the joint chain")
        self.masterLayout.addWidget(hintLabel)

        autoFindBtn = QPushButton("Auto Find Jnt")
        self.masterLayout.addWidget(autoFindBtn)
        autoFindBtn.clicked.connect(self.AutoFindBtnclicked)

        self.selectionDisplay = QLabel()
        self.masterLayout.addWidget(self.selectionDisplay)

        ctrlSettingLayout = QHBoxLayout()
        ctrlSizeLabel = QLabel("Controller Size: ")
        ctrlSettingLayout.addWidget(ctrlSizeLabel)

        self.ctrlSize = QLineEdit()
        self.ctrlSize.setValidator(QDoubleValidator())
        self.ctrlSize.textChanged.connect(self.CtrlSizeValueSet)
        self.ctrlSize.setText("10") # probably broken
        ctrlSettingLayout.addWidget(self.ctrlSize)

        self.masterLayout.addLayout(ctrlSettingLayout)

        self.colorPicker = ColorPickerWidget()
        self.masterLayout.addWidget(self.colorPicker)

        rigThreeJntchainBtn = QPushButton("Rig Three Jnt Chain")
        self.masterLayout.addWidget(rigThreeJntchainBtn)
        rigThreeJntchainBtn.clicked.connect(self.RigThreeJntChainbtnClicked)


        self.adjustSize()
        self.threeJntChain = ThreeJntChain()

    def AutoFindBtnclicked(self):
        print("Find Button Pressed")
        self.threeJntChain.AutoFindJntsBasedOnSel()
        self.selectionDisplay.setText((f"{self.threeJntChain.root}, {self.threeJntChain.middle}, {self.threeJntChain.end}"))
    
    def RigThreeJntChainbtnClicked(self):
        print("Rig Button Pressed")
        self.threeJntChain.colorR = self.colorPicker.color.redF()
        self.threeJntChain.colorG = self.colorPicker.color.greenF()
        self.threeJntChain.colorB = self.colorPicker.color.blueF()
        print(self.colorPicker.color.redF)
        print(self.colorPicker.color.greenF)
        print(self.colorPicker.color.blueF)
        self.threeJntChain.RigThreeJntChain()
    
    def CtrlSizeValueSet(self, valStr:str):
        size = float(valStr)
        self.threeJntChain.ctrlSize = size

threeJntChainWidget = ThreeJntChainWiget()
threeJntChainWidget.show()