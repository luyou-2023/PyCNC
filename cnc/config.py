# Hardware limitations config
STEPPER_PULSE_LENGTH_US = 2
STEPPER_MAX_ACCELERATION_MM_PER_S2 = 3000  # for all axis, mm per sec^2

MAX_VELOCITY_MM_PER_MIN_X = 30000  # mm per min
MAX_VELOCITY_MM_PER_MIN_Y = 24000  # mm per min
MAX_VELOCITY_MM_PER_MIN_Z = 120    # mm per min
MAX_VELOCITY_MM_PER_MIN_E = 1500   # mm per min

STEPPER_PULSES_PER_MM_X = 100
STEPPER_PULSES_PER_MM_Y = 100
STEPPER_PULSES_PER_MM_Z = 400
STEPPER_PULSES_PER_MM_E = 150

# invert axises direction
STEPPER_INVERTED_X = True
STEPPER_INVERTED_Y = False
STEPPER_INVERTED_Z = False
STEPPER_INVERTED_E = True

TABLE_SIZE_X_MM = 200
TABLE_SIZE_Y_MM = 200
TABLE_SIZE_Z_MM = 220

SPINDLE_MAX_RPM = 10000
EXTRUDER_MAX_TEMPERATURE = 250
BED_MAX_TEMPERATURE = 100
MIN_TEMPERATURE = 40
EXTRUDER_PID = {"P": 0.0993079964195,
                "I": 0.00267775053311,
                "D": 0.267775053311}
BED_PID = {"P": 5.06820175723,
           "I": 0.0476413193519,
           "D": 4.76413193519}

# Pins config
STEPPER_STEP_PIN_X = 16
STEPPER_STEP_PIN_Y = 20
STEPPER_STEP_PIN_Z = 21
STEPPER_STEP_PIN_E = 25

STEPPER_DIR_PIN_X = 13
STEPPER_DIR_PIN_Y = 19
STEPPER_DIR_PIN_Z = 26
STEPPER_DIR_PIN_E = 8

SPINDLE_PWM_PIN = 7
FAN_PIN = 10
EXTRUDER_HEATER_PIN = 9
BED_HEATER_PIN = 11
EXTRUDER_TEMPERATURE_SENSOR_CHANNEL = 0
BED_TEMPERATURE_SENSOR_CHANNEL = 1

ENDSTOP_PIN_X = 12
ENDSTOP_PIN_Y = 6
ENDSTOP_PIN_Z = 5

# Hardware behavior config
# Run command immediately after receiving and stream new pulses, otherwise
# buffer will be prepared firstly and then command will run.
# Before enabling this feature, please make sure that board performance is
# enough for streaming pulses(faster then real time).
INSTANT_RUN = True
