
# PHASOR ROTATION REFERENCED from Qi Tianshi.
# https://github.com/qitianshi/AC-animations?tab=readme-ov-file


from matplotlib.animation import FuncAnimation
from matplotlib.patches import ConnectionPatch
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys, time, math
import numpy as np
import serial



#for the sounds
from scipy.io.wavfile import write
from scipy import signal
import pygame

#initializing pygame
pygame.init()
pygame.mixer.init() 


AUDIO_RATE = 44100
a_freq = 440 #setting a frequency in audible range
length  = 1


ser = serial.Serial(
    port='COM19', #change to whichever serial port we end up using (e.g. COM5)
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)
ser.isOpen()  

#import  arrows
def rotate_center(xcenter, ycenter, length, rotation) -> tuple[float]:
    """Rotates an arrow of a specified length at its center."""

    half_length = length / 2
    rad_angle = np.radians(rotation)

    return (
        xcenter - half_length * np.sin(rad_angle),
        ycenter - half_length * np.cos(rad_angle),
        length * np.sin(rad_angle),
        length * np.cos(rad_angle)
    )

def rotate_tail(xtail, ytail, length, rotation) -> tuple[float]:
    """Rotates an arrow of a specified length at its tail."""

    rad_angle = np.radians(rotation)

    return (
        xtail,
        ytail,
        length * np.sin(rad_angle),
        length * np.cos(rad_angle)
    )

X_MAX = 4

# Default fig size is 6.4 x 4.8. This ratio keeps the aspect ratio of
# the sinusoid the same as travelling_sine

fig, (ax_phasor, ax_sine) = plt.subplots(
    1, 2, figsize=(11.2, 4.8), gridspec_kw={'width_ratios': [3, 4]})

line1, = ax_sine.plot([], [])
line2, = ax_sine.plot([], [])
line1.set_color('orange')
line2.set_color('blue')

red_patch = mpatches.Patch(color='orange', label='Reference Voltage')
blue_patch = mpatches.Patch(color='blue', label='Input Voltage')

plt.legend(handles=[red_patch, blue_patch])

# Limits
ax_sine.set_xlim((0, X_MAX))
ax_sine.set_ylim((-1.5, 1.5))

# Ticks
ax_sine.set_xticks([])
ax_sine.set_yticks(ticks=[-1, 0, 1],
                   labels=[r'-2.5V', '0', r'2.5V'])

# Labels next to arrowheads
ax_sine.set_ylabel(r'V(t)', loc='top', rotation=0)
ax_sine.set_xlabel('t', loc='right')

# Vertical left and horizontal center axes with arrowheads.
ax_sine.spines['right'].set_visible(False)
ax_sine.spines['top'].set_visible(False)
ax_sine.spines['bottom'].set_position('zero')
ax_sine.plot(1, 0, ls='', marker=5, ms=5, color='k',
             transform=ax_sine.get_yaxis_transform(), clip_on=False)
ax_sine.plot(0, 1, ls='', marker=6, ms=5, color='k',
             transform=ax_sine.get_xaxis_transform(), clip_on=False)


# Axes for phasor
ax_phasor.set_ylim((-1.5, 1.5))
ax_phasor.set_xlim((-1.1, 1.1))
ax_phasor.spines['right'].set_visible(False)
ax_phasor.spines['top'].set_visible(False)
ax_phasor.spines['left'].set_position('zero')
ax_phasor.spines['bottom'].set_position('zero')
ax_phasor.plot(1, 0, ls='', marker=5, ms=5, color='k',
               transform=ax_phasor.get_yaxis_transform(), clip_on=False)
ax_phasor.plot(0, 1, ls='', marker=6, ms=5, color='k',
               transform=ax_phasor.get_xaxis_transform(), clip_on=False)
ax_phasor.set_aspect('equal')

# Ticks
ax_phasor.set_xticks([])
ax_phasor.set_yticks([])

# Unit circle
ax_phasor.add_patch(plt.Circle(
    (0, 0), radius=1, facecolor='white', edgecolor='darkgray', ls='--'))

# Lines and arrows
phasor1 = ax_phasor.arrow(0, 0, 0, 0)
horiz_connector1 = ConnectionPatch(
    xyA=(-1, 0), xyB=(0, 0),
    coordsA='data', coordsB='data', axesA=ax_phasor, axesB=ax_sine,
    ls='--', edgecolor='darkgray'
)
ax_sine.add_artist(horiz_connector1)

phasor2 = ax_phasor.arrow(0, 0, 0, 0)
horiz_connector2 = ConnectionPatch(
    xyA=(-1, 0), xyB=(0, 0),
    coordsA='data', coordsB='data', axesA=ax_phasor, axesB=ax_sine,
    ls='--', edgecolor='darkgray'
)
ax_sine.add_artist(horiz_connector2)

t1 = ax_sine.text(2.4,-1,f"Frequency = {0}Hz\nInput Vrms = {0}V\nReference Vrms = {0}V\nPhase = {0}°", bbox=dict(facecolor='white',edgecolor='lightgray', boxstyle='round', alpha=1))

def _init():
    line1.set_data([], [])
    line2.set_data([], [])
    return (line1, line2)

#this will be equivalent to "data gen"
def _anim(i):
    strin = ser.readline()
    print(strin) 

    vr=strin[0:5]
    vi=strin[6:11]
    per = strin[12:17]
    ph=strin[18:]

    x = np.linspace(0, X_MAX, 1000)
    y1 = float(vr)/2.5*np.sin(2 * np.pi * 10.0/float(per) * (x - 0.01 * i))
    y2 = float(vi)/2.5*np.sin(2 * np.pi * 10.0/float(per) * (x - 0.01 * i) + np.pi*float(ph)/180.0)
    line1.set_data(x, y1)
    line2.set_data(x, y2)
    
    t1.set_text(f"Frequency = {round(1000.0/float(per),2)}Hz\nInput Vrms = {round(float(vi)/1.41,2)}V\nReference Vrms = {round(float(vr)/1.41,2)}V\nPhase = {float(ph)}°")

    #linspace for sounds -- will make them start with a
    t = np.linspace(0,length, length*AUDIO_RATE, dtype = np.float32)
    ya = float(vr)/2.5*np.sin(2*np.pi*(2.5*1000.0/float(per)*t)) + float(vi)/2.5*np.sin(2*np.pi*(2.5*1000.0/float(per)*t) - np.pi*float(ph)/180.0)
    #save to wave file
    write("sine.wav", AUDIO_RATE,ya)
    sine_file = "C:\\Users\\maya2\\Documents\\GitHub\\Lab5Phasor\\sine.wav"
    #playing sine wave sound with each cycle
    sine_sound = pygame.mixer.Sound(sine_file)
    sine_sound.play()
    
    phasor1_coordinates = rotate_tail(
        0, 0, float(vr)/2.5, -1 * 10.0/float(per) * (i / 100) * 360 - 90
    )
    phasor1_tail = (
        phasor1_coordinates[0] + phasor1_coordinates[2],      # x
        phasor1_coordinates[1] + phasor1_coordinates[3]       # y
    )

    global phasor1  # pylint: disable=all
    phasor1.remove()
    phasor1 = ax_phasor.arrow(
        *phasor1_coordinates,
        fc='orange', ec='orange',
        head_width=0.05, head_length=0.1, length_includes_head=True
    )

    global horiz_connector1
    horiz_connector1.remove()
    horiz_connector1 = ConnectionPatch(
        xyA=(phasor1_tail[0], phasor1_tail[1]), xyB=(0, phasor1_tail[1]),
        coordsA='data', coordsB='data', axesA=ax_phasor, axesB=ax_sine,
        ls='--', edgecolor='darkgray'
    )
    ax_sine.add_patch(horiz_connector1)

    phasor2_coordinates = rotate_tail(
        0, 0, float(vi)/2.5, -1 * 10.0/float(per) *(i / 100) * 360 - 90 + float(ph)
    )
    phasor2_tail = (
        phasor2_coordinates[0] + phasor2_coordinates[2],      # x
        phasor2_coordinates[1] + phasor2_coordinates[3]       # y
    )

    global phasor2  # pylint: disable=all
    phasor2.remove()
    phasor2 = ax_phasor.arrow(
        *phasor2_coordinates,
        fc='blue', ec='blue',
        head_width=0.05, head_length=0.1, length_includes_head=True
    )

    global horiz_connector2
    horiz_connector2.remove()
    horiz_connector2 = ConnectionPatch(
        xyA=(phasor2_tail[0], phasor2_tail[1]), xyB=(0, phasor2_tail[1]),
        coordsA='data', coordsB='data', axesA=ax_phasor, axesB=ax_sine,
        ls='--', edgecolor='darkgray'
    )
    ax_sine.add_patch(horiz_connector2)
    
    return (line1, line2, phasor1, horiz_connector1, phasor2, horiz_connector2) 


# Animate
anim = FuncAnimation(fig, _anim, init_func=_init, frames=100, interval=16,
                     blit=False)
#anim.save('videos/ac/freqdiff_phasor_and_sine.gif', writer='imagemagick')

plt.show()
