using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Servo_Multi
{
    class Sensor_WindSpeed
    {
        //public int totalTick = 0;                    // holds the current count
        //public int lastTick = 0;
        public int curTick = 0;
        public int TriggersPerSecondMPH = 1;

        public int LastTotalTick = 0;
        public int LastCurTick = 0;

        // note : (if we're storing ticks every 1 second then there should be 30 periods because equation is based on wind speed Summed over 30 seconds.)
        public int totalPeriodsToSum = 30;                      // how many periods are being summed for 30seconds 
        public Queue<int> tickCount = new Queue<int>(30);       // needs to be same # of periods as totalPeriodsToSum

        


        // ----- FUNCTION :: Calculate the actual windspeed from inputs
        public double calculateWindSpeed()
        {
            // 1. Count rotations for 30 seconds
            // 2. Multiply # of rotation by diameter of anemometer in inches and divide by 168 = wind speed in MPH
            // 3. Multiply # of rotations by the diameter in centimeters and divide by 265  = wind speed in KPH.

            //revolutions = 178
            //diameter = 6.5 inches
            //Circumference = DataBindings * Pi
            //Circumference = 20.41 inches
            //figure out how far the anemometer travels in one rotation 20.41inches/1 X 1ft/12inches = 1.70 feet
            //how many feet travelling in one minute ==> 1.70feet/1 X 178revolutions/1minute = 302.6 feet/minute
            //302.6feet/1minute X 60min/1hr = 18,156ft/hr
            //18156feet/1hr X 1mi/5280feet = 3.44 MPH

            // v = r*w
            // v = linear speed
            // r = radius
            // w = angular speed

            int tempCurTick = curTick;          // immediately store current number of ticks - in case more ticks happen while making calculation
            int totalTicks = 0;                 // initialize local variable to hold total count of ticks
            

            if (tickCount.Count > (totalPeriodsToSum-1))
            {
                tickCount.Dequeue();            // remove the 0th element from queue if present (FIFO model so its the oldest data)
            }

            
            tickCount.Enqueue(curTick);         // add current tick count onto queue
            
            foreach (int number in tickCount)
            {
                totalTicks += number;           // sum up all the tick intervals
            }
            
            
            // ===== NOTE :: need to adjsut in case there aren't enough queued values


            double speed = (totalTicks / TriggersPerSecondMPH);     // calculate the speed
            speed = Math.Round(speed, 2);                           // round the speed to 2 decimaml places

            curTick = curTick - tempCurTick;    // reset the current tick - but allow ticks that happened during clauclation to stay
            
            return speed;
        }

        private void Sensor_WindSpeed_Load(object sender, EventArgs e)
        {
         
        }
    }
}
