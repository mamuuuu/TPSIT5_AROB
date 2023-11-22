import RPi.GPIO as GPIO
import time
import AlphaBot

alphaBot = AlphaBot.Alphabot()

DR = 16
DL = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)

try:
	while True:
		DR_status = GPIO.input(DR)	#Statue of anterior right sensor
		DL_status = GPIO.input(DL)	#Statue of anterior left sensor
		# if DL_* == 1: not detention
		# if DL_* == 0: detention
		if((DL_status == 1) and (DR_status == 1)):
			alphaBot.forward()
			print("forward")
		elif((DL_status == 1) and (DR_status == 0)):
			alphaBot.left()
			print("left")
		elif((DL_status == 0) and (DR_status == 1)):
			alphaBot.right()
			print("right")
		else:
			alphaBot.backward()
			time.sleep(0.2)
			alphaBot.left()
			time.sleep(0.2)
			alphaBot.stop()
			print("backward")

except KeyboardInterrupt:
	GPIO.cleanup()
