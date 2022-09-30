import os
import pyaudio
import wave
import audioop
import time
import threading
import RPi.GPIO as GPIO
import math
import serial

class Talker():

    def __init__(self):
        """
            Class used to initialise the talker with all the necessary threads.
        """
        self.servo_pin = 4
        #self.init_servo()
        self.p = pyaudio.PyAudio()
        # Servo variables
        self.current_angle = 0
        self.last_angle = -2
        self.pwm = None
        # Audio variables
        self.min_decibels = 9999
        self.max_decibels = 0
        self.current_decibels = 0
        self.current_wav = None
        self.is_preset = False
        # Threading
        self.lock = threading.Lock()
        self.audio_thread = threading.Thread(target=self.play_audio, args=(1,))
        self.servo_thread = threading.Thread(target=self.set_angle, args=(1,))
        self.calculation_thread = threading.Thread(target=self.get_angle, args=(1,))
        

    def get_angle(self, name):
        """
            Calculate the angle of the servo at a given time given the current decibels level.
        Args:
            name (_type_): Angle calculation thread name.
        """
        while True:
            if self.current_decibels < self.min_decibels and self.current_decibels > 10:
                self.min_decibels = self.current_decibels
            if self.current_decibels > self.max_decibels:
                self.max_decibels = self.current_decibels
            if self.max_decibels > 0:
                angle = 60 if self.current_decibels < ((self.max_decibels + self.min_decibels) / 2) else 170
                self.lock.acquire()
                self.current_angle = angle
                self.lock.release()

    def set_angle(self, name):
        """
            Set the angle of the servo based on the current calculations.
        Args:
            name (_type_): Servo thread name.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm=GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)
        while True:
            if self.current_angle != self.last_angle and self.current_angle != 0:
                self.lock.acquire()
                duty = self.current_angle / 18 + 2
                GPIO.output(self.servo_pin, True)
                self.pwm.ChangeDutyCycle(duty)
                time.sleep(0.35)
                GPIO.output(self.servo_pin, False)
                self.pwm.ChangeDutyCycle(0)
                self.last_angle = self.current_angle
                self.lock.release()
                self.is_preset = False
                    
        self.pwm.stop()
        GPIO.cleanup()
        servo_thread.join()

    def play_audio(self, name):
        """
            Check the current set wav and play the audio as a stream / calculate the decibels of each audio chunk.
        Args:
            name (_type_): Audio thread name.
        """
        chunk = 1024
        self.stop = False
        while True:
            if self.current_wav != None:
                f = wave.open(self.current_wav, "rb")  
                #open stream  
                framerate = f.getframerate() if self.is_preset else 36000
                stream = self.p.open(format = self.p.get_format_from_width(f.getsampwidth()),  
                                channels = f.getnchannels(),  
                                rate = framerate,  
                                output = True)  
                #read data  
                data = f.readframes(chunk)  
                while data and not self.stop:  
                    stream.write(data)  
                    data = f.readframes(chunk)
                    rms = audioop.rms(data, 2)
                    if rms != 0:
                        self.current_decibels = 20 * math.log10(rms)
                stream.stop_stream()
                stream.close()
                self.current_wav = None  


while True:
    t = Talker()
    # Start the threads
    t.audio_thread.start()
    t.servo_thread.start()
    t.calculation_thread.start()
    # Load the preset wavs ( the ones not generated using tts)
    wav_dir = os.path.join(os.getcwd(), "preset_wavs") 
    wavs = [wav.replace(".wav","") for wav in os.listdir(wav_dir) if os.path.isfile(os.path.join(wav_dir, wav))]
    while True:
        try:
            # Check the serial channel for new data
            with serial.Serial('/dev/rfcomm0') as ser:
                line = ser.readline().decode('ascii').strip()
                if line != "":
                    if line == "stop":
                        t.stop = True
                    elif line in wavs:
                        t.is_preset = True
                        t.current_wav = os.path.join(wav_dir,line + ".wav")
                    else:
                        os.system("echo " + line + " | sudo text2wave -o " + os.path.join(os.getcwd(), "output.wav") + "-eval '(voice_cmu_us_slt_arctic_hts)'")
                        t.current_wav = os.get_cwd() + os.path.join() + "output.wav"

        except Exception as e:
            print(e)
            print('cant communicate with device yet')