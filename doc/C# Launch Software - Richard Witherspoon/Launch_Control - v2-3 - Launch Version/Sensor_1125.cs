using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Servo_Multi
{
    class Sensor_1125
    {
        public double calculateTempF(int val)
        {
            double tmp = (val * 0.39996) - 77.9998;
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            //string tempString = tmp.ToString("0.##"); // +"°F";
            return tmp;
        }

        public double calculateTempC(int val)
        {
            double tmp = (val * 0.2222) - 61.111;
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            //string tempString = tmp.ToString("0.##"); // + "°c";
            return tmp;
        }

        public double calculateHumidity(int val)
        {
            double tmp = (val * 0.1906) - 40.2;
            tmp = Math.Round(tmp, 2);                           // round to 2 decimal places
            //string tempString = tmp.ToString("0.##"); // + "%";
            return tmp;
        }

        private void Sensor_1125_Load(object sender, EventArgs e)
        {

        }
    }
}
