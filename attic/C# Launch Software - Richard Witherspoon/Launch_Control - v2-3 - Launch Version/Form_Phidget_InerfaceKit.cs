/*
 *      Created By: Richard Witherspoon
 *      Created On: 2012-08-03
 * Last Updated By: 
 * Last Updated On: 
 *     Description: General Phidget code - moved here so not implemented on Form1.cs
*/

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using Phidgets;             // for the phidget class and the exceptions class
using Phidgets.Events;      // for the event handling classes
using System.Collections;

namespace Servo_Multi
{
    public class Form_Phidget_InerfaceKit
    {

        public Form1 _mainForm;    // get a reference to Form1

        public Form_Phidget_InerfaceKit(Form1 mainForm)
        {
            // FUNCTION :: Instantiate the class
            _mainForm = mainForm;   // store the reference to main form
        }

        


    } //end class
} //end namespace