# Class to monitor a rotary encoder and update a value.  You can either read the value when you need it, by calling getValue(), or
# you can configure a callback which will be called whenever the value changes.

#import RPi.GPIO as GPIO	#mkocot
from gpiozero import RotaryEncoder	#mkocot
import time

def current_milli_time():
	return round(time.time() * 1000)

class Encoder:
	ENCODER_WAIT = 40   # collect same moves within this time span
 
	def __init__(self, leftPin, rightPin, callback=None):
		#self.leftPin = leftPin	#mkocot
		#self.rightPin = rightPin	#mkocot
		# NOTE: left, right is different from GPIO, to keep it "legacy"	#mkocot
		# swap values	#mkocot
		self.rotor = RotaryEncoder(rightPin, leftPin)	#mkocot
		self.rotor.when_rotated_clockwise = self.rotated_right	#mkocot
		self.rotor.when_rotated_counter_clockwise = self.rotated_left	#mkocot
		self.value = 0
		#self.state = '00'	#mkocot
		#self.direction = None	#mkocot
		self.lastMS = 0
		self.lastDirection = None
		self.diffValue = 1
		self.callback = callback
		
		# GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#mkocot
		# GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#mkocot
		# GPIO.add_event_detect(self.leftPin, GPIO.BOTH, callback=self.transitionOccurred)  	#mkocot
		# GPIO.add_event_detect(self.rightPin, GPIO.BOTH, callback=self.transitionOccurred)  	#mkocot

	def rotated_left(self):	#mkocot
		self.value = self.value - 1
		if self.callback is not None:
			if self.lastMS > current_milli_time():
				if self.lastDirection == "L":
					self.diffValue = self.diffValue + 2
				else:
					self.diffValue = 1
			else:
				self.diffValue = 1
			self.lastMS = current_milli_time() + self.ENCODER_WAIT
			self.lastDirection = "L"
			self.callback(self.value)
   
	def rotated_right(self):	#mkocot
		self.value = self.value + 1
		if self.callback is not None:
			if self.lastMS > current_milli_time():
				if self.lastDirection == "R":
					self.diffValue = self.diffValue + 2
				else:
					self.diffValue = 1
			else:
				self.diffValue = 1
			self.lastMS = current_milli_time() + self.ENCODER_WAIT
			self.lastDirection = "R"
			self.callback(self.value)
			
	def reset(self):
		self.diffValue = 1
		self.lastMS = 0
		self.lastDirection = None

	def getValue(self):
		return self.value
