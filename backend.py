from flask import Flask, render_template, redirect, Markup
import RPi.GPIO as GPIO
import subprocess
import os
import datetime
import time
app = Flask(__name__)
#app.config['LOGGER_HANDLER_POLICY'] = 'debug'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

channelName = ['WCD-1', 'WCD-2']
relayPin    = [ 6, 13]
ledPin      = [19, 26]
buttonPin   = [20, 21]

# Define a threaded callback function to run in another thread when events are detected
def button_handler(button, ignore_button = False):
    if button == 20 and (ignore_button or GPIO.input(20) == 0):
        state = not GPIO.input(6)
        GPIO.output(6, state)
        GPIO.output(19, state)
    if button == 21 and (ignore_button or GPIO.input(21) == 0):
        state = not GPIO.input(13)
        GPIO.output(13, state)
        GPIO.output(26, state)

# configure the outputs
for pin in relayPin + ledPin:
    GPIO.setup(pin, GPIO.OUT, initial = GPIO.HIGH)

# configure the inputs
for pin in buttonPin:
    GPIO.setup(pin, GPIO.IN)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback = button_handler, bouncetime = 500)

def accState(channelNumber):
    if GPIO.input(relayPin[channelNumber]) is 0:
        return 'containerOff'
    else:
        return 'containerOn'

@app.route("/")
def main():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %I:%M %p")

    passer = ''
    for j in range(len(channelName)):
        pinHtmlName = channelName[j].replace(" ", "<br>")
        passer = passer + "<button class='%s' formaction='/pin/%d/'>%s</button>" % (accState(j), j, pinHtmlName)

    buttonGrid = Markup(passer)
    templateData = {
        'title' : 'EasyOn',
        'time': timeString,
        'buttons' : buttonGrid
    }
    return render_template('main.html', **templateData)

@app.route("/pin/<int:channelNumber>/")
def toggle(channelNumber):
    button_handler(buttonPin[channelNumber], True)
    return redirect("/", code=302)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8000, debug=False)
