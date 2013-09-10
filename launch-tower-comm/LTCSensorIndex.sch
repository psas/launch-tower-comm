<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="6.4">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="no" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="yes" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="yes" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="yes" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="yes" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="yes" active="no"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="yes" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="yes" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="yes" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="yes" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="yes" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="yes" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="yes" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="yes" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="yes" active="no"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="yes" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="yes" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="yes" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="yes" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="yes" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="yes" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="yes" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="yes" active="no"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="launch-tower">
<packages>
<package name="LAYOUT-PACKAGE">
<pad name="P$1" x="-11.43" y="3.81" drill="0.8" shape="square"/>
<pad name="P$2" x="-8.89" y="3.81" drill="0.8" shape="square"/>
<pad name="P$3" x="-6.35" y="3.81" drill="0.8" shape="square"/>
<pad name="P$4" x="-3.81" y="3.81" drill="0.8" shape="square"/>
<pad name="P$5" x="-1.27" y="3.81" drill="0.8" shape="square"/>
<pad name="P$6" x="1.27" y="3.81" drill="0.8" shape="square"/>
<pad name="P$7" x="-11.43" y="1.27" drill="0.8" shape="square"/>
<pad name="P$8" x="-8.89" y="1.27" drill="0.8" shape="square"/>
<pad name="P$9" x="-6.35" y="1.27" drill="0.8" shape="square"/>
<pad name="P$10" x="-3.81" y="1.27" drill="0.8" shape="square"/>
<pad name="P$11" x="-1.27" y="1.27" drill="0.8" shape="square"/>
<pad name="P$12" x="1.27" y="1.27" drill="0.8" shape="square"/>
<pad name="P$13" x="-11.43" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$14" x="-8.89" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$15" x="-6.35" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$16" x="-3.81" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$17" x="-1.27" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$18" x="1.27" y="-1.27" drill="0.8" shape="square"/>
<pad name="P$19" x="-11.43" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$20" x="-8.89" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$21" x="-6.35" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$22" x="-3.81" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$23" x="-1.27" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$24" x="1.27" y="-3.81" drill="0.8" shape="square"/>
<pad name="P$25" x="-11.43" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$26" x="-8.89" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$27" x="-6.35" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$28" x="-3.81" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$29" x="-1.27" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$30" x="1.27" y="-6.35" drill="0.8" shape="square"/>
<pad name="P$31" x="-11.43" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$32" x="-8.89" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$33" x="-6.35" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$34" x="-3.81" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$35" x="-1.27" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$36" x="1.27" y="-8.89" drill="0.8" shape="square"/>
<pad name="P$37" x="-11.43" y="-11.43" drill="0.8" shape="square"/>
<pad name="P$38" x="-8.89" y="-11.43" drill="0.8" shape="square"/>
<pad name="P$39" x="-6.35" y="-11.43" drill="0.8" shape="square"/>
<pad name="P$40" x="-3.81" y="-11.43" drill="0.8" shape="square"/>
<pad name="P$41" x="-1.27" y="-11.43" drill="0.8" shape="square"/>
<pad name="P$42" x="1.27" y="-11.43" drill="0.8" shape="square"/>
</package>
<package name="LEMO-12">
<pad name="P7" x="-1.27" y="3.81" drill="0.7"/>
<pad name="P6" x="1.27" y="3.81" drill="0.7"/>
<pad name="P8" x="-3.81" y="1.27" drill="0.7"/>
<pad name="P12" x="-1.27" y="1.27" drill="0.7"/>
<pad name="P11" x="1.27" y="1.27" drill="0.7"/>
<pad name="P5" x="3.81" y="1.27" drill="0.7"/>
<pad name="P1" x="-3.81" y="-1.27" drill="0.7"/>
<pad name="P9" x="-1.27" y="-1.27" drill="0.7"/>
<pad name="P10" x="1.27" y="-1.27" drill="0.7"/>
<pad name="P4" x="3.81" y="-1.27" drill="0.7"/>
<pad name="P2" x="-1.27" y="-3.81" drill="0.7"/>
<pad name="P3" x="1.27" y="-3.81" drill="0.7"/>
</package>
</packages>
<symbols>
<symbol name="LAYOUT_PHIDGET">
<pin name="M+" x="-20.32" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="M-" x="-17.78" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="DI-GND" x="-25.4" y="10.16" visible="pin" length="short"/>
<pin name="DI-8" x="-25.4" y="7.62" visible="pin" length="short"/>
<pin name="DI-7" x="-25.4" y="5.08" visible="pin" length="short"/>
<pin name="DI-6" x="-25.4" y="2.54" visible="pin" length="short"/>
<pin name="DI-5" x="-25.4" y="0" visible="pin" length="short"/>
<pin name="DI-4" x="-25.4" y="-2.54" visible="pin" length="short"/>
<pin name="DI-3" x="-25.4" y="-5.08" visible="pin" length="short"/>
<pin name="DI-2" x="-25.4" y="-7.62" visible="pin" length="short"/>
<pin name="DO-7" x="22.86" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="DO-6" x="22.86" y="2.54" visible="pin" length="short" rot="R180"/>
<pin name="DO-GND" x="22.86" y="10.16" visible="pin" length="short" rot="R180"/>
<pin name="DO-8" x="22.86" y="7.62" visible="pin" length="short" rot="R180"/>
<wire x1="-22.86" y1="17.78" x2="20.32" y2="17.78" width="0.254" layer="94"/>
<wire x1="20.32" y1="17.78" x2="20.32" y2="-17.78" width="0.254" layer="94"/>
<wire x1="20.32" y1="-17.78" x2="-22.86" y2="-17.78" width="0.254" layer="94"/>
<wire x1="-22.86" y1="-17.78" x2="-22.86" y2="17.78" width="0.254" layer="94"/>
<pin name="DO-3" x="22.86" y="-5.08" visible="pin" length="short" rot="R180"/>
<pin name="DO-2" x="22.86" y="-7.62" visible="pin" length="short" rot="R180"/>
<pin name="DO-5" x="22.86" y="0" visible="pin" length="short" rot="R180"/>
<pin name="DO-4" x="22.86" y="-2.54" visible="pin" length="short" rot="R180"/>
<pin name="DO-5V+" x="22.86" y="-12.7" visible="pin" length="short" rot="R180"/>
<pin name="DO-1" x="22.86" y="-10.16" visible="pin" length="short" rot="R180"/>
<pin name="DI-1" x="-25.4" y="-10.16" visible="pin" length="short"/>
<pin name="DI-5V+" x="-25.4" y="-12.7" visible="pin" length="short"/>
<pin name="AI-7" x="5.08" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-6" x="2.54" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-8" x="7.62" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-3" x="-5.08" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-2" x="-7.62" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-5" x="0" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-4" x="-2.54" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="AI-1" x="-10.16" y="-20.32" visible="pin" length="short" rot="R90"/>
<pin name="U-1" x="-10.16" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="U-4" x="-2.54" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="U-5" x="0" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="U-2" x="-7.62" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="U-3" x="-5.08" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="U-6" x="2.54" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="USB2" x="7.62" y="20.32" visible="pin" length="short" rot="R270"/>
<text x="-2.54" y="0" size="1.27" layer="94">PHIDGET</text>
</symbol>
<symbol name="LAYOUT_SENSOR_TEMPERATURE">
<text x="-0.762" y="-3.556" size="1.27" layer="94" rot="R90">Temp.</text>
<text x="2.032" y="-3.556" size="1.27" layer="94" rot="R90">Sensor</text>
<wire x1="-2.54" y1="5.08" x2="-2.54" y2="-5.08" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-5.08" x2="2.54" y2="-5.08" width="0.254" layer="94"/>
<wire x1="2.54" y1="-5.08" x2="2.54" y2="5.08" width="0.254" layer="94"/>
<wire x1="2.54" y1="5.08" x2="-2.54" y2="5.08" width="0.254" layer="94"/>
<pin name="X" x="0" y="-7.62" visible="pin" length="short" rot="R90"/>
</symbol>
<symbol name="LAYOUT_SENSOR_VOLTAGE">
<pin name="+" x="-2.54" y="7.62" visible="pin" length="short" rot="R270"/>
<pin name="-" x="0" y="7.62" visible="pin" length="short" rot="R270"/>
<text x="-3.302" y="-3.556" size="1.27" layer="94" rot="R90">Voltage</text>
<text x="1.524" y="-3.556" size="1.27" layer="94" rot="R90">Sensor</text>
<wire x1="-5.08" y1="5.08" x2="-5.08" y2="-5.08" width="0.254" layer="94"/>
<wire x1="-5.08" y1="-5.08" x2="2.54" y2="-5.08" width="0.254" layer="94"/>
<wire x1="2.54" y1="-5.08" x2="2.54" y2="5.08" width="0.254" layer="94"/>
<wire x1="2.54" y1="5.08" x2="-5.08" y2="5.08" width="0.254" layer="94"/>
<pin name="X" x="-2.54" y="-7.62" visible="pin" length="short" rot="R90"/>
</symbol>
<symbol name="LAYOUT_RELAY_BOARD">
<pin name="USB1" x="25.4" y="10.16" visible="pin" length="short" rot="R270"/>
<pin name="R1-1" x="-22.86" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R1-2" x="-20.32" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R1-3" x="-17.78" y="-10.16" visible="pin" length="short" rot="R90"/>
<text x="-7.62" y="5.08" size="1.27" layer="94">RELAY BOARD</text>
<wire x1="-25.4" y1="2.54" x2="-25.4" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-25.4" y1="-7.62" x2="-15.24" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-15.24" y1="-7.62" x2="-15.24" y2="2.54" width="0.254" layer="94"/>
<wire x1="-15.24" y1="2.54" x2="-25.4" y2="2.54" width="0.254" layer="94"/>
<pin name="R2-1" x="-10.16" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R2-2" x="-7.62" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R2-3" x="-5.08" y="-10.16" visible="pin" length="short" rot="R90"/>
<wire x1="-12.7" y1="2.54" x2="-12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-7.62" x2="-2.54" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-7.62" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-12.7" y2="2.54" width="0.254" layer="94"/>
<pin name="R3-1" x="2.54" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R3-2" x="5.08" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R3-3" x="7.62" y="-10.16" visible="pin" length="short" rot="R90"/>
<wire x1="0" y1="2.54" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="10.16" y2="-7.62" width="0.254" layer="94"/>
<wire x1="10.16" y1="-7.62" x2="10.16" y2="2.54" width="0.254" layer="94"/>
<wire x1="10.16" y1="2.54" x2="0" y2="2.54" width="0.254" layer="94"/>
<pin name="R4-1" x="15.24" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R4-2" x="17.78" y="-10.16" visible="pin" length="short" rot="R90"/>
<pin name="R4-3" x="20.32" y="-10.16" visible="pin" length="short" rot="R90"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="22.86" y2="-7.62" width="0.254" layer="94"/>
<wire x1="22.86" y1="-7.62" x2="22.86" y2="2.54" width="0.254" layer="94"/>
<wire x1="22.86" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="-27.94" y1="7.62" x2="-27.94" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-27.94" y1="-7.62" x2="27.94" y2="-7.62" width="0.254" layer="94"/>
<wire x1="27.94" y1="-7.62" x2="27.94" y2="7.62" width="0.254" layer="94"/>
<wire x1="27.94" y1="7.62" x2="-27.94" y2="7.62" width="0.254" layer="94"/>
</symbol>
<symbol name="LAYOUT_LEMO_12PIN">
<pin name="TEMPERATURE_DATA" x="25.4" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="TEMPERATURE-" x="27.94" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="TEMPERATURE+" x="30.48" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="HUMIDITY+" x="20.32" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="HUMIDITY-" x="17.78" y="20.32" visible="pin" length="short" rot="R270"/>
<text x="-24.13" y="20.32" size="1.27" layer="94">SENSORS</text>
<text x="-24.13" y="22.86" size="1.27" layer="94">EXTERIOR</text>
<pin name="HUMIDITY_DATA" x="15.24" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WINDSPEED1" x="-5.08" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WINDSPEED2" x="-2.54" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WIND_DIRECTION_1" x="5.08" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WIND_DIRECTION_2" x="7.62" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WIND_DIRECTION_3" x="10.16" y="20.32" visible="pin" length="short" rot="R270"/>
<pin name="WIND_DIRECTION_4" x="2.54" y="20.32" visible="pin" length="short" rot="R270"/>
<circle x="-24.13" y="7.62" radius="1.27" width="0.254" layer="94"/>
<circle x="-20.32" y="7.62" radius="1.27" width="0.254" layer="94"/>
<circle x="-20.32" y="3.81" radius="1.27" width="0.254" layer="94"/>
<circle x="-24.13" y="11.43" radius="1.27" width="0.254" layer="94"/>
<circle x="-20.32" y="0" radius="1.27" width="0.254" layer="94"/>
<circle x="-24.13" y="3.81" radius="1.27" width="0.254" layer="94"/>
<circle x="-16.51" y="7.62" radius="1.27" width="0.254" layer="94"/>
<circle x="-20.32" y="11.43" radius="1.27" width="0.254" layer="94"/>
<circle x="-27.94" y="7.62" radius="1.27" width="0.254" layer="94"/>
<circle x="-27.94" y="3.81" radius="1.27" width="0.254" layer="94"/>
<circle x="-16.51" y="3.81" radius="1.27" width="0.254" layer="94"/>
<circle x="-24.13" y="0" radius="1.27" width="0.254" layer="94"/>
<wire x1="-16.51" y1="7.62" x2="-11.43" y2="7.62" width="0.254" layer="92"/>
<wire x1="-20.32" y1="11.43" x2="-10.16" y2="11.43" width="0.254" layer="92"/>
<wire x1="-10.16" y1="11.43" x2="-8.89" y2="10.16" width="0.254" layer="92"/>
<wire x1="-19.05" y1="12.7" x2="-25.4" y2="12.7" width="0.254" layer="94" curve="-315"/>
<wire x1="-25.4" y1="12.7" x2="-25.4" y2="15.24" width="0.254" layer="94"/>
<wire x1="-25.4" y1="15.24" x2="-19.05" y2="15.24" width="0.254" layer="94"/>
<wire x1="-19.05" y1="15.24" x2="-19.05" y2="12.7" width="0.254" layer="94"/>
<wire x1="-11.43" y1="7.62" x2="-10.16" y2="6.35" width="0.254" layer="92"/>
<wire x1="-10.16" y1="6.35" x2="-10.16" y2="-10.16" width="0.254" layer="92"/>
<wire x1="-10.16" y1="-10.16" x2="-8.89" y2="-11.43" width="0.254" layer="92"/>
<wire x1="-8.89" y1="-11.43" x2="-2.54" y2="-11.43" width="0.254" layer="92"/>
<wire x1="-2.54" y1="-11.43" x2="-2.54" y2="0" width="0.254" layer="92"/>
<wire x1="-5.08" y1="0" x2="-5.08" y2="-10.16" width="0.254" layer="92"/>
<wire x1="-5.08" y1="-10.16" x2="-7.62" y2="-10.16" width="0.254" layer="92"/>
<wire x1="-7.62" y1="-10.16" x2="-8.89" y2="-8.89" width="0.254" layer="92"/>
<wire x1="-8.89" y1="-8.89" x2="-8.89" y2="6.35" width="0.254" layer="92"/>
<wire x1="-8.89" y1="6.35" x2="-8.89" y2="7.62" width="0.254" layer="92"/>
<wire x1="-8.89" y1="7.62" x2="-8.89" y2="10.16" width="0.254" layer="92"/>
<wire x1="25.4" y1="-8.89" x2="25.4" y2="-21.59" width="0.254" layer="92"/>
<wire x1="25.4" y1="-21.59" x2="-19.05" y2="-21.59" width="0.254" layer="92"/>
<wire x1="-19.05" y1="-21.59" x2="-20.32" y2="-20.32" width="0.254" layer="92"/>
<wire x1="-20.32" y1="-20.32" x2="-20.32" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-20.32" y1="-7.62" x2="-21.59" y2="-6.35" width="0.254" layer="92"/>
<wire x1="-21.59" y1="-6.35" x2="-27.94" y2="-6.35" width="0.254" layer="92"/>
<wire x1="-27.94" y1="-6.35" x2="-29.21" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-29.21" y1="-5.08" x2="-29.21" y2="2.54" width="0.254" layer="92"/>
<wire x1="-29.21" y1="2.54" x2="-27.94" y2="3.81" width="0.254" layer="92"/>
<wire x1="-27.94" y1="7.62" x2="-29.21" y2="7.62" width="0.254" layer="92"/>
<wire x1="-29.21" y1="7.62" x2="-30.48" y2="6.35" width="0.254" layer="92"/>
<wire x1="-30.48" y1="6.35" x2="-30.48" y2="-6.35" width="0.254" layer="92"/>
<wire x1="-30.48" y1="-6.35" x2="-29.21" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-29.21" y1="-7.62" x2="-22.86" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-22.86" y1="-7.62" x2="-21.59" y2="-8.89" width="0.254" layer="92"/>
<wire x1="-21.59" y1="-8.89" x2="-21.59" y2="-21.59" width="0.254" layer="92"/>
<wire x1="-21.59" y1="-21.59" x2="-20.32" y2="-22.86" width="0.254" layer="92"/>
<wire x1="-20.32" y1="-22.86" x2="27.94" y2="-22.86" width="0.254" layer="92"/>
<wire x1="27.94" y1="-22.86" x2="27.94" y2="-8.89" width="0.254" layer="92"/>
<wire x1="30.48" y1="-8.89" x2="30.48" y2="-24.13" width="0.254" layer="92"/>
<wire x1="30.48" y1="-24.13" x2="-21.59" y2="-24.13" width="0.254" layer="92"/>
<wire x1="-21.59" y1="-24.13" x2="-22.86" y2="-22.86" width="0.254" layer="92"/>
<wire x1="-22.86" y1="-22.86" x2="-22.86" y2="-10.16" width="0.254" layer="92"/>
<wire x1="-22.86" y1="-10.16" x2="-24.13" y2="-8.89" width="0.254" layer="92"/>
<wire x1="-24.13" y1="-8.89" x2="-30.48" y2="-8.89" width="0.254" layer="92"/>
<wire x1="-30.48" y1="-8.89" x2="-31.75" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-31.75" y1="-7.62" x2="-31.75" y2="10.16" width="0.254" layer="92"/>
<wire x1="-31.75" y1="10.16" x2="-30.48" y2="11.43" width="0.254" layer="92"/>
<wire x1="-30.48" y1="11.43" x2="-24.13" y2="11.43" width="0.254" layer="92"/>
<wire x1="20.32" y1="-2.54" x2="20.32" y2="-20.32" width="0.254" layer="92"/>
<wire x1="20.32" y1="-20.32" x2="-17.78" y2="-20.32" width="0.254" layer="92"/>
<wire x1="-17.78" y1="-20.32" x2="-19.05" y2="-19.05" width="0.254" layer="92"/>
<wire x1="-19.05" y1="-19.05" x2="-19.05" y2="-6.35" width="0.254" layer="92"/>
<wire x1="-19.05" y1="-6.35" x2="-20.32" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-20.32" y1="-5.08" x2="-24.13" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-24.13" y1="7.62" x2="-25.4" y2="7.62" width="0.254" layer="92"/>
<wire x1="-25.4" y1="7.62" x2="-26.67" y2="6.35" width="0.254" layer="92"/>
<wire x1="-26.67" y1="6.35" x2="-26.67" y2="-3.81" width="0.254" layer="92"/>
<wire x1="-26.67" y1="-3.81" x2="-25.4" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-25.4" y1="-5.08" x2="-24.13" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-24.13" y1="3.81" x2="-25.4" y2="2.54" width="0.254" layer="92"/>
<wire x1="-25.4" y1="2.54" x2="-25.4" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-25.4" y1="-2.54" x2="-24.13" y2="-3.81" width="0.254" layer="92"/>
<wire x1="-24.13" y1="-3.81" x2="-19.05" y2="-3.81" width="0.254" layer="92"/>
<wire x1="-19.05" y1="-3.81" x2="-17.78" y2="-5.08" width="0.254" layer="92"/>
<wire x1="-17.78" y1="-5.08" x2="-17.78" y2="-17.78" width="0.254" layer="92"/>
<wire x1="-17.78" y1="-17.78" x2="-16.51" y2="-19.05" width="0.254" layer="92"/>
<wire x1="-16.51" y1="-19.05" x2="17.78" y2="-19.05" width="0.254" layer="92"/>
<wire x1="17.78" y1="-19.05" x2="17.78" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-24.13" y1="0" x2="-24.13" y2="-1.27" width="0.254" layer="92"/>
<wire x1="-24.13" y1="-1.27" x2="-22.86" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-22.86" y1="-2.54" x2="-17.78" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-17.78" y1="-2.54" x2="-16.51" y2="-3.81" width="0.254" layer="92"/>
<wire x1="-16.51" y1="-3.81" x2="-16.51" y2="-16.51" width="0.254" layer="92"/>
<wire x1="-16.51" y1="-16.51" x2="-15.24" y2="-17.78" width="0.254" layer="92"/>
<wire x1="-15.24" y1="-17.78" x2="15.24" y2="-17.78" width="0.254" layer="92"/>
<wire x1="15.24" y1="-17.78" x2="15.24" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-16.51" y1="3.81" x2="-12.7" y2="3.81" width="0.254" layer="92"/>
<wire x1="-12.7" y1="3.81" x2="-11.43" y2="2.54" width="0.254" layer="92"/>
<wire x1="-11.43" y1="2.54" x2="-11.43" y2="-10.16" width="0.254" layer="92"/>
<wire x1="-11.43" y1="-10.16" x2="-11.43" y2="-11.43" width="0.254" layer="92"/>
<wire x1="-11.43" y1="-11.43" x2="-10.16" y2="-12.7" width="0.254" layer="92"/>
<wire x1="-10.16" y1="-12.7" x2="2.54" y2="-12.7" width="0.254" layer="92"/>
<wire x1="2.54" y1="-12.7" x2="2.54" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-20.32" y1="0" x2="-19.05" y2="-1.27" width="0.254" layer="92"/>
<wire x1="-19.05" y1="-1.27" x2="-17.78" y2="-1.27" width="0.254" layer="92"/>
<wire x1="-17.78" y1="-1.27" x2="-16.51" y2="-1.27" width="0.254" layer="92"/>
<wire x1="-16.51" y1="-1.27" x2="-15.24" y2="-2.54" width="0.254" layer="92"/>
<wire x1="-15.24" y1="-2.54" x2="-15.24" y2="-15.24" width="0.254" layer="92"/>
<wire x1="-15.24" y1="-15.24" x2="-13.97" y2="-16.51" width="0.254" layer="92"/>
<wire x1="-13.97" y1="-16.51" x2="10.16" y2="-16.51" width="0.254" layer="92"/>
<wire x1="10.16" y1="-16.51" x2="10.16" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-20.32" y1="3.81" x2="-19.05" y2="2.54" width="0.254" layer="92"/>
<wire x1="-19.05" y1="2.54" x2="-19.05" y2="1.27" width="0.254" layer="92"/>
<wire x1="-19.05" y1="1.27" x2="-17.78" y2="0" width="0.254" layer="92"/>
<wire x1="-17.78" y1="0" x2="-15.24" y2="0" width="0.254" layer="92"/>
<wire x1="-15.24" y1="0" x2="-13.97" y2="-1.27" width="0.254" layer="92"/>
<wire x1="-13.97" y1="-1.27" x2="-13.97" y2="-13.97" width="0.254" layer="92"/>
<wire x1="-13.97" y1="-13.97" x2="-12.7" y2="-15.24" width="0.254" layer="92"/>
<wire x1="-12.7" y1="-15.24" x2="7.62" y2="-15.24" width="0.254" layer="92"/>
<wire x1="7.62" y1="-15.24" x2="7.62" y2="-7.62" width="0.254" layer="92"/>
<wire x1="-20.32" y1="7.62" x2="-19.05" y2="7.62" width="0.254" layer="92"/>
<wire x1="-19.05" y1="7.62" x2="-17.78" y2="6.35" width="0.254" layer="92"/>
<wire x1="-17.78" y1="6.35" x2="-17.78" y2="2.54" width="0.254" layer="92"/>
<wire x1="-17.78" y1="2.54" x2="-16.51" y2="1.27" width="0.254" layer="92"/>
<wire x1="-16.51" y1="1.27" x2="-13.97" y2="1.27" width="0.254" layer="92"/>
<wire x1="-13.97" y1="1.27" x2="-12.7" y2="0" width="0.254" layer="92"/>
<wire x1="-12.7" y1="0" x2="-12.7" y2="-12.7" width="0.254" layer="92"/>
<wire x1="-12.7" y1="-12.7" x2="-11.43" y2="-13.97" width="0.254" layer="92"/>
<wire x1="-11.43" y1="-13.97" x2="5.08" y2="-13.97" width="0.254" layer="92"/>
<wire x1="5.08" y1="-13.97" x2="5.08" y2="-7.62" width="0.254" layer="92"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="LAYOUT-PHIDGET">
<gates>
<gate name="G$1" symbol="LAYOUT_PHIDGET" x="0" y="0"/>
</gates>
<devices>
<device name="" package="LAYOUT-PACKAGE">
<connects>
<connect gate="G$1" pin="AI-1" pad="P$1"/>
<connect gate="G$1" pin="AI-2" pad="P$2"/>
<connect gate="G$1" pin="AI-3" pad="P$3"/>
<connect gate="G$1" pin="AI-4" pad="P$4"/>
<connect gate="G$1" pin="AI-5" pad="P$5"/>
<connect gate="G$1" pin="AI-6" pad="P$6"/>
<connect gate="G$1" pin="AI-7" pad="P$7"/>
<connect gate="G$1" pin="AI-8" pad="P$8"/>
<connect gate="G$1" pin="DI-1" pad="P$9"/>
<connect gate="G$1" pin="DI-2" pad="P$10"/>
<connect gate="G$1" pin="DI-3" pad="P$11"/>
<connect gate="G$1" pin="DI-4" pad="P$12"/>
<connect gate="G$1" pin="DI-5" pad="P$13"/>
<connect gate="G$1" pin="DI-5V+" pad="P$14"/>
<connect gate="G$1" pin="DI-6" pad="P$15"/>
<connect gate="G$1" pin="DI-7" pad="P$16"/>
<connect gate="G$1" pin="DI-8" pad="P$17"/>
<connect gate="G$1" pin="DI-GND" pad="P$18"/>
<connect gate="G$1" pin="DO-1" pad="P$19"/>
<connect gate="G$1" pin="DO-2" pad="P$20"/>
<connect gate="G$1" pin="DO-3" pad="P$21"/>
<connect gate="G$1" pin="DO-4" pad="P$22"/>
<connect gate="G$1" pin="DO-5" pad="P$23"/>
<connect gate="G$1" pin="DO-5V+" pad="P$24"/>
<connect gate="G$1" pin="DO-6" pad="P$25"/>
<connect gate="G$1" pin="DO-7" pad="P$26"/>
<connect gate="G$1" pin="DO-8" pad="P$27"/>
<connect gate="G$1" pin="DO-GND" pad="P$28"/>
<connect gate="G$1" pin="M+" pad="P$29"/>
<connect gate="G$1" pin="M-" pad="P$30"/>
<connect gate="G$1" pin="U-1" pad="P$31"/>
<connect gate="G$1" pin="U-2" pad="P$32"/>
<connect gate="G$1" pin="U-3" pad="P$33"/>
<connect gate="G$1" pin="U-4" pad="P$34"/>
<connect gate="G$1" pin="U-5" pad="P$35"/>
<connect gate="G$1" pin="U-6" pad="P$36"/>
<connect gate="G$1" pin="USB2" pad="P$37"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="LAYOUT-SENSOR-TEMPERATURE">
<gates>
<gate name="G$1" symbol="LAYOUT_SENSOR_TEMPERATURE" x="0" y="0"/>
</gates>
<devices>
<device name="" package="LAYOUT-PACKAGE">
<connects>
<connect gate="G$1" pin="X" pad="P$1"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="LAYOUT-SENSOR-VOLTAGE">
<gates>
<gate name="G$1" symbol="LAYOUT_SENSOR_VOLTAGE" x="2.54" y="0"/>
</gates>
<devices>
<device name="" package="LAYOUT-PACKAGE">
<connects>
<connect gate="G$1" pin="+" pad="P$1"/>
<connect gate="G$1" pin="-" pad="P$2"/>
<connect gate="G$1" pin="X" pad="P$3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="LAYOUT-RELAY-BOARD">
<gates>
<gate name="G$1" symbol="LAYOUT_RELAY_BOARD" x="0" y="0"/>
</gates>
<devices>
<device name="" package="LAYOUT-PACKAGE">
<connects>
<connect gate="G$1" pin="R1-1" pad="P$24"/>
<connect gate="G$1" pin="R1-2" pad="P$23"/>
<connect gate="G$1" pin="R1-3" pad="P$22"/>
<connect gate="G$1" pin="R2-1" pad="P$21"/>
<connect gate="G$1" pin="R2-2" pad="P$20"/>
<connect gate="G$1" pin="R2-3" pad="P$19"/>
<connect gate="G$1" pin="R3-1" pad="P$18"/>
<connect gate="G$1" pin="R3-2" pad="P$17"/>
<connect gate="G$1" pin="R3-3" pad="P$16"/>
<connect gate="G$1" pin="R4-1" pad="P$15"/>
<connect gate="G$1" pin="R4-2" pad="P$14"/>
<connect gate="G$1" pin="R4-3" pad="P$13"/>
<connect gate="G$1" pin="USB1" pad="P$12"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="LAYOUT-LEMO-12PIN">
<gates>
<gate name="G$1" symbol="LAYOUT_LEMO_12PIN" x="-2.54" y="2.54"/>
</gates>
<devices>
<device name="" package="LEMO-12">
<connects>
<connect gate="G$1" pin="HUMIDITY+" pad="P12"/>
<connect gate="G$1" pin="HUMIDITY-" pad="P9"/>
<connect gate="G$1" pin="HUMIDITY_DATA" pad="P2"/>
<connect gate="G$1" pin="TEMPERATURE+" pad="P1"/>
<connect gate="G$1" pin="TEMPERATURE-" pad="P8"/>
<connect gate="G$1" pin="TEMPERATURE_DATA" pad="P7"/>
<connect gate="G$1" pin="WINDSPEED1" pad="P6"/>
<connect gate="G$1" pin="WINDSPEED2" pad="P5"/>
<connect gate="G$1" pin="WIND_DIRECTION_1" pad="P11"/>
<connect gate="G$1" pin="WIND_DIRECTION_2" pad="P10"/>
<connect gate="G$1" pin="WIND_DIRECTION_3" pad="P3"/>
<connect gate="G$1" pin="WIND_DIRECTION_4" pad="P4"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="U$1" library="launch-tower" deviceset="LAYOUT-PHIDGET" device=""/>
<part name="U$2" library="launch-tower" deviceset="LAYOUT-SENSOR-TEMPERATURE" device=""/>
<part name="U$3" library="launch-tower" deviceset="LAYOUT-SENSOR-VOLTAGE" device=""/>
<part name="U$4" library="launch-tower" deviceset="LAYOUT-SENSOR-VOLTAGE" device=""/>
<part name="U$5" library="launch-tower" deviceset="LAYOUT-SENSOR-VOLTAGE" device=""/>
<part name="U$6" library="launch-tower" deviceset="LAYOUT-SENSOR-VOLTAGE" device=""/>
<part name="U$7" library="launch-tower" deviceset="LAYOUT-SENSOR-VOLTAGE" device=""/>
<part name="U$8" library="launch-tower" deviceset="LAYOUT-RELAY-BOARD" device=""/>
<part name="U$9" library="launch-tower" deviceset="LAYOUT-LEMO-12PIN" device=""/>
</parts>
<sheets>
<sheet>
<plain>
<text x="109.22" y="33.02" size="1.778" layer="91">Internal Temperature</text>
<text x="10.16" y="76.2" size="1.778" layer="91">Ignition</text>
<text x="50.8" y="88.9" size="1.778" layer="91">Shorepower Control</text>
<text x="111.76" y="83.82" size="1.778" layer="91">Shorepower</text>
<text x="111.76" y="73.66" size="1.778" layer="91">Solar</text>
<text x="111.76" y="63.5" size="1.778" layer="91">System</text>
<text x="111.76" y="53.34" size="1.778" layer="91">Rocket Ready</text>
<text x="111.76" y="43.18" size="1.778" layer="91">Ignition Battery</text>
<text x="25.4" y="86.36" size="1.778" layer="91">Index</text>
<text x="27.94" y="76.2" size="1.778" layer="91">0</text>
<text x="27.94" y="63.5" size="1.778" layer="91">1</text>
<text x="27.94" y="50.8" size="1.778" layer="91">2</text>
<text x="27.94" y="38.1" size="1.778" layer="91">3</text>
<text x="73.66" y="68.58" size="1.778" layer="91">0</text>
<text x="73.66" y="48.26" size="1.778" layer="91">0</text>
<text x="73.66" y="43.18" size="1.778" layer="91">0</text>
<text x="71.12" y="43.18" size="1.778" layer="91">1</text>
<text x="73.66" y="50.8" size="1.778" layer="91">1</text>
<text x="71.12" y="68.58" size="1.778" layer="91">1</text>
<text x="73.66" y="53.34" size="1.778" layer="91">2</text>
<text x="68.58" y="43.18" size="1.778" layer="91">2</text>
<text x="68.58" y="68.58" size="1.778" layer="91">2</text>
<text x="73.66" y="55.88" size="1.778" layer="91">3</text>
<text x="66.04" y="43.18" size="1.778" layer="91">3</text>
<text x="66.04" y="68.58" size="1.778" layer="91">3</text>
<text x="63.5" y="43.18" size="1.778" layer="91">4</text>
<text x="73.66" y="58.42" size="1.778" layer="91">4</text>
<text x="63.5" y="68.58" size="1.778" layer="91">4</text>
<text x="73.66" y="60.96" size="1.778" layer="91">5</text>
<text x="60.96" y="43.18" size="1.778" layer="91">5</text>
<text x="60.96" y="68.58" size="1.778" layer="91">5</text>
<text x="73.66" y="63.5" size="1.778" layer="91">6</text>
<text x="58.42" y="43.18" size="1.778" layer="91">6</text>
<text x="58.42" y="68.58" size="1.778" layer="91">6</text>
<text x="73.66" y="66.04" size="1.778" layer="91">7</text>
<text x="55.88" y="68.58" size="1.778" layer="91">7</text>
<text x="55.88" y="43.18" size="1.778" layer="91">7</text>
</plain>
<instances>
<instance part="U$1" gate="G$1" x="63.5" y="58.42" rot="R90"/>
<instance part="U$2" gate="G$1" x="101.6" y="33.02" rot="R270"/>
<instance part="U$3" gate="G$1" x="101.6" y="71.12" rot="R270"/>
<instance part="U$4" gate="G$1" x="101.6" y="60.96" rot="R270"/>
<instance part="U$5" gate="G$1" x="101.6" y="50.8" rot="R270"/>
<instance part="U$6" gate="G$1" x="101.6" y="40.64" rot="R270"/>
<instance part="U$7" gate="G$1" x="101.6" y="81.28" rot="R270"/>
<instance part="U$8" gate="G$1" x="30.48" y="55.88" rot="R270"/>
<instance part="U$9" gate="G$1" x="58.42" y="0"/>
</instances>
<busses>
</busses>
<nets>
<net name="N$1" class="0">
<segment>
<pinref part="U$8" gate="G$1" pin="USB1"/>
<wire x1="40.64" y1="30.48" x2="40.64" y2="48.26" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="U-1"/>
<wire x1="40.64" y1="48.26" x2="43.18" y2="48.26" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$4" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="AI-3"/>
<wire x1="83.82" y1="53.34" x2="88.9" y2="53.34" width="0.1524" layer="91"/>
<wire x1="88.9" y1="53.34" x2="88.9" y2="22.86" width="0.1524" layer="91"/>
<wire x1="88.9" y1="22.86" x2="78.74" y2="22.86" width="0.1524" layer="91"/>
<pinref part="U$9" gate="G$1" pin="HUMIDITY_DATA"/>
<wire x1="78.74" y1="22.86" x2="76.2" y2="22.86" width="0.1524" layer="91"/>
<wire x1="76.2" y1="22.86" x2="73.66" y2="22.86" width="0.1524" layer="91"/>
<wire x1="73.66" y1="22.86" x2="73.66" y2="20.32" width="0.1524" layer="91"/>
<pinref part="U$9" gate="G$1" pin="HUMIDITY-"/>
<wire x1="76.2" y1="20.32" x2="76.2" y2="22.86" width="0.1524" layer="91"/>
<pinref part="U$9" gate="G$1" pin="HUMIDITY+"/>
<wire x1="78.74" y1="20.32" x2="78.74" y2="22.86" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$5" class="0">
<segment>
<wire x1="91.44" y1="20.32" x2="91.44" y2="55.88" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="AI-4"/>
<wire x1="91.44" y1="55.88" x2="83.82" y2="55.88" width="0.1524" layer="91"/>
<pinref part="U$9" gate="G$1" pin="TEMPERATURE_DATA"/>
<wire x1="91.44" y1="20.32" x2="83.82" y2="20.32" width="0.1524" layer="91"/>
</segment>
</net>
<net name="IGNITION" class="0">
<segment>
<pinref part="U$8" gate="G$1" pin="R1-3"/>
<wire x1="7.62" y1="73.66" x2="20.32" y2="73.66" width="0.1524" layer="91"/>
<pinref part="U$8" gate="G$1" pin="R1-2"/>
<wire x1="20.32" y1="73.66" x2="20.32" y2="76.2" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$6" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="AI-1"/>
<wire x1="83.82" y1="48.26" x2="83.82" y2="33.02" width="0.1524" layer="91"/>
<pinref part="U$2" gate="G$1" pin="X"/>
<wire x1="83.82" y1="33.02" x2="93.98" y2="33.02" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$7" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="AI-2"/>
<wire x1="83.82" y1="50.8" x2="86.36" y2="50.8" width="0.1524" layer="91"/>
<wire x1="86.36" y1="50.8" x2="86.36" y2="43.18" width="0.1524" layer="91"/>
<pinref part="U$6" gate="G$1" pin="X"/>
<wire x1="86.36" y1="43.18" x2="93.98" y2="43.18" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$8" class="0">
<segment>
<pinref part="U$5" gate="G$1" pin="X"/>
<wire x1="93.98" y1="53.34" x2="93.98" y2="58.42" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="AI-5"/>
<wire x1="93.98" y1="58.42" x2="83.82" y2="58.42" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$9" class="0">
<segment>
<pinref part="U$4" gate="G$1" pin="X"/>
<wire x1="93.98" y1="63.5" x2="93.98" y2="60.96" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="AI-6"/>
<wire x1="93.98" y1="60.96" x2="83.82" y2="60.96" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$10" class="0">
<segment>
<pinref part="U$3" gate="G$1" pin="X"/>
<wire x1="93.98" y1="73.66" x2="91.44" y2="73.66" width="0.1524" layer="91"/>
<wire x1="91.44" y1="73.66" x2="91.44" y2="63.5" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="AI-7"/>
<wire x1="91.44" y1="63.5" x2="83.82" y2="63.5" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$11" class="0">
<segment>
<pinref part="U$7" gate="G$1" pin="X"/>
<wire x1="93.98" y1="83.82" x2="88.9" y2="83.82" width="0.1524" layer="91"/>
<wire x1="88.9" y1="83.82" x2="88.9" y2="66.04" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="AI-8"/>
<wire x1="88.9" y1="66.04" x2="83.82" y2="66.04" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="DI-GND"/>
<pinref part="U$9" gate="G$1" pin="WINDSPEED1"/>
<wire x1="53.34" y1="33.02" x2="53.34" y2="20.32" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="DI-8"/>
<pinref part="U$9" gate="G$1" pin="WINDSPEED2"/>
<wire x1="55.88" y1="33.02" x2="55.88" y2="20.32" width="0.1524" layer="91"/>
</segment>
</net>
<net name="SHOREPOWER" class="0">
<segment>
<pinref part="U$7" gate="G$1" pin="+"/>
<pinref part="U$7" gate="G$1" pin="-"/>
<wire x1="109.22" y1="83.82" x2="109.22" y2="81.28" width="0.1524" layer="91"/>
<wire x1="109.22" y1="81.28" x2="119.38" y2="81.28" width="0.1524" layer="91"/>
</segment>
</net>
<net name="SOLAR" class="0">
<segment>
<pinref part="U$3" gate="G$1" pin="-"/>
<wire x1="109.22" y1="71.12" x2="119.38" y2="71.12" width="0.1524" layer="91"/>
<pinref part="U$3" gate="G$1" pin="+"/>
<wire x1="109.22" y1="73.66" x2="109.22" y2="71.12" width="0.1524" layer="91"/>
</segment>
</net>
<net name="SYSTEM" class="0">
<segment>
<pinref part="U$4" gate="G$1" pin="+"/>
<pinref part="U$4" gate="G$1" pin="-"/>
<wire x1="109.22" y1="63.5" x2="109.22" y2="60.96" width="0.1524" layer="91"/>
<wire x1="109.22" y1="60.96" x2="119.38" y2="60.96" width="0.1524" layer="91"/>
</segment>
</net>
<net name="ROCKET_READY" class="0">
<segment>
<pinref part="U$5" gate="G$1" pin="+"/>
<pinref part="U$5" gate="G$1" pin="-"/>
<wire x1="109.22" y1="53.34" x2="109.22" y2="50.8" width="0.1524" layer="91"/>
<wire x1="109.22" y1="50.8" x2="119.38" y2="50.8" width="0.1524" layer="91"/>
</segment>
</net>
<net name="IGNITION_BATTERY" class="0">
<segment>
<pinref part="U$6" gate="G$1" pin="+"/>
<pinref part="U$6" gate="G$1" pin="-"/>
<wire x1="109.22" y1="43.18" x2="109.22" y2="40.64" width="0.1524" layer="91"/>
<wire x1="109.22" y1="40.64" x2="119.38" y2="40.64" width="0.1524" layer="91"/>
</segment>
</net>
<net name="SHOREPOWER_CTL" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="DO-8"/>
<wire x1="55.88" y1="81.28" x2="55.88" y2="86.36" width="0.1524" layer="91"/>
<wire x1="55.88" y1="86.36" x2="68.58" y2="86.36" width="0.1524" layer="91"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
</eagle>
