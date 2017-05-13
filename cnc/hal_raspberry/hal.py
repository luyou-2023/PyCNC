import logging
import time

import rpgpio

from cnc.pulses import PulseGeneratorLinear
from cnc.coordinates import Coordinates
from cnc.config import *

# Stepper motors channel for RPIO
STEPPER_CHANNEL = 0
# Since there is no way to add pulses and then start cycle in RPIO,
# use this delay to start adding pulses to cycle. It can be easily
# solved by modifying RPIO in a way of adding method to start cycle
# explicitly.
RPIO_START_DELAY_US = 200000
# Since RPIO generate cycles in loop, use this delay to stop RPIO
# It can be removed if RPIO would allow to run single shot cycle.
RPIO_STOP_DELAY_US = 5000000

US_IN_SECONDS = 1000000

gpio = rpgpio.GPIO()
dma = rpgpio.DMAGPIO()

STEP_PIN_MASK_X = 1 << STEPPER_STEP_PIN_X
STEP_PIN_MASK_Y = 1 << STEPPER_STEP_PIN_Y
STEP_PIN_MASK_Z = 1 << STEPPER_STEP_PIN_Z

def init():
    """ Initialize GPIO pins and machine itself, including callibration if
        needed. Do not return till all procedure is completed.
    """
    gpio.init(STEPPER_STEP_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)

    # calibration
    gpio.set(STEPPER_DIR_PIN_X)
    gpio.set(STEPPER_DIR_PIN_Y)
    gpio.set(STEPPER_DIR_PIN_Z)
    pins = STEP_PIN_MASK_X | STEP_PIN_MASK_Y | STEP_PIN_MASK_Z
    dma.clear()
    dma.add_pulse(pins, STEPPER_PULSE_LINGTH_US)
    while True:
        if (STEP_PIN_MASK_X & pins) != 0 and gpio.read(ENDSTOP_PIN_X) == 0:
            pins &= ~STEP_PIN_MASK_X
            dma.clear()
            dma.add_pulse(pins, STEPPER_PULSE_LINGTH_US)
        if (STEP_PIN_MASK_Y & pins) != 0 and gpio.read(ENDSTOP_PIN_Y) == 0:
            pins &= ~STEP_PIN_MASK_Y
            dma.clear()
            dma.add_pulse(pins, STEPPER_PULSE_LINGTH_US)
        if (STEP_PIN_MASK_Z & pins) != 0 and gpio.read(ENDSTOP_PIN_Z) == 0:
            pins &= ~STEP_PIN_MASK_Z
            dma.clear()
            dma.add_pulse(pins, STEPPER_PULSE_LINGTH_US)
        if pins == 0:
            break
        dma.run(False)
        # limit velocity at ~10% of top velocity
        time.sleep((1 / 0.10) / (STEPPER_MAX_VELOCITY_MM_PER_MIN
                                 / 60 * STEPPER_PULSES_PER_MM))


def spindle_control(percent):
    """ Spindle control implementation.
    :param percent: Spindle speed in percent.
    """
    # TODO spindle control.
    logging.info("TODO spindle control: {}%".format(percent))


def move_linear(delta, velocity):
    """ Move head to specified position
    :param delta: Coordinated object, delta position in mm
    :param velocity: velocity in mm per min
    """
    logging.info("move {} with velocity {}".format(delta, velocity))
    # initialize generator
    generator = PulseGeneratorLinear(delta, velocity)
    # wait if previous command still works
    while dma.is_active():
        time.sleep(0.001)

    # set direction pins
    if delta.x > 0.0:
        gpio.clear(STEPPER_DIR_PIN_X)
    else:
        gpio.set(STEPPER_DIR_PIN_X)
    if delta.y > 0.0:
        gpio.clear(STEPPER_DIR_PIN_Y)
    else:
        gpio.set(STEPPER_DIR_PIN_Y)
    if delta.z > 0.0:
        gpio.clear(STEPPER_DIR_PIN_Z)
    else:
        gpio.set(STEPPER_DIR_PIN_Z)

    # prepare and run dma
    dma.clear()
    prev = 0
    is_ran = False
    st = time.time()
    for tx, ty, tz in generator:
        pins = 0
        k = int(round(min(x for x in (tx, ty, tz) if x is not None)
                      * US_IN_SECONDS))
        if tx is not None:
            pins |= STEP_PIN_MASK_X
        if ty is not None:
            pins |= STEP_PIN_MASK_Y
        if tz is not None:
            pins |= STEP_PIN_MASK_Z
        if k - prev > 0:
            dma.add_delay(k - prev)
        dma.add_pulse(pins, STEPPER_PULSE_LINGTH_US)
        # TODO not a precise way! pulses will set in queue, instead of crossing
        # if next pulse start during pulse length. Though it almost doesn't
        # matter for pulses with 1-2us length.
        prev = k + STEPPER_PULSE_LINGTH_US
        # instant run handling
        if not is_ran and INSTANT_RUN:
            if k > 500000:  # wait at least 500 ms is uploaded
                if time.time() - st > 0.5:
                    # may be instant run should be canceled here?
                    logging.warn("Buffer preparing for instant run took more "
                                 "time then buffer time")
                dma.run_stream()
                is_ran = True
    pt = time.time()
    if not is_ran:
        dma.run(False)
    else:
        dma.finalize_stream()

    logging.info("prepared in " + str(round(pt - st, 2)) + "s, estimated in "
                 + str(round(generator.total_time_s(), 2)) + "s")


def join():
    """ Wait till motors work.
    """
    # wait till dma works
    while dma.is_active():
        time.sleep(0.01)