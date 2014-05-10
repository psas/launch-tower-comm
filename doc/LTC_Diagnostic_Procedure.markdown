# Launch Tower Computer Diagnostic Test Procedures



## Initial Setup

1. Disconnect
  * R± M± S T Q±
  * I± J± K± L±
    * All of these don’t connect devices like batteries and solar
      panel to the exterior connection.
  * N (to battery) O (to charger)
2. S2 to “OFF”



## Test Main Power Switch

1. S2 to “OFF”
2. Continuity test across both H points
  * [PASS] Have NO continuity across points
  * [FAIL] Have continuity across points
3. S2 to “ON”
4. Continuity test across both H points
  * [PASS] Have continuity across points
  * [FAIL] Have NO continuity across points
5. S2 to “OFF”



## Test Solar Panel Connection And Lights
	
1. S2 to “OFF”
2. Connect 9-16 VDC (VINPUT) to J±
  * [PASS] L1 light is ON
  * [FAIL] L1 light is OFF
3. Depress and hold S1
  * [PASS] L1 light is OFF
  * [FAIL] L1 light is ON
4. S2 to “OFF”


## Test System Battery Connection And Lights

1. S2 to “OFF”
2. Connect 9-16 VDC (VINPUT) to I± or L±
  * [PASS] L2 light is ON
  * [FAIL] L2 light is OFF
3. S2 to “OFF”
4. S2 to “ON”
  * [PASS] L3 and L4 and L5 light is ON
  * [FAIL] L3 and L4 and L5 light is OFF
5. S2 to “OFF”



## Test Power Conversion

1. S2 to “OFF”
2. Connect 9-16 VDC (VINPUT) to I± or L±
3. S2 to “ON”
4. Voltage Check: A± B± C± D± E± F±
       | A± and B±        | C± and D±   | E± and F±
-------|------------------|-------------|------------
[PASS] | (VINPUT) ± .02 V | 5 V ± .02 V | 24 V ± .02V
[FAIL] | != PASS          | != PASS     | != PASS
5. S2 to “OFF”



## Test Phidget Board

1. S2 to “OFF”
2. Connect: M±
3. S2 to “ON”
4. Voltage Check: M±
  * [PASS] Voltage = (VINPUT) ± .02 V
  * [FAIL] Voltage ! = (VINPUT) ± .02 V
  * Note: OK if L5 goes out. This indicates Phidget board has turned
    off 24 V converter.
5. S2 to “OFF”



## Test Ignition Board

### Board Power

S2 to “OFF”
Connect: Q±
S2 to “ON”
Voltage Check: Q±
[PASS] Voltage = 5V ± .02V and L6 is ON
[FAIL] Voltage != 5V ± .02V or L6 is OFF
S2 to “OFF”


### Shore Power

Disconnect: M±
Connect: R+
S2 to “ON”
Voltage Check: R+ / Q-
[PASS] Voltage = 24V ± .02V and L5 is ON
[FAIL] Voltage != 24V ± .02V or L5 is OFF
S2 to “OFF”
Re-Connect: M±


### Ignition Battery

NEED PROCEDURE HERE



## Test Ignition Battery Charger

S2 to “OFF”
S2 to “ON”
Voltage Check: S (positive tip)
[PASS] Voltage = (VINPUT) ± .02V
[FAIL] Voltage != (VINPUT) ± .02V
Connect: S
[PASS] Battery charger turns on
[FAIL] Battery charger does NOT turn on

Note: If charger display shows “Er2” – it indicates the input voltage on S is greater than the 16V maximum input of charger.
S2 to “OFF”



## Test Beagleboard

S2 to “OFF”
S2 to “ON”
Voltage Check: T (positive tip)
[PASS] Voltage = 5V ± .02V
[FAIL] Voltage != 5V ± .02V
Connect: T
[PASS] L7 is ON and L8 and L9 start flashing
[FAIL] L7 is OFF or L7 is RED

Note: Failure at this stage may indicate the polarity is revered on
connection

Note: At this stage it may not be a good idea to turn S2 to “OFF”
because it could corrupt the beagleboard image. Instead, let computer
boot – connect to it and power down the board normally.  S2 to “OFF”
