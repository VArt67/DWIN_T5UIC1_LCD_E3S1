import time
#import multitimer #mkocot
import threading #mkocot
import atexit
import debugpy

from encoder import Encoder
#from RPi import GPIO	#mkocot
from gpiozero import Button	#mkocot

from printerInterface import PrinterData
from DWIN_Screen import T5UIC1_LCD
from menuTest import PrinterMenues


def current_milli_time():
	return round(time.time() * 1000)

def startTimeMeasure(id):
    id = time.time()
    return id
    
def printElapsedTime(id, msg="Elapsed time: "):
    print(msg, time.time() - id)
    id = time.time()
    return id

def _MAX(lhs, rhs):
	if lhs > rhs:
		return lhs
	else:
		return rhs


def _MIN(lhs, rhs):
	if lhs < rhs:
		return lhs
	else:
		return rhs

class RepeatableTimer(threading.Timer):	#mkocot
	def run(self):
		while not self.finished.wait(self.interval):
			self.function(*self.args, **self.kwargs)

	def stop(self):
		self.cancel()

class select_t:
	now = 0
	last = 0

	def set(self, v):
		self.now = self.last = v

	def reset(self):
		self.set(0)

	def changed(self):
		c = (self.now != self.last)
		if c:
			self.last = self.now
			return c

	def dec(self):
		if (self.now):
			self.now -= 1
		return self.changed()

	def inc(self, v):
		if (self.now < (v - 1)):
			self.now += 1
		else:
			self.now = (v - 1)
		return self.changed()


class DWIN_LCD:

	TROWS = 6
	MROWS = TROWS - 1  # Total rows, and other-than-Back
	TITLE_HEIGHT = 30  # Title bar height
	MLINE = 53         # Menu line height
	LBLX = 60          # Menu item label X
	MENU_CHR_W = 8
	STAT_CHR_W = 10

	dwin_abort_flag = False  # Flag to reset feedrate, return to Home

	MSG_STOP_PRINT = "Stop Print"
	MSG_PAUSE_PRINT = "Pausing..."

	DWIN_SCROLL_UP = 2
	DWIN_SCROLL_DOWN = 3

	select_page = select_t()
	select_file = select_t()
	select_print = select_t()
	select_prepare = select_t()

	select_control = select_t()
	select_axis = select_t()
	select_temp = select_t()
	select_motion = select_t()
	select_tune = select_t()
	select_PLA = select_t()
	select_ABS = select_t()

	index_file = MROWS
	index_prepare = MROWS
	index_control = MROWS
	index_leveling = MROWS
	index_tune = MROWS

	MainMenu = 0
	SelectFile = 1
	PrintProcess = 5
	
	# Last Process ID
	Last_Prepare = 21

	# Back Process ID
	Back_Main = 22
	Back_Print = 23

	Print_window = 33
	Popup_Window = 34

 
	MINUNITMULT = 10

	ENCODER_DIFF_NO = 0  # no state
	ENCODER_DIFF_CW = 1  # clockwise rotation
	ENCODER_DIFF_CCW = 2  # counterclockwise rotation
	ENCODER_DIFF_ENTER = 3   # click
	ENCODER_WAIT = 80
	ENCODER_WAIT_ENTER = 400 #sur (300)
	EncoderRateLimit = True


	dwin_zoffset = 0.0
	last_zoffset = 0.0

	# Picture ID
	Start_Process = 0
	Language_English = 1
	Language_Chinese = 2

	# ICON ID
	ICON = 0x09

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

	MENU_CHAR_LIMIT = 24
	STATUS_Y = 357 #was 360, change for display_info Y

	MOTION_CASE_RATE = 1
	MOTION_CASE_ACCEL = 2
	MOTION_CASE_JERK = MOTION_CASE_ACCEL + 0
	MOTION_CASE_STEPS = MOTION_CASE_JERK + 1
	MOTION_CASE_TOTAL = MOTION_CASE_STEPS

	PREPARE_CASE_MOVE = 1
	PREPARE_CASE_DISA = 2
	PREPARE_CASE_HOME = 3
	PREPARE_CASE_ZOFF = PREPARE_CASE_HOME + 1
	PREPARE_CASE_PLA = PREPARE_CASE_ZOFF + 1
	PREPARE_CASE_ABS = PREPARE_CASE_PLA + 1
	PREPARE_CASE_COOL = PREPARE_CASE_ABS + 1
	PREPARE_CASE_LANG = PREPARE_CASE_COOL + 0
	PREPARE_CASE_TOTAL = PREPARE_CASE_LANG

	CONTROL_CASE_TEMP = 1
	CONTROL_CASE_MOVE = 2
	#CONTROL_CASE_INFO = 3
	CONTROL_CASE_KLIPPER_RESTART = 3
	CONTROL_CASE_FW_RESTART = 4
	CONTROL_CASE_HOST_RESTART = 5
	CONTROL_CASE_HOST_SHUTDOWN = 6
	CONTROL_CASE_TOTAL = 6

	TUNE_CASE_SPEED = 1
	TUNE_CASE_FLOW = (TUNE_CASE_SPEED + 1)
	TUNE_CASE_FAN = (TUNE_CASE_FLOW + 1)	# + fan
	TUNE_CASE_ZOFF = (TUNE_CASE_FAN + 1)
	TUNE_CASE_RETRACT_L = (TUNE_CASE_ZOFF + 1)		# + fw_retract_length
	TUNE_CASE_RETRACT_S = (TUNE_CASE_RETRACT_L + 1)		# + fw_retract_speed
	TUNE_CASE_UNRETRACT_S = (TUNE_CASE_RETRACT_S + 1)	# + fw_unretract_speed
	TUNE_CASE_UNRETRACT_EXTRA_L = (TUNE_CASE_UNRETRACT_S + 1)		# + fw_unretract_extra_length
	TUNE_CASE_TOTAL = TUNE_CASE_UNRETRACT_EXTRA_L
	#TUNE_CASE_TEMP = (TUNE_CASE_ZOFF + 0)	# - CASE_TEMP
	#TUNE_CASE_BED = (TUNE_CASE_TEMP + 0)	# - CASE_BED

	TEMP_CASE_TEMP = (0 + 1)
	TEMP_CASE_BED = (TEMP_CASE_TEMP + 1)
	TEMP_CASE_FAN = (TEMP_CASE_BED + 1)	#sur+1 fan menu
	TEMP_CASE_PLA = (TEMP_CASE_FAN + 1)
	TEMP_CASE_ABS = (TEMP_CASE_PLA + 1)
	TEMP_CASE_TOTAL = TEMP_CASE_ABS

	PREHEAT_CASE_TEMP = (0 + 1)
	PREHEAT_CASE_BED = (PREHEAT_CASE_TEMP + 1)
	PREHEAT_CASE_FAN = (PREHEAT_CASE_BED + 0)
	PREHEAT_CASE_SAVE = (PREHEAT_CASE_FAN + 1)
	PREHEAT_CASE_TOTAL = PREHEAT_CASE_SAVE

	# Dwen serial screen initialization
	# Passing parameters: serial port number
	# DWIN screen uses serial port 1 to send
	def __init__(self, USARTx, encoder_pins, button_pin, octoPrint_API_Key):
		#GPIO.setmode(GPIO.BCM)	#mkocot
		print("Waiting for debugger attach")
		#debugpy.wait_for_client()
		self.encoder = Encoder(encoder_pins[0], encoder_pins[1])
		self.button_pin = button_pin
		#GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#mkocot
		#GPIO.add_event_detect(self.button_pin, GPIO.BOTH, callback=self.encoder_has_data)	#mkocot
		self.button = Button(button_pin)	#mkocot
		self.button.when_pressed = self.encoder_has_data	#mkocot
		self.encoder.callback = self.encoder_has_data
		self.EncodeLast = 0
		self.EncodeMS = current_milli_time() + self.ENCODER_WAIT
		self.EncodeEnter = current_milli_time() + self.ENCODER_WAIT_ENTER
		self.next_rts_update_ms = 0
		self.last_cardpercentValue = 101
		self.lcdLock = threading.RLock()  # encoder_has_data & EachMomentUpdate threads
		self.lcd = T5UIC1_LCD(USARTx)
		self.lcd.Backlight_SetLuminance(0x14) #Sur 20
		self.HMI_ShowBoot("Initializing ...")
		self.checkkey = self.MainMenu
		self.pd = PrinterData(octoPrint_API_Key)
		self.HMI_progress(5)
		self.timer = RepeatableTimer(
			interval=0.25, function=self.EachMomentUpdate) #sur interval 1(2)
		self.HMI_progress(10)
		#self.HMI_AudioFeedback(True) #Sur?
		print("Boot looks good")
		print("Testing Web-services")
		self.HMI_progress(15)
		self.pd.init_Webservices()
		self.HMI_progress(20)
		for i in range(1,4):
			self.HMI_progress(i*25)
			time.sleep(1)
		while self.pd.status is None:
			print("No Web-services. Next try ...")
			self.pd.init_Webservices()
			self.HMI_ShowBoot("Web-service still loading")
			time.sleep(1);
		self.HMI_progress(80)
		self.HMI_Init()
		self.HMI_progress(98)
		self.HMI_StartFrame(False)
		self.printerMenues = PrinterMenues(self.pd, self.lcd, self.HMI_StartFrame)
		self.printerMenues.setup()
		print("Init ready")

	def lcdExit(self):
		print("Shutting down the LCD")
		self.lcd.JPG_ShowAndCache(0)
		self.lcd.Frame_SetDir(1)
		self.lcd.UpdateLCD()
		self.timer.stop()
		#GPIO.remove_event_detect(self.button_pin)	#mkocot
		self.button.close()	#mkocot

	def MBASE(self, L):
		return 49 + self.MLINE * L

	def HMI_SetLanguageCache(self):
		self.lcd.JPG_CacheTo1(self.Language_English)

	def HMI_SetLanguage(self):
		self.HMI_SetLanguageCache()

	def HMI_progress(self, percentage):
			self.lcd.ICON_Show(self.ICON, self.ICON_Bar, 15, 260)
			self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 15 + percentage * 242 / 100, 260, 257, 280)
			self.lcd.UpdateLCD()

	def HMI_ShowBoot(self, mesg=None):
		if mesg:
			self.lcd.Draw_String(
				False, False, self.lcd.DWIN_FONT_STAT,
				self.lcd.Color_White, self.lcd.Color_Bg_Black,
				10, 50,
				mesg
			)
		self.HMI_progress(0)
		return
		for t in range(0, 100, 2):
			self.lcd.ICON_Show(self.ICON, self.ICON_Bar, 15, 260)
			self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 15 + t * 242 / 100, 260, 257, 280)
			self.lcd.UpdateLCD()
			time.sleep(.020)

	def HMI_Init(self):
		# HMI_SDCardInit()

		self.HMI_SetLanguage()
		self.timer.start()
		atexit.register(self.lcdExit)

	def HMI_StartFrame(self, with_update=True):
		self.EncoderRateLimit = True		
		self.last_status = self.pd.status
		if self.pd.status == 'printing':
			self.Goto_PrintProcess()
		elif self.pd.status in ['operational', 'complete', 'standby', 'cancelled']:
			self.Goto_MainMenu()
		else:
			self.Goto_MainMenu()
		self.Draw_Status_Area(with_update)

	def HMI_MainMenu(self):
		encoder_diffState = self.get_encoder_state()
		if (encoder_diffState == self.ENCODER_DIFF_NO):
			return
		if (encoder_diffState == self.ENCODER_DIFF_CW):
			if(self.select_page.inc(4)):
				if self.select_page.now == 0:
					self.ICON_Print()
				if self.select_page.now == 1:
					self.ICON_Print()
					self.ICON_Prepare()
				if self.select_page.now == 2:
					self.ICON_Prepare()
					self.ICON_Control()
				if self.select_page.now == 3:
					self.ICON_Control()
					if self.pd.HAS_ONESTEP_LEVELING:
						self.ICON_Leveling(True)
					else:
						self.ICON_StartTune(True)	#self.ICON_StartInfo(True)
		elif (encoder_diffState == self.ENCODER_DIFF_CCW):
			if (self.select_page.dec()):
				if self.select_page.now == 0:
					self.ICON_Print()
					self.ICON_Prepare()
				elif self.select_page.now == 1:
					self.ICON_Prepare()
					self.ICON_Control()
				elif self.select_page.now == 2:
					self.ICON_Control()
					if self.pd.HAS_ONESTEP_LEVELING:
						self.ICON_Leveling(False)
					else:
						self.ICON_StartTune(False)	#self.ICON_StartInfo(False)
				elif self.select_page.now == 3:
					if self.pd.HAS_ONESTEP_LEVELING:
						self.ICON_Leveling(True)
					else:
						self.ICON_StartTune(True)	#self.ICON_StartInfo(True)
		elif (encoder_diffState == self.ENCODER_DIFF_ENTER):
			if self.select_page.now == 0:  # Print File
				self.checkkey = self.SelectFile
				self.Draw_Print_File_Menu()
			if self.select_page.now == 1:  # Prepare
				self.checkkey = self.Prepare
				self.select_prepare.reset()
				self.index_prepare = self.MROWS
				self.Draw_Prepare_Menu()
			if self.select_page.now == 2:  # Control
				self.checkkey = self.Control
				self.select_control.reset()
				self.index_control = self.MROWS
				self.Draw_Control_Menu()
			if self.select_page.now == 3:  # Leveling or Info
				if self.pd.HAS_ONESTEP_LEVELING:
					self.checkkey = self.Leveling
					self.HMI_Leveling()
				else:
					#self.checkkey = self.Info
					#self.Draw_Info_Menu()
					self.checkkey = self.Tune	#tune sur
					self.Draw_Tune_Menu()

		self.lcd.UpdateLCD()

	def HMI_SelectFile(self):
		encoder_diffState = self.get_encoder_state()
		if (encoder_diffState == self.ENCODER_DIFF_NO):
			return

		fullCnt = len(self.pd.GetFiles(refresh=True))

		if (encoder_diffState == self.ENCODER_DIFF_CW and fullCnt):
			if (self.select_file.inc(1 + fullCnt)):
				itemnum = self.select_file.now - 1  # -1 for "Back"
				if (self.select_file.now > self.MROWS and self.select_file.now > self.index_file):  # Cursor past the bottom
					self.index_file = self.select_file.now  # New bottom line
					self.Scroll_Menu(self.DWIN_SCROLL_UP)
					self.Draw_SDItem(itemnum, self.MROWS)  # Draw and init the shift name
				else:
					self.Move_Highlight(1, self.select_file.now + self.MROWS - self.index_file)  # Just move highlight
		elif (encoder_diffState == self.ENCODER_DIFF_CCW and fullCnt):
			if (self.select_file.dec()):
				itemnum = self.select_file.now - 1  # -1 for "Back"
				if (self.select_file.now < self.index_file - self.MROWS):  # Cursor past the top
					self.index_file -= 1  # New bottom line
					self.Scroll_Menu(self.DWIN_SCROLL_DOWN)
					if (self.index_file == self.MROWS):
						self.Draw_Back_First()
					else:
						self.Draw_SDItem(itemnum, 0)  # Draw the item (and init shift name)
				else:
					self.Move_Highlight(-1, self.select_file.now + self.MROWS - self.index_file)  # Just move highlight
		elif (encoder_diffState == self.ENCODER_DIFF_ENTER):
			if (self.select_file.now == 0):  # Back
				self.select_page.set(0)
				self.Goto_MainMenu()
			else:
				filenum = self.select_file.now - 1
				# Reset highlight for next entry
				self.select_print.reset()
				self.select_file.reset()

				# // Start choice and print SD file
				self.pd.HMI_flag.heat_flag = True
				self.pd.HMI_flag.print_finish = False
				self.pd.HMI_ValueStruct.show_mode = 0

				self.pd.openAndPrintFile(filenum)
				self.Goto_PrintProcess()

		self.lcd.UpdateLCD()

	def HMI_Prepare(self):
		encoder_diffState = self.get_encoder_state()
		self.printerMenues.handleInput(encoder_diffState, self.encoder.diffValue)
		return

	def HMI_Control(self):
		encoder_diffState = self.get_encoder_state()
		self.printerMenues.handleInput(encoder_diffState, self.encoder.diffValue)
		return

	def HMI_Info(self):
		encoder_diffState = self.get_encoder_state()
		if (encoder_diffState == self.ENCODER_DIFF_NO):
			return
		if (encoder_diffState == self.ENCODER_DIFF_ENTER):
			# if self.pd.HAS_ONESTEP_LEVELING:
			# 	self.checkkey = self.Control
			# 	self.select_control.set(self.CONTROL_CASE_INFO)
			# 	self.Draw_Control_Menu()
			# else:
			# 	self.select_page.set(3)
			# 	self.Goto_MainMenu()

			self.select_page.set(3)
			self.Goto_MainMenu()

		self.lcd.UpdateLCD()

	def HMI_Printing(self):
		encoder_diffState = self.get_encoder_state()
		if (encoder_diffState == self.ENCODER_DIFF_NO):
			return
		if (self.pd.HMI_flag.done_confirm_flag):
			if (encoder_diffState == self.ENCODER_DIFF_ENTER):
				self.pd.HMI_flag.done_confirm_flag = False
				self.dwin_abort_flag = True  # Reset feedrate, return to Home
			return

		if (encoder_diffState == self.ENCODER_DIFF_CW):
			if (self.select_print.inc(3)):
				if self.select_print.now == 0:
					self.ICON_Tune()
				elif self.select_print.now == 1:
					self.ICON_Tune()
					if (self.pd.printingIsPaused()):
						self.ICON_Continue()
					else:
						self.ICON_Pause()
				elif self.select_print.now == 2:
					if (self.pd.printingIsPaused()):
						self.ICON_Continue()
					else:
						self.ICON_Pause()
					self.ICON_Stop()
		elif (encoder_diffState == self.ENCODER_DIFF_CCW):
			if (self.select_print.dec()):
				if self.select_print.now == 0:
					self.ICON_Tune()
					if (self.pd.printingIsPaused()):
						self.ICON_Continue()
					else:
						self.ICON_Pause()
				elif self.select_print.now == 1:
					if (self.pd.printingIsPaused()):
						self.ICON_Continue()
					else:
						self.ICON_Pause()
					self.ICON_Stop()
				elif self.select_print.now == 2:
					self.ICON_Stop()
		elif (encoder_diffState == self.ENCODER_DIFF_ENTER):
			if self.select_print.now == 0:  # Tune
				self.checkkey = self.Tune
				self.pd.HMI_ValueStruct.show_mode = 0
				self.select_tune.reset()
				self.index_tune = self.MROWS
				self.Draw_Tune_Menu()
			elif self.select_print.now == 1:  # Pause
				if (self.pd.HMI_flag.pause_flag):
					self.ICON_Pause()
					self.pd.resume_job()
				else:
					self.pd.HMI_flag.select_flag = True
					self.checkkey = self.Print_window
					self.Popup_window_PauseOrStop()
			elif self.select_print.now == 2:  # Stop
				self.pd.HMI_flag.select_flag = True
				self.checkkey = self.Print_window
				self.Popup_window_PauseOrStop()
		self.lcd.UpdateLCD()

	# Pause and Stop window */
	def HMI_PauseOrStop(self):
		encoder_diffState = self.get_encoder_state()
		if (encoder_diffState == self.ENCODER_DIFF_NO):
			return
		if (encoder_diffState == self.ENCODER_DIFF_CW):
			self.Draw_Select_Highlight(False)
		elif (encoder_diffState == self.ENCODER_DIFF_CCW):
			self.Draw_Select_Highlight(True)
		elif (encoder_diffState == self.ENCODER_DIFF_ENTER):
			if (self.select_print.now == 1):  # pause window
				if (self.pd.HMI_flag.select_flag):
					self.pd.HMI_flag.pause_action = True
					self.ICON_Continue()
					self.pd.pause_job()
				self.Goto_PrintProcess()
			elif (self.select_print.now == 2):  # stop window
				if (self.pd.HMI_flag.select_flag):
					self.dwin_abort_flag = True  # Reset feedrate, return to Home
					self.pd.cancel_job()
					self.Goto_MainMenu()
				else:
					self.Goto_PrintProcess()  # cancel stop
		self.lcd.UpdateLCD()

	# Tune  */
	def HMI_Tune(self):
		encoder_diffState = self.get_encoder_state()
		self.printerMenues.handleInput(encoder_diffState, self.encoder.diffValue)
		return



	# --------------------------------------------------------------#
	# --------------------------------------------------------------#

	def Draw_Status_Area(self, with_update):
		#  Clear the bottom area of the screen
		#not here self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, self.STATUS_Y, self.lcd.DWIN_WIDTH, self.lcd.DWIN_HEIGHT - 1)
		#
		#  Status Area
		#

		#display_status
		self.lcd.Draw_String(
			False, True, self.lcd.font8x16,
			self.lcd.Color_White, self.lcd.Color_Bg_Black,
			#(self.lcd.DWIN_WIDTH - len(self.pd.display_status) * self.STAT_CHR_W) / 2, 354,
			0, 358,
			self.pd.display_status.center(int(self.lcd.DWIN_WIDTH / self.MENU_CHR_W))
		)

		############# 1-st line Sur

		#temp_hotend
		if self.pd.HAS_HOTEND:
			self.lcd.ICON_Show(self.ICON, self.ICON_HotendTemp, 8, 382)
			self.lcd.Draw_IntValue(
				True, True, 0, self.lcd.DWIN_FONT_STAT,
				self.lcd.Color_White, self.lcd.Color_Bg_Black,
				3, 8 + 2 * self.STAT_CHR_W, 382,
				self.pd.thermalManager['temp_hotend'][0]['celsius']
			)
			self.lcd.Draw_String(
				False, False, self.lcd.DWIN_FONT_STAT,
				self.lcd.Color_White, self.lcd.Color_Bg_Black,
				26 + 3 * self.STAT_CHR_W + 5, 382,
				"/"
			)
			self.lcd.Draw_IntValue(
				True, True, 0, self.lcd.DWIN_FONT_STAT,
				self.lcd.Color_White, self.lcd.Color_Bg_Black, 3, 26 + 4 * self.STAT_CHR_W + 6, 382,
				self.pd.thermalManager['temp_hotend'][0]['target']
			)
		if self.pd.HOTENDS > 1:
			self.lcd.ICON_Show(self.ICON, self.ICON_HotendTemp, 8, 381)

		#feedrate %
		self.lcd.ICON_Show(self.ICON, self.ICON_Speed, 116, 382)
		self.lcd.Draw_IntValue(
			True, True, 0, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 3, 116 + 2 * self.STAT_CHR_W, 382,
			self.pd.feedrate_percentage
		)
		self.lcd.Draw_String(
			False, False, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 116 + 5 * self.STAT_CHR_W + 2, 382,
			"%"
		)

		#z-offset
		# if self.pd.HAS_ZOFFSET_ITEM:
		# 	self.lcd.ICON_Show(self.ICON, self.ICON_Zoffset, 192, 410)
		# 	self.lcd.Draw_Signed_Float(
		# 		self.lcd.DWIN_FONT_STAT,
		# 		self.lcd.Color_Bg_Black, 2, 2, 212, 410, 
		# 		self.pd.BABY_Z_VAR * 100
		# 	)

		#or gcode speed /60 for mm/s
		self.lcd.ICON_Show(self.ICON, self.ICON_Motion, 192, 382)
		self.lcd.Draw_Signed_Float(
			self.lcd.DWIN_FONT_STAT, 
			self.lcd.Color_Bg_Black, 3, 1, 195 + 2 * self.STAT_CHR_W, 382,
			self.pd.gcode_speed / 60 * 10 
		)
		# self.lcd.Draw_String(
		# 	False, False, self.lcd.DWIN_FONT_STAT,
		# 	self.lcd.Color_White, self.lcd.Color_Bg_Black, 202 + 5 * self.STAT_CHR_W + 2, 410,
		# 	"mm/s"
		# )

		############# 2-nd line

		#temp_bed
		if self.pd.HAS_HEATED_BED:
			self.lcd.ICON_Show(self.ICON, self.ICON_BedTemp, 8, 410)
			self.lcd.Draw_IntValue(
				True, True, 0, self.lcd.DWIN_FONT_STAT, self.lcd.Color_White,
				self.lcd.Color_Bg_Black, 3, 8 + 2 * self.STAT_CHR_W, 410,
				self.pd.thermalManager['temp_bed']['celsius']
			)
			self.lcd.Draw_String(
				False, False, self.lcd.DWIN_FONT_STAT, self.lcd.Color_White,
				self.lcd.Color_Bg_Black, 26 + 3 * self.STAT_CHR_W + 5, 410,
				"/"
			)
			self.lcd.Draw_IntValue(
				True, True, 0, self.lcd.DWIN_FONT_STAT,
				self.lcd.Color_White, self.lcd.Color_Bg_Black, 3, 26 + 4 * self.STAT_CHR_W + 6, 410,
				self.pd.thermalManager['temp_bed']['target']
			)

		#flowrate %
		self.lcd.ICON_Show(self.ICON, self.ICON_Extruder, 116, 410)
		self.lcd.Draw_IntValue(
			True, True, 0, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 3, 116 + 2 * self.STAT_CHR_W, 410,
			self.pd.flowrate_percentage
		)
		self.lcd.Draw_String(
			False, False, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 116 + 5 * self.STAT_CHR_W + 2, 410,
			"%"
		)

		#fan speed %
		self.lcd.ICON_Show(self.ICON, self.ICON_FanSpeed, 192, 410)
		self.lcd.Draw_IntValue(
			True, True, 0, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 3, 197 + 2 * self.STAT_CHR_W, 410,
			self.pd.thermalManager['fan_speed'][0]
		)
		self.lcd.Draw_String(
			False, False, self.lcd.DWIN_FONT_STAT,
			self.lcd.Color_White, self.lcd.Color_Bg_Black, 202 + 5 * self.STAT_CHR_W + 2, 410,
			"%"
		)

		################ 3-d line

		self.lcd.Draw_Line(self.lcd.Line_Color, 1, 440, 270, 440)

		#current X
		self.lcd.ICON_Show(self.ICON, self.ICON_MaxSpeedX, 6, 446)
		self.lcd.Draw_Signed_Float(
			self.lcd.DWIN_FONT_STAT, 
			self.lcd.Color_Bg_Black, 3, 1, 8 + 2 * self.STAT_CHR_W, 446,
			self.pd.current_position.x * 10
		)
		
		#current Y
		self.lcd.ICON_Show(self.ICON, self.ICON_MaxSpeedY, 94, 446)
		self.lcd.Draw_Signed_Float(
			self.lcd.DWIN_FONT_STAT, 
			self.lcd.Color_Bg_Black, 3, 1, 96 + 2 * self.STAT_CHR_W, 446,
			self.pd.current_position.y * 10
		)

		#current Z
		self.lcd.ICON_Show(self.ICON, self.ICON_MaxSpeedZ, 179, 446) #181
		self.lcd.Draw_Signed_Float(
			self.lcd.DWIN_FONT_STAT, 
			self.lcd.Color_Bg_Black, 3, 2, 183 + 2 * self.STAT_CHR_W, 446,
			self.pd.current_position.z * 100
		)

		# if with_update:
		# 	self.lcd.UpdateLCD()
		# 	time.sleep(.005)

	def Draw_Title(self, title):
		self.lcd.Draw_String(False, False, self.lcd.DWIN_FONT_HEAD, self.lcd.Color_White, self.lcd.Color_Bg_Blue, 14, 4, title)

	def Draw_Popup_Bkgd_105(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Window, 14, 105, 258, 374)

	def Draw_More_Icon(self, line):
		self.lcd.ICON_Show(self.ICON, self.ICON_More, 226, self.MBASE(line) - 3)

	def Draw_Menu_Cursor(self, line):
		self.lcd.Draw_Rectangle(1, self.lcd.Rectangle_Color, 0, self.MBASE(line) - 18, 14, self.MBASE(line + 1) - 20)

	def Draw_Menu_Icon(self, line, icon):
		self.lcd.ICON_Show(self.ICON, icon, 26, self.MBASE(line) - 3)

	def Draw_Menu_Line(self, line, icon=False, label=False):
		if (label):
			self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, self.LBLX, self.MBASE(line) - 1, label)
		if (icon):
			self.Draw_Menu_Icon(line, icon)
		self.lcd.Draw_Line(self.lcd.Line_Color, 16, self.MBASE(line) + 33, 256, self.MBASE(line) + 34)

	# The "Back" label is always on the first line
	def Draw_Back_Label(self):
		#self.lcd.Frame_AreaCopy(1, 226, 179, 256, 189, self.LBLX, self.MBASE(0))
		self.lcd.Draw_String(
			False, True, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BG,
			self.LBLX, self.MBASE(0),
			self.pd.s_BACK
		)
   
	# Draw "Back" line at the top
	def Draw_Back_First(self, is_sel=True):
		self.Draw_Menu_Line(0, self.ICON_Back)
		self.Draw_Back_Label()
		if (is_sel):
			self.Draw_Menu_Cursor(0)

	def draw_move_en(self, line):
		self.lcd.Frame_AreaCopy(1, 69, 61, 102, 71, self.LBLX, line)  # "Move"

	def draw_max_en(self, line):
		self.lcd.Frame_AreaCopy(1, 245, 119, 269, 129, self.LBLX, line)  # "Max"

	def draw_max_accel_en(self, line):
		self.draw_max_en(line)
		self.lcd.Frame_AreaCopy(1, 1, 135, 79, 145, self.LBLX + 27, line)  # "Acceleration"

	def draw_speed_en(self, inset, line):
		self.lcd.Frame_AreaCopy(1, 184, 119, 224, 132, self.LBLX + inset, line)  # "Speed"

	def draw_jerk_en(self, line):
		self.lcd.Frame_AreaCopy(1, 64, 119, 106, 129, self.LBLX + 27, line)  # "Jerk"

	def draw_steps_per_mm(self, line):
		self.lcd.Frame_AreaCopy(1, 1, 151, 119, 161, self.LBLX, line)  # "Steps-per-mm" 101 -> 119

	# Display an SD item
	def Draw_SDItem(self, item, row=0):
		fl = self.pd.GetFiles()[item]
		self.Draw_Menu_Line(row, self.ICON_File, fl)

	def Draw_Select_Highlight(self, sel):
		self.pd.HMI_flag.select_flag = sel
		if sel:
			c1 = self.lcd.Select_Color
			c2 = self.lcd.Color_Bg_Window
		else:
			c1 = self.lcd.Color_Bg_Window
			c2 = self.lcd.Select_Color
		self.lcd.Draw_Rectangle(0, c1, 25, 279, 126, 318)
		self.lcd.Draw_Rectangle(0, c1, 24, 278, 127, 319)
		self.lcd.Draw_Rectangle(0, c2, 145, 279, 246, 318)
		self.lcd.Draw_Rectangle(0, c2, 144, 278, 247, 319)

	def Draw_Popup_Bkgd_60(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Window, 14, 60, 258, 330)

	def Draw_Printing_Screen(self):
		#self.lcd.Frame_AreaCopy(1, 40, 2, 92, 14, 14, 9)  # Printing
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BG, 14, 8, self.pd.s_PRINTING)
		#self.lcd.Frame_AreaCopy(1, 0, 44, 96, 58, 41, 188)  # Printing Time
		self.lcd.Draw_String(False, True, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BG, 41, 188, self.pd.s_TIME)
		#self.lcd.Frame_AreaCopy(1, 98, 44, 152, 58, 176, 188)  # Remain AreaCopy(1, 98, 44, 271 - 119, 479 - 420 - 1, 176, 188); // Stop
		#self.lcd.Frame_AreaCopy(1, 99, 44, 152, 57, 176, 188)  # Remain Sur
		self.lcd.Draw_String(False, True, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BG, 176, 188, self.pd.s_REMAIN)
  
	def Draw_Print_ProgressBar(self, Percentrecord=None):
		if not Percentrecord:
			Percentrecord = self.pd.getPercent()
		self.lcd.ICON_Show(self.ICON, self.ICON_Bar, 15, 93)
		self.lcd.Draw_Rectangle(1, self.lcd.BarFill_Color, 16 + Percentrecord * 240 / 100, 93, 256, 113)
		self.lcd.Draw_IntValue(True, True, 0, self.lcd.font8x16, self.lcd.Percent_Color, self.lcd.Color_Bg_Black, 2, 117, 133, Percentrecord)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Percent_Color, self.lcd.Color_Bg_Black, 133, 133, "%")

	def Draw_Print_ProgressElapsed(self):
		elapsed = self.pd.duration()  # print timer
		self.lcd.Draw_IntValue(True, True, 1, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 2, 42, 212, elapsed / 3600)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 58, 212, ":")
		self.lcd.Draw_IntValue(True, True, 1, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 2, 66, 212, (elapsed % 3600) / 60)

	def Draw_Print_ProgressRemain(self):
		remain_time = self.pd.remain()
		if not remain_time: return #time remaining is None during warmup.
		self.lcd.Draw_IntValue(True, True, 1, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 2, 176, 212, remain_time / 3600)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 192, 212, ":")
		self.lcd.Draw_IntValue(True, True, 1, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, 2, 200, 212, (remain_time % 3600) / 60)

	def Draw_Print_File_Menu(self):
		self.Clear_Title_Bar()
		#self.lcd.Frame_TitleCopy(1, 52, 31, 137, 41)  # "Print file"
		self.lcd.Draw_String(False, False, self.lcd.font10x20, self.lcd.Color_FG, self.lcd.Color_BGTitle, 14, 8, self.pd.s_PRINT_FILE)
		self.Redraw_SD_List()

	def Draw_Prepare_Menu(self):
		self.Clear_Main_Window()
		self.printerMenues.activate(self.printerMenues.PrepareMenu)
		self.EncoderRateLimit = False		
		return



	def Draw_Info_Menu(self):
		self.Clear_Main_Window()

		self.lcd.Draw_String(
			False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black,
			(self.lcd.DWIN_WIDTH - len(self.pd.MACHINE_SIZE) * self.MENU_CHR_W) / 2, 122,
			self.pd.MACHINE_SIZE
		)
		self.lcd.Draw_String(
			False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black,
			(self.lcd.DWIN_WIDTH - len(self.pd.SHORT_BUILD_VERSION) * self.MENU_CHR_W) / 2, 195,
			self.pd.SHORT_BUILD_VERSION
		)
		self.lcd.Frame_TitleCopy(1, 190, 16, 215, 26)  # "Info"
		self.lcd.Frame_AreaCopy(1, 120, 150, 146, 161, 124, 102)
		self.lcd.Frame_AreaCopy(1, 146, 151, 254, 161, 82, 175)
		self.lcd.Frame_AreaCopy(1, 0, 165, 94, 175, 89, 248)
		self.lcd.Draw_String(
			False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black,
			(self.lcd.DWIN_WIDTH - len(self.pd.CORP_WEBSITE_E) * self.MENU_CHR_W) / 2, 268,
			self.pd.CORP_WEBSITE_E
		)
		self.Draw_Back_First()
		for i in range(3):
			self.lcd.ICON_Show(self.ICON, self.ICON_PrintSize + i, 26, 99 + i * 73)
			self.lcd.Draw_Line(self.lcd.Line_Color, 16, self.MBASE(2) + i * 73, 256, 156 + i * 73)

	def Draw_Tune_Menu(self):
		#debugpy.breakpoint()
		self.Clear_Main_Window()
		self.printerMenues.activate(self.printerMenues.TuneMenu)
		self.EncoderRateLimit = False		
		return

	# --------------------------------------------------------------#
	# --------------------------------------------------------------#

	def Goto_MainMenu(self):
		self.checkkey = self.MainMenu
		self.Clear_Main_Window()

		#self.lcd.Frame_AreaCopy(1, 0, 2, 39, 12, 14, 9)	#Home
		self.lcd.Draw_String(False, True, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 14, 8, self.pd.s_HOME)
		self.lcd.ICON_Show(self.ICON, self.ICON_LOGO, 71, 52)

		self.ICON_Print()
		self.ICON_Prepare()
		self.ICON_Control()
		if self.pd.HAS_ONESTEP_LEVELING:
			self.ICON_Leveling(self.select_page.now == 3)
		else:
			# Tune menu Sur
			self.ICON_StartTune(self.select_page.now == 3)
			#self.ICON_StartInfo(self.select_page.now == 3)

		#clear status area here, Sur
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, self.STATUS_Y, self.lcd.DWIN_WIDTH, self.lcd.DWIN_HEIGHT - 1)
		self.Draw_Status_Area(False)
		
	def Goto_PrintProcess(self):
		self.checkkey = self.PrintProcess
		self.Clear_Main_Window()
		self.Draw_Printing_Screen()

		self.ICON_Tune()
		if (self.pd.printingIsPaused()):
			self.ICON_Continue()
		else:
			self.ICON_Pause()
		self.ICON_Stop()

		# Copy into filebuf string before entry
		name = self.pd.file_name
		if name:
			npos = _MAX(0, self.lcd.DWIN_WIDTH - len(name) * self.MENU_CHR_W) / 2
			self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_White, self.lcd.Color_Bg_Black, npos, 60, name)

		self.lcd.ICON_Show(self.ICON, self.ICON_PrintTime, 17, 193)
		self.lcd.ICON_Show(self.ICON, self.ICON_RemainTime, 150, 191)

		self.Draw_Print_ProgressBar()
		self.Draw_Print_ProgressElapsed()
		self.Draw_Print_ProgressRemain()

		#clear status area here, Sur
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, self.STATUS_Y, self.lcd.DWIN_WIDTH, self.lcd.DWIN_HEIGHT - 1)
		self.Draw_Status_Area(False)
		
	# --------------------------------------------------------------#
	# --------------------------------------------------------------#

	def Clear_Title_Bar(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Blue, 0, 0, self.lcd.DWIN_WIDTH, 30)

	def Clear_Menu_Area(self):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, self.STATUS_Y)

	def Clear_Main_Window(self):
		self.Clear_Title_Bar()
		self.Clear_Menu_Area()

	def Clear_Popup_Area(self):
		self.Clear_Title_Bar()
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, self.lcd.DWIN_HEIGHT)

	def Popup_window_PauseOrStop(self):
		self.Clear_Main_Window()
		self.Draw_Popup_Bkgd_60()
		if(self.select_print.now == 1):
			self.lcd.Draw_String(
				False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color, self.lcd.Color_Bg_Window,
				(272 - 8 * 11) / 2, 150,
				self.MSG_PAUSE_PRINT
			)
		elif (self.select_print.now == 2):
			self.lcd.Draw_String(
				False, True, self.lcd.font8x16, self.lcd.Popup_Text_Color, self.lcd.Color_Bg_Window,
				(272 - 8 * 10) / 2, 150,
				self.MSG_STOP_PRINT
			)
		self.lcd.ICON_Show(self.ICON, self.ICON_Confirm_E, 26, 280)
		self.lcd.ICON_Show(self.ICON, self.ICON_Cancel_E, 146, 280)
		self.Draw_Select_Highlight(True)

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

	def Erase_Menu_Cursor(self, line):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, self.MBASE(line) - 18, 14, self.MBASE(line + 1) - 20)

	def Erase_Menu_Text(self, line):
		self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, self.LBLX, self.MBASE(line) - 14, 271, self.MBASE(line) + 28)

	def Move_Highlight(self, ffrom, newline):
		self.Erase_Menu_Cursor(newline - ffrom)
		self.Draw_Menu_Cursor(newline)

	def Add_Menu_Line(self):
		self.Move_Highlight(1, self.MROWS)
		self.lcd.Draw_Line(self.lcd.Line_Color, 16, self.MBASE(self.MROWS + 1) - 20, 256, self.MBASE(self.MROWS + 1) - 20)

	def Scroll_Menu(self, dir):
		self.lcd.Frame_AreaMove(1, dir, self.MLINE, self.lcd.Color_Bg_Black, 0, 31, self.lcd.DWIN_WIDTH, 349)
		if dir == self.DWIN_SCROLL_DOWN:
			self.Move_Highlight(-1, 0)
		elif dir == self.DWIN_SCROLL_UP:
			self.Add_Menu_Line()

	# Redraw the first set of SD Files
	def Redraw_SD_List(self):
		self.select_file.reset()
		self.index_file = self.MROWS
		self.Clear_Menu_Area()  # Leave title bar unchanged
		self.Draw_Back_First()
		fl = self.pd.GetFiles()
		ed = len(fl)
		if ed > 0:
			if ed > self.MROWS:
				ed = self.MROWS
			for i in range(ed):
				self.Draw_SDItem(i, i + 1)
		else:
			self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Red, 10, self.MBASE(3) - 10, self.lcd.DWIN_WIDTH - 10, self.MBASE(4))
			self.lcd.Draw_String(False, False, self.lcd.font16x32, self.lcd.Color_Yellow, self.lcd.Color_Bg_Red, ((self.lcd.DWIN_WIDTH) - 8 * 16) / 2, self.MBASE(3), "No Media")

	def CompletedHoming(self):
		self.pd.HMI_flag.home_flag = False
		if (self.checkkey == self.Last_Prepare):
			self.checkkey = self.Prepare
			self.select_prepare.now = self.PREPARE_CASE_HOME
			self.index_prepare = self.MROWS
			self.Draw_Prepare_Menu()
		elif (self.checkkey == self.Back_Main):
			self.pd.HMI_ValueStruct.print_speed = self.pd.feedrate_percentage = 100
			# dwin_zoffset = TERN0(HAS_BED_PROBE, probe.offset.z)
			# planner.finish_and_disable()
			self.Goto_MainMenu()

	def say_x(self, inset, line):
		self.lcd.Frame_AreaCopy(1, 95, 104, 102, 114, self.LBLX + inset, line)  # "X"

	def say_y(self, inset, line):
		self.lcd.Frame_AreaCopy(1, 104, 104, 110, 114, self.LBLX + inset, line)  # "Y"

	def say_z(self, inset, line):
		self.lcd.Frame_AreaCopy(1, 112, 104, 120, 114, self.LBLX + inset, line)  # "Z"

	def say_e(self, inset, line):
		self.lcd.Frame_AreaCopy(1, 237, 119, 244, 129, self.LBLX + inset, line)  # "E"

	# --------------------------------------------------------------#
	# --------------------------------------------------------------#

	def ICON_Print(self):
		if self.select_page.now == 0:
			self.lcd.ICON_Show(self.ICON, self.ICON_Print_1, 17, 130)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 17, 130, 126, 229)
			#self.lcd.Frame_AreaCopy(1, 1, 451, 31, 463, 57, 201)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Print_0, 17, 130)
			#self.lcd.Frame_AreaCopy(1, 1, 423, 31, 435, 57, 201)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 52, 201, self.pd.s_PRINT)

	def ICON_Prepare(self):
		if self.select_page.now == 1:
			self.lcd.ICON_Show(self.ICON, self.ICON_Prepare_1, 145, 130)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 145, 130, 254, 229)
			#self.lcd.Frame_AreaCopy(1, 33, 451, 82, 466, 175, 201)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Prepare_0, 145, 130)
			#self.lcd.Frame_AreaCopy(1, 33, 423, 82, 438, 175, 201)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 170, 201, self.pd.s_PREPARE)

	def ICON_Control(self):
		if self.select_page.now == 2:
			self.lcd.ICON_Show(self.ICON, self.ICON_Control_1, 17, 246)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 17, 246, 126, 345)
			#self.lcd.Frame_AreaCopy(1, 85, 451, 132, 463, 48, 318)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Control_0, 17, 246)
			#self.lcd.Frame_AreaCopy(1, 85, 423, 132, 434, 48, 318)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 45, 318, self.pd.s_CONTROL)

	def ICON_Leveling(self, show):
		if show:
			self.lcd.ICON_Show(self.ICON, self.ICON_Leveling_1, 145, 246)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 145, 246, 254, 345)
			self.lcd.Frame_AreaCopy(1, 84, 437, 120, 449, 182, 318)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Leveling_0, 145, 246)
			self.lcd.Frame_AreaCopy(1, 84, 465, 120, 478, 182, 318)

	def ICON_StartInfo(self, show):
		if show:
			self.lcd.ICON_Show(self.ICON, self.ICON_Info_1, 145, 246)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 145, 246, 254, 345)
			self.lcd.Frame_AreaCopy(1, 132, 451, 159, 466, 186, 318)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Info_0, 145, 246)
			self.lcd.Frame_AreaCopy(1, 132, 423, 159, 435, 186, 318)

	def ICON_Tune(self):
		if (self.select_print.now == 0):
			self.lcd.ICON_Show(self.ICON, self.ICON_Setup_1, 8, 252)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 8, 252, 87, 351)
			#self.lcd.Frame_AreaCopy(1, 0, 466, 34, 476, 31, 325)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Setup_0, 8, 252)
			#self.lcd.Frame_AreaCopy(1, 0, 438, 32, 448, 31, 325)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 31, 325, self.pd.s_TUNE)

	def ICON_StartTune(self, show):
		if show:
			self.lcd.ICON_Show(self.ICON, self.ICON_Setup_1, 145, 246)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 145, 246, 224, 345)	#254, 345)
			self.lcd.Frame_AreaCopy(1, 0, 466, 34, 476, 182, 318)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Setup_0, 145, 246)
			self.lcd.Frame_AreaCopy(1, 0, 438, 32, 448, 182, 318)
		#self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 182, 318, self.pd.s_)

	def ICON_Continue(self):
		if (self.select_print.now == 1):
			self.lcd.ICON_Show(self.ICON, self.ICON_Continue_1, 96, 252)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 96, 252, 175, 351)
			#self.lcd.Frame_AreaCopy(1, 1, 452, 32, 464, 121, 325)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Continue_0, 96, 252)
			#self.lcd.Frame_AreaCopy(1, 1, 424, 31, 434, 121, 325)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 121, 325, self.pd.s_CONTINUE)

	def ICON_Pause(self):
		if (self.select_print.now == 1):
			self.lcd.ICON_Show(self.ICON, self.ICON_Pause_1, 96, 252)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 96, 252, 175, 351)
			#self.lcd.Frame_AreaCopy(1, 177, 451, 216, 462, 116, 325)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Pause_0, 96, 252)
			#self.lcd.Frame_AreaCopy(1, 177, 423, 215, 433, 116, 325)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 116, 325, self.pd.s_PAUSE)

	def ICON_Stop(self):
		if (self.select_print.now == 2):
			self.lcd.ICON_Show(self.ICON, self.ICON_Stop_1, 184, 252)
			self.lcd.Draw_Rectangle(0, self.lcd.Color_White, 184, 252, 263, 351)
			#self.lcd.Frame_AreaCopy(1, 218, 452, 249, 466, 209, 325)
		else:
			self.lcd.ICON_Show(self.ICON, self.ICON_Stop_0, 184, 252)
			#self.lcd.Frame_AreaCopy(1, 218, 423, 247, 436, 209, 325)
		self.lcd.Draw_String(False, False, self.lcd.font8x16, self.lcd.Color_FG, self.lcd.Color_BGTitle, 209, 325, self.pd.s_STOP)




	# --------------------------------------------------------------#
	# --------------------------------------------------------------#

	def EachMomentUpdate(self):
		# variable update
		update = self.pd.update_variable()
		self.lcdLock.acquire(blocking=True, timeout=- 1)
		if self.last_status != self.pd.status:
			self.last_status = self.pd.status
			#print(self.pd.status)
			if self.pd.status == 'printing':
				self.Goto_PrintProcess()
			elif self.pd.status in ['operational', 'complete', 'standby', 'cancelled']:
				self.Goto_MainMenu()

		if (self.checkkey == self.PrintProcess):
			if (self.pd.HMI_flag.print_finish and not self.pd.HMI_flag.done_confirm_flag):
				self.pd.HMI_flag.print_finish = False
				self.pd.HMI_flag.done_confirm_flag = True
				# show percent bar and value
				self.Draw_Print_ProgressBar(0)
				# show print done confirm
				self.lcd.Draw_Rectangle(1, self.lcd.Color_Bg_Black, 0, 250, self.lcd.DWIN_WIDTH - 1, self.STATUS_Y)
				self.lcd.ICON_Show(self.ICON, self.ICON_Confirm_E, 86, 283)
			elif (self.pd.HMI_flag.pause_flag != self.pd.printingIsPaused()):
				# print status update
				self.pd.HMI_flag.pause_flag = self.pd.printingIsPaused()
				if (self.pd.HMI_flag.pause_flag):
					self.ICON_Continue()
				else:
					self.ICON_Pause()
			self.Draw_Print_ProgressBar()
			self.Draw_Print_ProgressElapsed()
			self.Draw_Print_ProgressRemain()

		self.printerMenues.periodicUpdate()
		#if self.pd.HMI_flag.home_flag:
		#	if self.pd.ishomed():
		#		self.CompletedHoming()
    

		if update:
			self.Draw_Status_Area(update)
		self.lcd.UpdateLCD()
		self.lcdLock.release()

	def encoder_has_data(self, val):
		self.lcdLock.acquire(blocking=True, timeout=- 1)
		if self.checkkey == self.MainMenu:
			self.HMI_MainMenu()
		elif self.checkkey == self.SelectFile:
			self.HMI_SelectFile()
		elif self.checkkey == self.PrintProcess:
			self.HMI_Printing()
		elif self.checkkey == self.Print_window:
			self.HMI_PauseOrStop()
		elif self.checkkey == self.Info:
			self.HMI_Info()

		else:
			encoder_diffState = self.get_encoder_state()
			self.printerMenues.handleInput(encoder_diffState, self.encoder.diffValue)
			
		self.lcd.UpdateLCD()
		self.lcdLock.release()

	def get_encoder_state(self):
		if self.button.is_pressed:	#mkocot
			if self.EncodeEnter < current_milli_time(): # prevent double clicks
				self.EncodeEnter = current_milli_time() + self.ENCODER_WAIT_ENTER
				self.EncodeLast = self.encoder.value  # Update to prevent later trouble
				self.encoder.reset()	
				return self.ENCODER_DIFF_ENTER
			#print("button.is_pressed double click prevention")
			return self.ENCODER_DIFF_NO

		if self.EncoderRateLimit:
			if self.EncodeMS > current_milli_time():
				#print("EncoderRateLimit hit")
				self.EncodeLast = self.encoder.value  # Update to prevent later trouble
				self.encoder.reset()
				return self.ENCODER_DIFF_NO
			self.EncodeMS = current_milli_time() + self.ENCODER_WAIT

		if self.encoder.value < self.EncodeLast:
			self.EncodeLast = self.encoder.value
			return self.ENCODER_DIFF_CW
		elif self.encoder.value > self.EncodeLast:
			self.EncodeLast = self.encoder.value
			return self.ENCODER_DIFF_CCW
		#elif not GPIO.input(self.button_pin):	#mkocot
		else:
			self.encoder.reset()
			return self.ENCODER_DIFF_NO

	def HMI_AudioFeedback(self, success=True):
		if (success):
			self.pd.buzzer.tone(100, 659)
			self.pd.buzzer.tone(10, 0)
			self.pd.buzzer.tone(100, 698)
		else:
			self.pd.buzzer.tone(40, 440)
