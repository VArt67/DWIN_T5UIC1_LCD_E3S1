
from DWIN_Screen import T5UIC1_LCD
from printerInterface import PrinterData
from enum import Enum
import traceback
import debugpy

ENCODER_DIFF_NO = 0  # no state
ENCODER_DIFF_CW = 1  # clockwise rotation
ENCODER_DIFF_CCW = 2  # counterclockwise rotation
ENCODER_DIFF_ENTER = 3   # click


ICON_LOGO = 0
ICON_Print_0 = 1
ICON_Print_1 = 2
ICON_Prepare_0 = 3
ICON_Prepare_1 = 4
ICON_Control_0 = 5
ICON_Control_1 = 6
ICON_Leveling_0 = 7
ICON_Leveling_1 = 8
ICON_HotendTemp = 9
ICON_BedTemp = 10
ICON_Speed = 11
ICON_Zoffset = 12
ICON_Back = 13
ICON_File = 14
ICON_PrintTime = 15
ICON_RemainTime = 16
ICON_Setup_0 = 17
ICON_Setup_1 = 18
ICON_Pause_0 = 19
ICON_Pause_1 = 20
ICON_Continue_0 = 21
ICON_Continue_1 = 22
ICON_Stop_0 = 23
ICON_Stop_1 = 24
ICON_Bar = 25
ICON_More = 26
ICON_Axis = 27
ICON_CloseMotor = 28
ICON_Homing = 29
ICON_SetHome = 30
ICON_PLAPreheat = 31
ICON_ABSPreheat = 32
ICON_Cool = 33
ICON_Language = 34
ICON_MoveX = 35
ICON_MoveY = 36
ICON_MoveZ = 37
ICON_Extruder = 38
ICON_Temperature = 40
ICON_Motion = 41
ICON_WriteEEPROM = 42
ICON_ReadEEPROM = 43
ICON_ResumeEEPROM = 44
ICON_Info = 45
ICON_SetEndTemp = 46
ICON_SetBedTemp = 47
ICON_FanSpeed = 48
ICON_SetPLAPreheat = 49
ICON_SetABSPreheat = 50
ICON_MaxSpeed = 51
ICON_MaxAccelerated = 52
ICON_MaxJerk = 53
ICON_Step = 54
ICON_PrintSize = 55
ICON_Version = 56
ICON_Contact = 57
ICON_StockConfiguraton = 58
ICON_MaxSpeedX = 59
ICON_MaxSpeedY = 60
ICON_MaxSpeedZ = 61
ICON_MaxSpeedE = 62
ICON_MaxAccX = 63
ICON_MaxAccY = 64
ICON_MaxAccZ = 65
ICON_MaxAccE = 66
ICON_MaxSpeedJerkX = 67
ICON_MaxSpeedJerkY = 68
ICON_MaxSpeedJerkZ = 69
ICON_MaxSpeedJerkE = 70
ICON_StepX = 71
ICON_StepY = 72
ICON_StepZ = 73
ICON_StepE = 74
ICON_Setspeed = 75
ICON_SetZOffset = 76
ICON_Rectangle = 77
ICON_BLTouch = 78
ICON_TempTooLow = 79
ICON_AutoLeveling = 80
ICON_TempTooHigh = 81
ICON_NoTips_C = 82
ICON_NoTips_E = 83
ICON_Continue_C = 84
ICON_Continue_E = 85
ICON_Cancel_C = 86
ICON_Cancel_E = 87
ICON_Confirm_C = 88
ICON_Confirm_E = 89
ICON_Info_0 = 90
ICON_Info_1 = 91





class LineItemType(Enum):
	Unknown=0	# Only valid for Init
	Int=1
	Float=2
	SignedFloat=3
	Callback=4	
	SubMenu=5



class MenuItem:
	def __init__(self, icon, label: str, itemType, callback=None, getValueCallback=None, min=0, max=100, enableAccel=True):
		self.icon=icon
		self.label=label
		self.type=itemType
		self.callback=callback
		self.getValueCallback=getValueCallback
		self.enableAccel=enableAccel
		self.min=min
		self.max=max
		self.value=0
		self.iDigits=3		# number of interger digits
		self.fDigits=1		# number fraction digits (only for Float or SignedFloat)
		self.incDecValues=1
		if (itemType == LineItemType.Float or itemType == LineItemType.SignedFloat):
			self.iDigits = 2
			self.incDecValues = 0.1
		self.valueChangeCallback=None	# Callback if value changes by user interaction
		self.activateCallback=None	    # Callback before execution of activate

	def setMinMax(self, min, max):
		self.min=min
		self.max=max

	def setDigits(self, iDigits, fDigits):
		self.iDigits=iDigits
		self.fDigits=fDigits
  
	def setIncValue(self, incDec):
		self.incDecValues=incDec
  
	def setValueChangeCallback(self, valueChangeCallback):
		self.valueChangeCallback = valueChangeCallback
   
	def setActivateCallback(self, activateCallback):
		self.activateCallback = activateCallback
   
	def setValue(self, value):
		self.value = value
		if (self.value>self.max): 
			self.value=self.max
		if (self.value<self.min): 
			self.value=self.min

	def getValue(self):
		return self.value

	def activate(self):
		if (self.activateCallback):
			self.value = self.activateCallback()
		if (self.getValueCallback):
			self.value = self.getValueCallback()

	def inc(self, multiplicator=1):
		prevValue=self.value
		if self.enableAccel:
			self.value += (self.incDecValues * multiplicator)
		else:
			self.value += self.incDecValues
		if (self.value>self.max): 
			self.value=self.max
		if (prevValue!=self.value):
			if (self.valueChangeCallback is not None):
				self.valueChangeCallback(prevValue,self.value)
			return True
		else:
			return False

	def dec(self, multiplicator=1):
		prevValue=self.value
		if self.enableAccel:
			self.value -= (self.incDecValues * multiplicator)
		else:
			self.value -= self.incDecValues
		if (self.value<self.min): 
			self.value=self.min
		if (prevValue!=self.value):
			if (self.valueChangeCallback is not None):
				self.valueChangeCallback(prevValue,self.value)
			return True
		else:
			return False
  
	def apply(self):
		if (self.callback is not None):
			if (self.type == LineItemType.SubMenu or self.type == LineItemType.Callback):
				self.callback()
			else:
				self.callback(self.value)
			return True
		return False

  



class SubMenu:
    
	TROWS = 6
	MROWS = TROWS - 1  # Total rows, and other-than-Back
	TITLE_HEIGHT = 30  # Title bar height
	LINE_HIGH = 53         # Menu line height
	LBLX = 60          # Menu item label X
	MENU_CHR_W = 8
	STAT_CHR_W = 10
	# ICON ID
	ICON = 0x09
 
	ICON_More = 26

	def __init__(self, lcd : type[T5UIC1_LCD], exitCallback):
		self.exitCallback = exitCallback
		self.lcd=lcd			# T5UIC1_LCD
		self.numItems=0
		self.topItem=0			# Item at top of screen
		self.selectedItem=0		# actual selected item
		self.menuItems=[]
		self.menuItemActive=False	# item value input is active

	def addItem(self, item : type[MenuItem]):
		self.menuItems.append(item)

	def MBASE(self, lineNumber):
		return 49 + self.LINE_HIGH * lineNumber
	
	def _drawSubMenuIcon(self, line):
		self.lcd.ICON_Show(self.ICON, self.ICON_More, 226, self.MBASE(line) - 3)

	def _drawMenuCursor(self, line=None):
		line = self.selectedItem - self.topItem
		self.lcd.Draw_Rectangle(1, self.lcd.Rectangle_Color, 0, self.MBASE(line) - 18, 14, self.MBASE(line + 1) - 20)
	def _eraseMenuCursor(self, line=None):
		line = self.selectedItem - self.topItem
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black,  0, self.MBASE(line) - 18, 14, self.MBASE(line + 1) - 20)

	def _drawMenuIcon(self, line, icon):
		self.lcd.ICON_Show(self.ICON, icon, 26, self.MBASE(line) - 3)

	def _drawMenuLine(self, line, icon=False, label=False):
		itemIndex = line + self.topItem
		if (icon):
			self._drawMenuIcon(line, icon)
		if (label):
			self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, self.LBLX, self.MBASE(line) - 1, label)
		if (self.menuItems[itemIndex].type == LineItemType.SubMenu):
			self._drawSubMenuIcon(line)
		self.menuItems[itemIndex].activate()
		self._drawItemValue(line)
		self.lcd.Draw_Line(self.lcd.Line_Color, 16, self.MBASE(line) + 33, 256, self.MBASE(line) + 34)

	def _drawMenuAll(self):
		for line in range(0,self.TROWS):
			itemIndex = line + self.topItem
			if (itemIndex < len(self.menuItems)):
				#print("_drawMenuAll %d %d" % (itemIndex, len(self.menuItems	)))
				self._drawMenuLine(line, self.menuItems[itemIndex].icon, self.menuItems[itemIndex].label)
		self._drawMenuCursor()
  
	def activate(self):
		self.topItem=0			# Item at top of screen
		self.selectedItem=0		# actual selected item
		self._drawMenuAll()
		self.lcd.UpdateLCD()
               
	def _drawItemValue(self, line):
		try:
			itemIndex = line + self.topItem
			if (self.menuItems[itemIndex].type == LineItemType.Int):
				self.lcd.Draw_IntValue(
				True, True, 0, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black,
				self.menuItems[itemIndex].iDigits, 
				216, self.MBASE(line), 
				self.menuItems[itemIndex].value)
			if (self.menuItems[itemIndex].type == LineItemType.Float):
				self.lcd.Draw_FloatValue(
				True, True, 0, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black,
				self.menuItems[itemIndex].iDigits, self.menuItems[itemIndex].fDigits,
				216, self.MBASE(line), 
				self.menuItems[itemIndex].value * (10 ** self.menuItems[itemIndex].fDigits))
			if (self.menuItems[itemIndex].type == LineItemType.SignedFloat):
				self.lcd.Draw_Signed_Float(
				self.lcd.font8x16, self.lcd.Color_Bg_Black, 
    			self.menuItems[itemIndex].iDigits, self.menuItems[itemIndex].fDigits, 
     			216, self.MBASE(line), 
				self.menuItems[itemIndex].value * (10 ** self.menuItems[itemIndex].fDigits))
		except Exception  as e: 
			print(e)
			traceback.print_exc()
			debugpy.breakpoint()

	def _drawActiveItemValue(self, initFromSystem=True):
		try:
			itemIndex = self.selectedItem
			line = itemIndex - self.topItem
			if initFromSystem:
				self.menuItems[itemIndex].activate()	# read value from system
			if (self.menuItems[itemIndex].type == LineItemType.Int):
				self.lcd.Draw_IntValue(
					True, True, 0, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Select_Color,
					self.menuItems[itemIndex].iDigits, 
					216, self.MBASE(line), 
					self.menuItems[itemIndex].value)
			if (self.menuItems[itemIndex].type == LineItemType.Float):
				self.lcd.Draw_FloatValue(
					True, True, 0, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Select_Color,
					self.menuItems[itemIndex].iDigits, self.menuItems[itemIndex].fDigits,
					216, self.MBASE(line), 
					self.menuItems[itemIndex].value * (10 ** self.menuItems[itemIndex].fDigits))
			if (self.menuItems[itemIndex].type == LineItemType.SignedFloat):
				self.lcd.Draw_Signed_Float(
					self.lcd.font8x16, self.lcd.Select_Color, 
	    			self.menuItems[itemIndex].iDigits, self.menuItems[itemIndex].fDigits, 
	     			216, self.MBASE(line), 
					self.menuItems[itemIndex].value * (10 ** self.menuItems[itemIndex].fDigits))
		except Exception  as e: 
			print(e)
			traceback.print_exc()
			debugpy.breakpoint()

	def _handleMenuSelection(self, encoderState):
		if (encoderState == ENCODER_DIFF_CW):
			newSelection = self.selectedItem + 1
			if (newSelection < len(self.menuItems)):
				self._eraseMenuCursor()
				self.selectedItem = newSelection
				if (self.selectedItem >= (self.topItem+self.TROWS)):	# scroll
					self.topItem += 1
					self.lcd.Frame_AreaMove(1, 2, self.LINE_HIGH, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, 349)
					self._drawMenuLine(self.TROWS-1, self.menuItems[self.selectedItem].icon, self.menuItems[self.selectedItem].label)
				self._drawMenuCursor()

		elif (encoderState == ENCODER_DIFF_CCW):
			newSelection = self.selectedItem - 1
			if (newSelection >= 0):
				self._eraseMenuCursor()
				self.selectedItem = newSelection
				if (self.selectedItem < self.topItem):		# scroll
					self.topItem = self.selectedItem
					self.lcd.Frame_AreaMove(1, 3, self.LINE_HIGH, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, 349)
					self._drawMenuLine(0, self.menuItems[self.selectedItem].icon, self.menuItems[self.selectedItem].label)
				self._drawMenuCursor()

		elif (encoderState == ENCODER_DIFF_ENTER):
			if (self.menuItems[self.selectedItem].type == LineItemType.Callback):
				self.menuItems[self.selectedItem].callback()
			elif (self.menuItems[self.selectedItem].type == LineItemType.SubMenu):
				self.menuItems[self.selectedItem].callback()
			else:
				self._drawActiveItemValue(True)
				self.menuItemActive = True
			self.lcd.UpdateLCD()
			
	def _handleMenuItem(self, encoderState, multiplicator=1):
		if (encoderState == ENCODER_DIFF_CW):
			#debugpy.breakpoint()
			self.menuItems[self.selectedItem].inc(multiplicator)
			self._drawActiveItemValue(False)
			self.lcd.UpdateLCD()
			return True
		if (encoderState == ENCODER_DIFF_CCW):
			self.menuItems[self.selectedItem].dec(multiplicator)
			self._drawActiveItemValue(False)
			self.lcd.UpdateLCD()
			return True
		if (encoderState == ENCODER_DIFF_ENTER):
			self.menuItemActive = False
			itemIndex = self.selectedItem
			line = itemIndex - self.topItem
			if (self.menuItems[itemIndex].apply()):
				self._drawMenuLine(line, self.menuItems[itemIndex].icon, self.menuItems[itemIndex].label)
				self.lcd.UpdateLCD()
				return True
			self._drawMenuLine(line, self.menuItems[itemIndex].icon, self.menuItems[itemIndex].label)
			self.lcd.UpdateLCD()
		return False

			
	def handleInput(self, encoderState, multiplicator=1):
		if (encoderState == ENCODER_DIFF_NO):
			return
		if (self.menuItemActive):
			self._handleMenuItem(encoderState, multiplicator)
		else:
			self._handleMenuSelection(encoderState)
   
   
   
   
   
class PrinterMenues:
	pd = None
	lcd = None
	mainMenuCallback = None

	STATUS_Y = 357
 
	TuneMenu    = None
	PrepareMenu = None
	ControlMenu = None
	prepMoveMenu= None
	ctrlTempMenu= None
	ctrlMotionMenu= None
	prepPlaMenu  = None
	prepAbsMenu  = None
 
	_activeMenu = None

	_menuStack = []

	def __init__(self, pd : type[PrinterData], lcd : type[T5UIC1_LCD], mainMenuCallback):
		self.pd = pd
		self.lcd= lcd
		self.mainMenuCallback=mainMenuCallback

		self.TuneMenu    = SubMenu(self.lcd, self.mainMenuCallback)
		self.PrepareMenu = SubMenu(self.lcd, self.mainMenuCallback)
		self.ControlMenu = SubMenu(self.lcd, self.mainMenuCallback)

 
	def zoffsetLiveCallback(self, previous, current):
		if self.pd is not None:
			if (previous<current):
				self.pd.add_mm('Z',  0.01)
			if (previous>current):
				self.pd.add_mm('Z', -0.01)

 
	def setup(self):
		self.mainBack=MenuItem(ICON_Back, "Back", LineItemType.Callback, self.mainMenuCallback, None)
		self.back    =MenuItem(ICON_Back, "Back", LineItemType.Callback, self.backCallback, None)

		#TuneMenu Items   ..........................................................................
		self.speed =  MenuItem(ICON_Speed,    "Printing Speed", LineItemType.Int, self.pd.set_feedrate,  self.pd.get_feedrate, 10, 400, True)
		self.flow  =  MenuItem(ICON_Extruder, "Flow Speed",     LineItemType.Int, self.pd.set_flowrate,  self.pd.get_flowrate,  1, 400, True)
		self.fspeed=  MenuItem(ICON_FanSpeed, "Fan Speed",      LineItemType.Int, self.pd.set_fanspeed,  self.pd.get_fanspeed,  0, 100, True)
		self.zoffset= MenuItem(ICON_Zoffset,  "Z-offset ", LineItemType.SignedFloat, self.pd.offset_z,   self.pd.getOffset_z,  -20, 20, False)
		self.zoffset.setDigits(1,2)
		self.zoffset.setIncValue(0.01)
		self.zoffset.setValueChangeCallback(self.zoffsetLiveCallback)
		self.reLength=MenuItem(ICON_ReadEEPROM,"Retract length",  LineItemType.Float, self.pd.set_fw_retract_length, self.pd.get_fw_retract_length,  0.0, 10.0, True)
		self.reSpeed= MenuItem(ICON_Speed,      "Retract speed",  LineItemType.Float, self.pd.set_fw_retract_speed,  self.pd.get_fw_retract_speed,   0.0, 80.0, True)
		self.unSpeed= MenuItem(ICON_WriteEEPROM,"Unretract speed",LineItemType.Float, self.pd.set_fw_unretract_speed,self.pd.get_fw_unretract_speed, 0.0, 80.0, True)
		self.exLength=MenuItem(ICON_More,       "Extra length",   LineItemType.Int,   self.pd.set_fw_unretract_extra_length,self.pd.get_fw_unretract_extra_length,  0.0, 10.0, True)

		self.TuneMenu.addItem(self.mainBack)
		self.TuneMenu.addItem(self.speed)
		self.TuneMenu.addItem(self.flow)
		self.TuneMenu.addItem(self.fspeed)
		self.TuneMenu.addItem(self.zoffset)
		self.TuneMenu.addItem(self.reLength)
		self.TuneMenu.addItem(self.reSpeed)
		self.TuneMenu.addItem(self.unSpeed)
		self.TuneMenu.addItem(self.exLength)
  
		# PrepareMenu Items  ..........................................................................
		self.prepMove    =  MenuItem(ICON_Axis,       "Move",            LineItemType.SubMenu,     self.activatePrepMove)
		self.prepDisStep =  MenuItem(ICON_CloseMotor, "Disable stepper", LineItemType.Callback,    self.pd.disableSteppers)
		self.prepHoming  =  MenuItem(ICON_Homing,     "Auto home",       LineItemType.Callback,    self.activateAutoHome)
		self.prepOffset  =  MenuItem(ICON_SetHome,    "Z-Offset",        LineItemType.SignedFloat, self.pd.offset_z,   self.pd.getOffset_z,  -20, 20, False)
		self.prepOffset.setActivateCallback(self.pd.probe_calibrate) # homing berfore adjust hight
		self.prepOffset.setDigits(1,2)
		self.prepOffset.setIncValue(0.01)
		self.prepOffset.setValueChangeCallback(self.zoffsetLiveCallback)
		self.prepPrePLA  =  MenuItem(ICON_PLAPreheat, "Preheat PLA",      LineItemType.Callback,    self.activatePreheatPLA)
		self.prepPreABS  =  MenuItem(ICON_ABSPreheat, "Preheat ABS",      LineItemType.Callback,    self.activatePreheatABS)
		self.prepCool    =  MenuItem(ICON_Cool,       "Cooldown",         LineItemType.Callback,    self.pd.disable_all_heaters)
  
		self.PrepareMenu.addItem(self.mainBack)
		self.PrepareMenu.addItem(self.prepMove)
		self.PrepareMenu.addItem(self.prepDisStep)
		self.PrepareMenu.addItem(self.prepHoming)
		self.PrepareMenu.addItem(self.prepOffset)
		self.PrepareMenu.addItem(self.prepPrePLA)
		self.PrepareMenu.addItem(self.prepPreABS)
		self.PrepareMenu.addItem(self.prepCool)

		# prepMoveMenu Items
		self.prepMoveX =  MenuItem(ICON_MoveX,    "Move X", LineItemType.Float, self.pd.setCurrentPositionX,  self.pd.getCurrentPositionX, self.pd.X_MIN_POS, self.pd.X_MAX_POS, True)
		self.prepMoveY =  MenuItem(ICON_MoveY,    "Move Y", LineItemType.Float, self.pd.setCurrentPositionY,  self.pd.getCurrentPositionY, self.pd.Y_MIN_POS, self.pd.Y_MAX_POS, True)
		self.prepMoveZ =  MenuItem(ICON_MoveZ,    "Move Z", LineItemType.Float, self.pd.setCurrentPositionZ,  self.pd.getCurrentPositionZ, self.pd.Z_MIN_POS, self.pd.Z_MAX_POS, True)
		self.prepMoveE =  MenuItem(ICON_Extruder, "Move Extruder", LineItemType.SignedFloat, self.pd.setCurrentPositionE,  self.pd.getCurrentPositionE, -50, 50, True)
		self.prepMoveX.setDigits(3,1)
		self.prepMoveY.setDigits(3,1)
		self.prepMoveZ.setDigits(3,1)

		self.prepMoveMenu= SubMenu(self.lcd, self.backCallback)
		self.prepMoveMenu.addItem(self.back)
		self.prepMoveMenu.addItem(self.prepMoveX)
		self.prepMoveMenu.addItem(self.prepMoveY)
		self.prepMoveMenu.addItem(self.prepMoveZ)
		self.prepMoveMenu.addItem(self.prepMoveE)
  
		# ControlMenu Items  ..........................................................................
		self.ctrlTemp  =  MenuItem(ICON_Temperature, "Temperature",    LineItemType.SubMenu,     self.activateCtrlTemp)
		self.ctrlMotion=  MenuItem(ICON_Motion,      "Motion",         LineItemType.SubMenu,     self.activateCtrlMotion)
		self.klRestart =  MenuItem(ICON_Contact,     "Klipper restart",LineItemType.Callback,    self.pd.klipper_restart)
		self.fwRestart =  MenuItem(ICON_Contact,     "FW restart",     LineItemType.Callback,    self.pd.mcu_fw_restart)
		self.hoRestart =  MenuItem(ICON_Contact,     "Host restart",   LineItemType.Callback,    self.pd.host_restart)
		self.hoShutdown=  MenuItem(ICON_Contact,     "Host shutdown",  LineItemType.Callback,    self.pd.host_shutdown)

		self.ControlMenu.addItem(self.mainBack)
		self.ControlMenu.addItem(self.ctrlTemp)
		#self.ControlMenu.addItem(self.ctrlMotion)
		self.ControlMenu.addItem(self.klRestart)
		self.ControlMenu.addItem(self.fwRestart)
		self.ControlMenu.addItem(self.hoRestart)
		self.ControlMenu.addItem(self.hoShutdown)

		#
		self.nozzleTemp= MenuItem(ICON_SetEndTemp,   "Nozzle Temperature",  LineItemType.Int, self.pd.setExtTemp, self.pd.getExtTempTarget, self.pd.MIN_E_TEMP,   self.pd.MAX_E_TEMP, True)
		self.bedTemp   = MenuItem(ICON_SetEndTemp,   "Bed Temperature",     LineItemType.Int, self.pd.setBedTemp, self.pd.getBedTempTarget, self.pd.MIN_BED_TEMP, self.pd.BED_MAX_TARGET, True)
		self.fanSpeed  = MenuItem(ICON_SetEndTemp,   "Fan speed",           LineItemType.Int, self.pd.set_fanspeed,self.pd.getActFanspeed, self.pd.MIN_E_TEMP, self.pd.MAX_E_TEMP, True)
		self.setPrePla = MenuItem(ICON_SetPLAPreheat,"Preheat PLS settings",LineItemType.SubMenu,     self.activatePrepPla)
		self.setPreAbs = MenuItem(ICON_SetABSPreheat,"Preheat ABS settings",LineItemType.SubMenu,     self.activatePrepAbs)

		self.ctrlTempMenu= SubMenu(self.lcd, self.backCallback)
		self.ctrlTempMenu.addItem(self.back)
		self.ctrlTempMenu.addItem(self.nozzleTemp)
		self.ctrlTempMenu.addItem(self.bedTemp)
		self.ctrlTempMenu.addItem(self.fanSpeed)
		self.ctrlTempMenu.addItem(self.setPrePla)
		self.ctrlTempMenu.addItem(self.setPreAbs)
		
		#
		self.nozzleTempPla= MenuItem(ICON_SetEndTemp,   "Nozzle Temperature",  LineItemType.Int, self.pd.setMaterialPresetHotendPLA, self.pd.getMaterialPresetHotendPLA, self.pd.MIN_E_TEMP, self.pd.MAX_E_TEMP, True)
		self.bedTempPla   = MenuItem(ICON_SetEndTemp,   "Bed Temperature",     LineItemType.Int, self.pd.setMaterialPresetBedPLA,    self.pd.getMaterialPresetBedPLA,    self.pd.MIN_BED_TEMP, self.pd.BED_MAX_TARGET, True)

		self.prepPlaMenu = SubMenu(self.lcd, self.backCallback)
		self.prepPlaMenu.addItem(self.back)
		self.prepPlaMenu.addItem(self.nozzleTempPla)
		self.prepPlaMenu.addItem(self.bedTempPla)
  
		#
		self.nozzleTempAbs= MenuItem(ICON_SetEndTemp,   "Nozzle Temperature",  LineItemType.Int, self.pd.setMaterialPresetHotendABS, self.pd.getMaterialPresetHotendABS, self.pd.MIN_E_TEMP, self.pd.MAX_E_TEMP, True)
		self.bedTempAbs   = MenuItem(ICON_SetEndTemp,   "Bed Temperature",     LineItemType.Int, self.pd.setMaterialPresetBedABS,    self.pd.getMaterialPresetBedABS,    self.pd.MIN_BED_TEMP, self.pd.BED_MAX_TARGET, True)

		self.prepAbsMenu = SubMenu(self.lcd, self.backCallback)
		self.prepAbsMenu.addItem(self.back)
		self.prepAbsMenu.addItem(self.nozzleTempAbs)
		self.prepAbsMenu.addItem(self.bedTempAbs)

		#
		self.ctrlMotionMenu= SubMenu(self.lcd, self.backCallback)







	## General purpose functions ---------------------------------------------
	def Clear_Title_Bar(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Blue, 0, 0, self.lcd.DWIN_WIDTH, 30)

	def Clear_Menu_Area(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, self.STATUS_Y)

	def Clear_Main_Window(self):
		self.Clear_Title_Bar()
		self.Clear_Menu_Area()

	## Dialog functions	-------------------------------------------------------
	def Popup_Window_Home(self, parking=False):
		self.Clear_Main_Window()
		self.Draw_Popup_Bkgd_60()
		self.lcd.ICON_Show(self.ICON, self.ICON_BLTouch, 101, 105)
		if parking:
			self.lcd.Draw_String(
				False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color, self.lcd.Color_Bg_Window,
				(272 - 8 * (7)) / 2, 230, "Parking")
		else:
			self.lcd.Draw_String(
				False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color, self.lcd.Color_Bg_Window,
				(272 - 8 * (10)) / 2, 230, "Homing XYZ")

		self.lcd.Draw_String(
			False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color, self.lcd.Color_Bg_Window,
			(272 - 8 * 23) / 2, 260, "Please wait until done.")

	def Popup_Window_ETempTooLow(self):
		self.Clear_Main_Window()
		self.Draw_Popup_Bkgd_60()
		self.lcd.ICON_Show(self.ICON, self.ICON_TempTooLow, 102, 105)
		self.lcd.Draw_String(
			False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color,
			self.lcd.Color_Bg_Window, 20, 235,
			"Nozzle is too cold"
		)
		self.lcd.ICON_Show(self.ICON, self.ICON_Confirm_E, 86, 280)

	## Item callback functions  ----------------------------------------------------------------
	# Activate submenus
	def activatePrepMove(self):
		self.activate(self.prepMoveMenu)
	def activateCtrlTemp(self):
		self.activate(self.ctrlTempMenu)
	def activateCtrlMotion(self):
		self.activate(self.ctrlMotionMenu)
	def activatePrepPla(self):
		self.activate(self.prepPlaMenu)
	def activatePrepAbs(self):
		self.activate(self.prepAbsMenu)

	def activateAutoHome(self):
		self.activate(self.prepMoveMenu)
		self.pd.current_position.homing()
		self.pd.HMI_flag.home_flag = True
		self.Popup_Window_Home()
		self.pd.sendGCode("G28")

	def activatePreheatPLA(self):
		self.pd.preheat("PLA")
	def activatePreheatABS(self):
		self.pd.preheat("ABS")

	# sub-menu "Back >""
	def backCallback(self):
		if (len(self._menuStack)>0) :
			self._activeMenu = self._menuStack.pop()
		else:
			self._activeMenu = None
		if self._activeMenu is not None:
			self.Clear_Main_Window()
			self._activeMenu.activate()
		else:
			self.mainMenuCallback()

	## Outside Interface ----------------------------------------------------------------
	# Call a main menu (PrintMenu | PrepareMenu | ControlMenu | tuneMenu)
	def activate(self, menu=None):
		if menu is None:
			menu = self.PrepareMenu	# for debugging only
		self._menuStack.append(self._activeMenu)  # previous menu
		self._activeMenu = menu
		self.Clear_Main_Window()
		self._activeMenu.activate()

	# handle encoder state change events
	def handleInput(self, encoderState, multiplicator=1):
		if (encoderState == ENCODER_DIFF_NO):
			return
		if self.pd.HMI_flag.home_flag:  # In homing mode
			return
		if self._activeMenu is not None:
			self._activeMenu.handleInput(encoderState, multiplicator)
   
	def periodicUpdate(self):
		if self.pd.HMI_flag.home_flag:  # HMI in homing mode
			if self.pd.ishomed():		# Homing done
				self._activeMenu.activate() # Re-Draw actal menu

