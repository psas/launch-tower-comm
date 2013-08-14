using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Servo_Multi
{
    class Sensor_1135
    {
        public double getVoltage(int val)
        {
            int rOffset = 1;                                    // custom offset is equation is wrong
            double tmp = ((val / 13.62) - 36.7107);             // make calculation
            tmp = (tmp < 0) ? tmp : tmp + rOffset;              // modify equation
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            string tempString = tmp.ToString("0.###"); // + "V";
            return tmp;
        }

        public double calculateVoltage(int val)
        {
            int rOffset = 1;                                    // custom offset is equation is wrong
            double tmp = ((val / 13.62) - 36.7107);             // make calculation
            tmp = (tmp < 0) ? tmp : tmp + rOffset;              // modify equation
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            return tmp;
        }
        
        private void Sensor_1135_Load(object sender, EventArgs e)
        {

        }
    }
}
