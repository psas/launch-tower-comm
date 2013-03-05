using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Servo_Multi
{
    class Sensor_1124
    {
        public double calculateTempF(int val)
        {
            int rOffset = 0;    // custom offset is equation is wrong
            double tmp = ((val * 0.39996) - 77.9998) + rOffset; //77.9998
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            //string tempString = tmp.ToString("0.##"); // +"°F";
            return tmp;
        }

        public double calculateTempC(int val)
        {
            double tmp = (val * 0.2222) - 61.111;
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            //string tempString = tmp.ToString("0.##"); // +"°c";
            return tmp;
        }

        private void Sensor_1124_Load(object sender, EventArgs e)
        {

        }
    }
}
