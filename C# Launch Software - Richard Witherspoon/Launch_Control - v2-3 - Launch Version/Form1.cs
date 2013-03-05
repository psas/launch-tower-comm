/* - Servo multi -
 * This example is very similar to the Servo-full example, except that this example demonstrates attaching and using two Phidget
 * Servo Controllers simultaneously.  Please note the two serial number variables declared at the beginning of the class.
 * These are used to store the serial numbers of the Phidgets Servos that we are attaching.  Please change these to reflect the serial
 * numbers of your own phidgets before running the program or you will find that it won't work.
 *
 * Note: This example can be easily modified to support more than two Phidget Servos.  To do this you simply need to create
 * seperate servo objects for each new Phidget Servo Controller you wish to be able to control and supply the serial number of each
 * subsequent device to the respect object's open() method.
 *
 * Copyright 2007 Phidgets Inc.  
 * This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
 * To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
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
using System.Text.RegularExpressions;   // used for Regex Checks
using System.Windows.Forms.DataVisualization.Charting;      // used for charting


//using System.Windows.Forms;
using System.Threading;             // used for advanced charting
/* 
 * =======================================================================================================
 *
 * 2012-08-02
 * Added code to read settings from external text file
 * 
 * 
 * =======================================================================================================
 */





/*
 * TO DO LIST
 * Animated graphs - http://www.codeproject.com/Articles/32836/A-simple-C-library-for-graph-plotting
 * */


namespace Servo_Multi
{
    public partial class Form1 : Form
    {

        string inputFile = "c:\\config.txt";                        // input file - which sensors in which location
        string outputFileStatus = "c:\\programstatus.txt";          // output file - program messages



        private double maxVoltageSolar = 24;                // maximum voltage on solar panel - before error thrown
        private double maxVoltageBattSystem = 24;           // maximum voltage on system battery - before error thrown
        private double maxVoltageBattIgnition = 24;         // maximum voltage on ignition battery - before error thrown
        private double maxVoltageRocket = 20;               // maximum voltage on rocket umbilical - before error thrown

        private double minVoltageSolar = 8;                 // minimum default on solar panel - before error thrown
        private double minVoltageBattSystem = 8;            // minimum default on system battery - before error thrown
        private double minVoltageBattIgnition = 8;          // minimum default voltage on ignition battery - before error thrown
        private double minVoltageRocket = 15;               // minimum default voltage on rocket umbilical - before error thrown

        private int sensorDataRate = 1;                     // default analog sensor rate

        private Sensor_WindSpeed ZsensorWindspeed;
        //public sensorWindspeed;
        //
        //public 
        
        //private double TriggersPerSecondMPH = 1;            // how many triggers per timer tick = 1 MPH
        private int timerTickInterval = 1000;               // tick interval (MS) - how often are we checking wind speed
        
        

        // ----- PHIDGET SERIAL NUMBERS -----
        int serialNuminterface1 = 178346;
        int serialNumEncoder1   = 82292;
        int serialNumRelay1     = 259173;


        // ----- GRAPH CONFIGURATION -----
        
        private int NumGraphs = 4;
        private String CurExample = "TILED_VERTICAL_AUTO";
        private String CurColorSchema = "GRAY";
        private PrecisionTimer.Timer mTimer = null;
        private DateTime lastTimerTick = DateTime.Now;
        



        // ----- NON-MODIFIABLE VARIABLES -----
        Phidgets.Encoder encoder;                               // Declare an encoder object
        private InterfaceKit ifKit;                             // Declare an interface kit object
        private InterfaceKit relayKit;                          // Declare a relay interface kit object

        private ArrayList inputArray;
        private ErrorEventBox errorBox;
        private TextBox[] sensorInArray = new TextBox[8];       // stores analog sensor value

        public bool phidgetEncoderFound = false;                // stores if phidget device found
        public bool phidgetInterfaceFound = false;              // stores if phidget device found
        public bool phidgetRelayFound = false;                  // stores if phidget device found

        string phidgetServerIpAddress = "";                     // will store IP Address
        int phidgetServerPortNumber = 0;                        // will store port number
        string phidgetServerPassword = "";                      // will store password


        public string[] analogSensorInput = new string[8];      // will hold what sensor is in each analog slot
        public string[] digitalRelayOutput = new string[4];     // will hold what each relay is triggering
        public string[] gpioOutput = new string[8];             // will hold what each gpio is triggering
        public string[] digitalSensorInput = new string[8];     // will hold what sensor is in each digital slot
        

        private HiPerfTimer pt;

        const int velQueueSize = 50;                            // ??? - may be used for rotary encoder
        Queue velData = new Queue(velQueueSize);                // ??? - may be used for rotary encoder


        // initialize dictionary to hold phidget values
        public Dictionary<string, double> phidgetValues = new Dictionary<string, double>();

        string outputFileSensor = "";                           // will hold output filename - sensor logs


        public float encoderZeroPosition = 0;                   // will hold the encoder 0 position (pointing north)


        /*
         * ====================================================================================================
         * ====================== FORM FUNCTIONS ==============================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Application is starting up
        public Form1()
        {
            InitializeComponent();                                          // initialize this form controls
            
            LogScreen("Welcome to Launch Control v1.0");                    // log message
            LogScreen("Initializing Form");                                 // log message
            
            ifKit_Uninitialize_Display();                                   // handle form elements related to ifKit
            relayKit_Uninitialize_Display();                                // handle form elements related to relayKit
            encoder_Uninitialize_Display();                                 // handle form elements related to encoder

            errorBox = new ErrorEventBox();                                 // declare error handling class
            
            LogScreen("Processing Phidget device status.");                 // log message
            NetworkDisplayDisconnected();                                   // handle initial network config

            TextFromFile ZtxtObj = new TextFromFile();                      // instantiate the class
            string theOutput = ZtxtObj.readConfigFile(inputFile, analogSensorInput, digitalRelayOutput, gpioOutput, digitalSensorInput);                 // open and read the file
            txtTempOutput.Text = theOutput;


            initializeLogfile();                                            // create the logfile (with unique name)
            initializePhidgetValueDictionary();                             // initialize the dictionaty holding phidget log values
            timerLogfileInitialize();                                       // initialize the logfile timer


            ZsensorWindspeed = new Sensor_WindSpeed();

            tmrWindSpeed.Interval = 500;
            tmrWindSpeed.Enabled = true;


            /*
            if (false)
            {
                // ---------------- configure the chart ----------------
                var series = chart1.Series.FindByName("Series1");
                //series.ChartType = SeriesChartType.Line;
                //series.XValueType = ChartValueType.Int32;

                // set view range to [0,max]

                var chartArea = chart1.ChartAreas[series.ChartArea];
                chartArea.AxisX.Minimum = 0;
                chartArea.AxisX.Maximum = 100;

                // enable autoscroll
                chartArea.CursorX.AutoScroll = true;

                // let's zoom to [0,blockSize] (e.g. [0,100])
                chartArea.AxisX.ScaleView.Zoomable = true;
                chartArea.AxisX.ScaleView.SizeType = DateTimeIntervalType.Number;
                int blockSize = 20;
                int position = 0;
                int size = blockSize;
                chartArea.AxisX.ScaleView.Zoom(position, size);

                // disable zoom-reset button (only scrollbar's arrows are available)
                chartArea.AxisX.ScrollBar.ButtonStyle = ScrollBarButtonStyles.SmallScroll;

                // set scrollbar small change to blockSize (e.g. 100)
                chartArea.AxisX.ScaleView.SmallScrollSize = blockSize;

                // turn off gridlines on chart
                chart1.ChartAreas[0].AxisX.MajorGrid.Enabled = false;
                chart1.ChartAreas[0].AxisX.MinorGrid.Enabled = false;
                //chart1.ChartAreas[0].AxisY.MajorGrid.Enabled = false;
                //chart1.ChartAreas[0].AxisY.MinorGrid.Enabled = false;
            }
            */

            /*
            display.Smoothing = System.Drawing.Drawing2D.SmoothingMode.None;
            CalcDataGraphs();
            display.Refresh();
            mTimer = new PrecisionTimer.Timer();
            mTimer.Period = 40;                         // 20 fps
            mTimer.Tick += new EventHandler(OnTimerTick);
            lastTimerTick = DateTime.Now;
            mTimer.Start();        
            */
        }
















        // ----- FUNCTION :: Application is terminating
        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            Application.DoEvents();     // ----- Run any events in the message queue - otherwise close will hang if there are any outstanding events
            PhidgetsDisconnect();       // disconnect all phidget devices
        }

        private void picRelayUmbilical_Click(object sender, EventArgs e)
        {
            if (phidgetInterfaceFound)
            {
                processGPIOButton("gpioUmbilical", picGPIOUmbilical);

                int GPIONum = Array.IndexOf(gpioOutput, "gpioUmbilical");       // figure out the GPIO number based on array position
                bool curStatus = ifKit.outputs[GPIONum];                        // get current status of this GPIO
                curStatus = !curStatus;                                         // flip status because ifkit won't have detected change yet

                if (curStatus == true)
                {
                    //lblRocketFire.AutoSize = true;
                    lblRocketFire.Height = 40;
                    lblRocketFire.Text = "Umbilical Power" + Environment.NewLine + "Must Be Off";   // set title of box
                    picRelayIgnition.Visible = false;                                               // hide the toggle switch

                    // determine if ignition currently happening -s top it if so
                    int relayNum = Array.IndexOf(digitalRelayOutput, "relayRocketFire");        // figure out the relay number based on array position
                    bool curStatusZ = relayKit.outputs[relayNum];                               // get current status of this relay

                    if (curStatusZ == true)
                    {
                        processRelayButton("relayRocketFire", picRelayIgnition);                // call function to invert relay status
                    }

                }
                else
                {
                    //lblRocketFire.AutoSize = false;
                    lblRocketFire.Height = 20;
                    lblRocketFire.Text = "Rocket Ignition";                 // set title of box
                    picRelayIgnition.Visible = true;                        // show the toggle switch
                }
            } // end checking ifkit attached
        }

        private void picRelayOther_Click(object sender, EventArgs e)
        {
            processRelayButton("relayOther", picRelayOther);
        }

        private void picRelaySiren_Click(object sender, EventArgs e)
        {
            processRelayButton("relaySiren", picRelaySiren);
        }

        private void picRelayLight_Click(object sender, EventArgs e)
        {
            processRelayButton("relayLight", picRelayLight);
        }

        private void picRelayIgnition_Click(object sender, EventArgs e)
        {
            processRelayButton("relayRocketFire", picRelayIgnition);
        }





        private void btnConnectPhidgets_Click(object sender, EventArgs e)
        {
            PhidgetsConnectSetup();         // connect to phidget devices
            NetworkDisplayConnected();      // run cleanup on the netowrk display (???)
        }

        private void btnDisconnectPhidgets_Click(object sender, EventArgs e)
        {
            PhidgetsDisconnect();           // disconnect from phidget devices
            NetworkDisplayDisconnected();   // run cleanup on the netowrk display
        }

        void processGPIOButton(string gpioTitle, PictureBox pic)
        {
            if (phidgetInterfaceFound)
            {
                int GPIONum = Array.IndexOf(gpioOutput, gpioTitle);                         // figure out the GPIO number based on array position
                bool curStatus = ifKit.outputs[GPIONum];                                    // get current status of this GPIO
                bool newStatus = !curStatus;                                                // swap the GPIO high/low status
                Image imgNew = (newStatus == true) ? picSwitchOn.Image : picSwitchOff.Image;
                
                string cbName = "cbGPIOStatus" + GPIONum;                                   // create name of checkbox
                CheckBox cb = (CheckBox)this.Controls.Find(cbName, true)[0];                // find checkbox control

                cb.Checked = newStatus;                                                     // check the visual checkbox indicator
                ifKit.outputs[GPIONum] = newStatus;                                         // toggle the actual GPIO
                pic.Image = imgNew;                                                         // swap out the image
            }
        }

        void processRelayButton(string relayTitle, PictureBox pic)
        {
            if (relayKit != null)
            {
                int relayNum = Array.IndexOf(digitalRelayOutput, relayTitle);               // figure out the relay number based on array position
                bool curStatus = relayKit.outputs[relayNum];                                // get current status of this relay
                bool newStatus = !curStatus;                                                // swap the relay on/off status
                Image imgNew = (newStatus == true) ? picSwitchOn.Image : picSwitchOff.Image;

                string cbName = "cbRelayStatus" + relayNum;                                 // create name of checkbox
                CheckBox cb = (CheckBox)this.Controls.Find(cbName, true)[0];                // find checkbox control

                cb.Checked = newStatus;                                                     // check the visual checkbox indicator
                relayKit.outputs[relayNum] = newStatus;                                     // toggle the actual relay
                pic.Image = imgNew;                                                         // swap out the image
            }
        }


        // ----- FUNCTION :: Connect to all phidget devices over network
        private void PhidgetsConnectSetup()
        {
            bool passChecks = true;
            phidgetServerIpAddress = txtIPAddress.Text;
            phidgetServerPassword = txtServerPassword.Text;
            phidgetServerPortNumber = (isInt32(txtPortAddress.Text)) ? Convert.ToInt32(txtPortAddress.Text) : 0;
            
            if (phidgetServerPortNumber == 0) {
                MessageBox.Show("ERROR :: Port number is not a valid sequence of digits.");
                passChecks = false;
            }

            if (phidgetServerIpAddress == "")
            {
                MessageBox.Show("ERROR :: ENTER AN IP ADDRESS");
                passChecks = false;
            }

            if (passChecks) {

                NetworkDisplayConnected();      // disable connection area

                InitializePhidgetEncoder();     // INITIALIZE THE ROTARY ENCODER
                InitializePhidgetInterface();   // INITIALIZE THE INTERFACE KIT
                InitializePhidgetRelay();       // INITIALIZE THE RELAY INTERFACE KIT

                makeSensorInArray();            // initialize the sensor array textfield values - analog inputs
                makeDigiOutArray();             // initialize the sensor array textfield values - digital outputs



                // ----- INITIALIZE THE HIGH PERFORMANCE COUNTER (for wind speed calculation) -----
                //pt = new HiPerfTimer();     // create a new PerfTimer object
                //pt.Start();                             // start the timer

                tmrWindSpeed.Interval = timerTickInterval;      // Interval in MS
                tmrWindSpeed.Enabled = true;                    // Turn on the timer

            } //end ipAddress check
        }


        









        private void tmrWindSpeed_Tick(object sender, EventArgs e)
        {
            double curVal = ZsensorWindspeed.calculateWindSpeed();

            phidgetValues["wind-speed"] = curVal;           // Store value in dictionary for logfile writting
            lblTowerWindSpeed.Text = curVal.ToString();     // output speed to the screen

            if (false) 
            {
                // ------ OUTPUT THE WIND SPEED QUEUE ------
                string newline = (txtLogToScreen.Text != "") ? Environment.NewLine : "";        // figure out newline character
                int count = 0;
                string output = "";
                foreach (int number in ZsensorWindspeed.tickCount)
                {
                    output += count + ": " + number.ToString() + newline;
                    count++;
                }
                lblTick0.Text = output;
            }
        }


        //Modify the sensitivity of the analog inputs. In other words, the amount that the inputs
        //must change before triggering sensorchange events.
        private void inputIKTrk_Scroll(object sender, EventArgs e)
        {
            try
            {
                for (int i = 0; i < ifKit.sensors.Count; i++)
                {
                    ifKit.sensors[i].Sensitivity = inputIKTrk.Value;
                }
                sensitivityIKTxt.Text = inputIKTrk.Value.ToString();
            }
            catch (PhidgetException ex)
            {
                MessageBox.Show(ex.Description);
            }
        }


        // This method will associate the sensorInArray with text boxes that display the current values 
        // of the analog inputs on the interface kit. It will also initialize the visibility of the
        // text boxes and analog input labeling to false.
        private void makeSensorInArray()
        {
            for (int i = 0; i < 8; i++)
            {
                ((Label)analogInputsGroupBox.Controls["analogInputLabel" + i.ToString()]).Visible = true;
                sensorInArray[i] = (TextBox)analogInputsGroupBox.Controls["textBox" + (i + 1).ToString()];
                sensorInArray[i].Visible = true;
            }
        }






        /*
         * ====================================================================================================
         * ====================== INTERFACE KIT FUNCTIONS =====================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void ifKit_Uninitialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            lblTowerTemp.Text = "err";
            lblTowerHumidity.Text = "err";
            lblEnclosureTemp.Text = "err";
            //grpPowerSystems.Enabled = false;
            //grpAtmosphericConditions.Enabled = false;
            //grpUmbilicalPower.Enabled = false;

            picBattSolar.Image = imgListBatteryLevel.Images[0];
            picBattSystem.Image = imgListBatteryLevel.Images[0];
            picBattIgnition.Image = imgListBatteryLevel.Images[0];
            picBattRocket.Image = imgListBatteryLevel.Images[0];

            txtBattSolarLevelSet.Text = 0.ToString();                  // initial minimum voltage value
            txtBattSystemLevelSet.Text = 0.ToString();                 // initial minimum voltage value
            txtBattIgnitionLevelSet.Text = 0.ToString();               // initial minimum voltage value
            txtRocketLevelSet.Text = 0.ToString();                     // initial minimum voltage value

            lblPowerSolar.Text = "ERROR";
            lblPowerSystem.Text = "ERROR";
            lblPowerIgnition.Text = "ERROR";
            lblPowerRocket.Text = "ERROR";

            picGPIOUmbilical.Visible = false;

        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void ifKit_Initialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            lblTowerTemp.Text = "-- *F";
            lblTowerHumidity.Text = "-- %";
            lblEnclosureTemp.Text = "-- *F";
            //grpPowerSystems.Enabled = true;
            //grpAtmosphericConditions.Enabled = true;
            //grpUmbilicalPower.Enabled = true;

            picBattSolar.Image = imgListBatteryLevel.Images[0];
            picBattSystem.Image = imgListBatteryLevel.Images[0];
            picBattIgnition.Image = imgListBatteryLevel.Images[0];
            picBattRocket.Image = imgListBatteryLevel.Images[0];

            txtBattSolarLevelSet.Text = minVoltageSolar.ToString();                 // initial minimum voltage value
            txtBattSystemLevelSet.Text = minVoltageBattSystem.ToString();           // initial minimum voltage value
            txtBattIgnitionLevelSet.Text = minVoltageBattIgnition.ToString();       // initial minimum voltage value
            txtRocketLevelSet.Text = minVoltageRocket.ToString();                   // initial minimum voltage value

            lblPowerSolar.Text = "INIT";
            lblPowerSystem.Text = "INIT";
            lblPowerIgnition.Text = "INIT";
            lblPowerRocket.Text = "INIT";

            picGPIOUmbilical.Visible = true;
        }

        // ----- FUNCTION :: Handle ifKit being attached and initialized
        public void ifKit_Attach(object sender, AttachEventArgs e)
        {
            InterfaceKit ifKit = (InterfaceKit)sender;

            phidgetInterfaceFound = (ifKit.Attached) ? true : false;     // stores if phidget device found
            string msg = (phidgetInterfaceFound) ? "Phidget interface kit found" : "NO Phidget interface kit found";
            LogScreen("MSG :: " + msg);

            // ----- display various items about this IF Kit
            txtIKAttached.Text      = ifKit.Attached.ToString();
            txtIKName.Text          = ifKit.Name;
            txtIKSerial.Text        = ifKit.SerialNumber.ToString();
            txtIKVersion.Text       = ifKit.Version.ToString();
            txtIKInputDigNum.Text   = ifKit.inputs.Count.ToString();
            txtIKOutputDigNum.Text  = ifKit.outputs.Count.ToString();
            txtIKInputAnlgNum.Text  = ifKit.sensors.Count.ToString();


            // ----- configure input sensors
            int i;
            if (ifKit.sensors.Count > 0)
            {
                // set the sensor rate
                for (i = 0; i < ifKit.sensors.Count; i++)
                {
                    /*
                    if (ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_2_2_2
                        || ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_8_8_8
                        || ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_8_8_8_w_LCD)
                        ifKit.sensors[i].DataRate = sensorDataRate;  
                     */
                    
                    // ===== NEED TO SET DATA RATE =====
                    
                    //ifKit.sensors[i].DataRate = sensorDataRate.ToString();  
                }

                // enable sensor rate change slider 
                inputIKTrk.Value        = sensorDataRate;
                inputIKTrk.Visible      = true;
                inputIKTrk.Enabled      = true;
                sensitivityIKTxt.Text   = sensorDataRate.ToString();

                try
                {
                    if (ifKit.sensors.Count > 0)
                        inputIKTrk.Value        = ifKit.sensors[0].Sensitivity;
                        sensitivityIKTxt.Text   = inputIKTrk.Value.ToString();
                }
                catch { }

            }

            // ----- configure digital outputs
            //ifKit.outputs[outputIndex] = outputChk.Checked;
            if (ifKit.outputs.Count > 0)
            {
                for (i = 0; i < ifKit.outputs.Count; i++)
                {
                    ifKit.outputs[i] = false;   // initialize to off "low" state
                }

                
                cbGPIOStatus0.Checked = false;
                cbGPIOStatus1.Checked = false;
                cbGPIOStatus2.Checked = false;
                cbGPIOStatus3.Checked = false;
                cbGPIOStatus4.Checked = false;
                cbGPIOStatus5.Checked = false;
                cbGPIOStatus6.Checked = false;
                cbGPIOStatus7.Checked = false;

                //ifKit.outputs[2] = true;
            }

            // initialize form display
            ifKit_Initialize_Display();

            // initialize values in logfile
            phidgetValues["gpio-umbilical"] = 0;
        }

        // ----- FUNCTION :: Handle ifKit being detached
        public void ifKit_Detach(object sender, DetachEventArgs e)
        {
            InterfaceKit ifKit = (InterfaceKit)sender;

            // ----- clear various items about this IF Kit
            txtIKAttached.Text = ifKit.Attached.ToString();
            txtIKName.Text = "";
            txtIKSerial.Text = "";
            txtIKVersion.Text = "";
            txtIKInputDigNum.Text = "";
            txtIKOutputDigNum.Text = "";
            txtIKInputAnlgNum.Text = "";

            // ----- disable sensor rate change slider 
            label26.Visible = false;
            inputIKTrk.Value = 0;
            inputIKTrk.Visible = false;
            inputIKTrk.Enabled = false;

            
            cbGPIOStatus0.Checked = false;
            cbGPIOStatus1.Checked = false;
            cbGPIOStatus2.Checked = false;
            cbGPIOStatus3.Checked = false;
            cbGPIOStatus4.Checked = false;
            cbGPIOStatus5.Checked = false;
            cbGPIOStatus6.Checked = false;
            cbGPIOStatus7.Checked = false;


            //if ((advSensorForm != null) && (advSensorForm.IsDisposed == false))
            //    advSensorForm.Close();

            // uninitialize form display
            ifKit_Uninitialize_Display();

            // de-initialize values in logfile
            phidgetValues["gpio-umbilical"] = -1;
        }

        // ----- FUNCTION :: Error event handler
        public void ifKit_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_PACKETLOST:
                    //Ignore this error - it's not useful in this context.
                    return;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_OVERRUN:
                    //Ignore this error - it's not useful in this context.
                    return;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }





        //Digital input change event handler
        //Here we check or uncheck the corresponding input checkbox based 
        //on the index of the digital input that generated the event
        public void ifKit_InputChange(object sender, InputChangeEventArgs e)
        {
            sensorInArray[e.Index].Text = e.Value.ToString();

            string sensorInput = digitalSensorInput[e.Index];
            double curVal, minVal, maxVal;

            switch (sensorInput)
            {
                /*
                case "voltageSolar":
                    // ----- VOLTAGE FOR SOLAR PANEL -----
                    Sensor_1135 sensorVoltage1 = new Sensor_1135();

                    curVal = sensorVoltage1.calculateVoltage(e.Value);
                    minVal = (txtBattSolarLevelSet.Text != "" && isInt32(txtBattSolarLevelSet.Text)) ? double.Parse(txtBattSolarLevelSet.Text) : 0;
                    maxVal = maxVoltageSolar;

                    phidgetValues["power-solar"] = curVal;      // Store value in dictionary for logfile writting

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSolar, picBattSolar, pnlPowerSolar);
                    //lblPowerSolar.Text = lblPowerSolar.Text + curVal.ToString("0.###") + "V";
                    lblPowerSolar.Text = curVal.ToString("0.###") + "V";
                    break;
                */
                case "windSpeed":
                    curVal = 0;

                    //string tmpText = e.Value.ToString();
                    //int newCount = (tmpText == "True") ? 1 : 0;
                    //int newIncrement = 1;                               // set the increment to add to count
                    //windSensorCount += newIncrement;                    // increment wind sensor count


                    //ZsensorWindspeed.totalTick += 1;
                    ZsensorWindspeed.curTick += 1;

                    //lblTicksTotal.Text = ZsensorWindspeed.totalTick.ToString();
                    //lblTicksCur.Text = ZsensorWindspeed.curTick.ToString();

                    //lblTowerWindSpeed.Text = curVal.ToString("0.###");
                    //phidgetValues["wind-speed"] = curVal;      // Store value in dictionary for logfile writting
                    break;
            }






        }

        //Digital output change event handler
        //Here we check or uncheck the corresponding output checkbox
        //based on the index of the output that generated the event
        public void ifKit_OutputChange(object sender, OutputChangeEventArgs e)
        {
            //digiOutDispArray[e.Index].Checked = e.Value;
            //sensorInArray[e.Index].Text = e.Value.ToString();

            string gpioCase = gpioOutput[e.Index];
            switch (gpioCase)
            {
                case "gpioUmbilical":
                    
                    int GPIONum = Array.IndexOf(gpioOutput, gpioCase);                  // figure out the GPIO number based on array position
                    bool curStatus = ifKit.outputs[GPIONum];                            // get current status of this GPIO
                    double curVal = (curStatus == true) ? 1 : 0;
                    phidgetValues["gpio-umbilical"] = curVal;                           // Store value in dictionary for logfile writting

                    break;
            }
        }

        //Sensor input change event handler
        //Set the textbox content based on the input index that is communicating
        //with the interface kit
        public void ifKit_SensorChange(object sender, SensorChangeEventArgs e)
        {
            sensorInArray[e.Index].Text = e.Value.ToString();

            string sensorInput = analogSensorInput[e.Index];
            double curVal, minVal, maxVal;

            switch (sensorInput)
            {
                case "voltageSolar":
                    // ----- VOLTAGE FOR SOLAR PANEL -----
                    Sensor_1135 sensorVoltage1 = new Sensor_1135();

                    curVal = sensorVoltage1.calculateVoltage(e.Value);
                    minVal = (txtBattSolarLevelSet.Text != "" && isInt32(txtBattSolarLevelSet.Text)) ? double.Parse(txtBattSolarLevelSet.Text) : 0;
                    maxVal = maxVoltageSolar;
                    
                    phidgetValues["power-solar"] = curVal;      // Store value in dictionary for logfile writting

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSolar, picBattSolar, pnlPowerSolar);
                    //lblPowerSolar.Text = lblPowerSolar.Text + curVal.ToString("0.###") + "V";
                    lblPowerSolar.Text = curVal.ToString("0.###"); // + "V";
                    break;

                case "voltageSystem":
                    // ----- VOLTAGE FOR SYSTEM BATTERY -----
                    Sensor_1135 sensorVoltage2 = new Sensor_1135();

                    curVal = sensorVoltage2.calculateVoltage(e.Value);
                    //minVal = double.Parse(txtBattSystemLevelSet.Text);
                    minVal = (isInt32(txtBattSystemLevelSet.Text)) ? double.Parse(txtBattSystemLevelSet.Text) : 0;
                    maxVal = maxVoltageBattSystem;

                    phidgetValues["power-system"] = curVal;      // Store value in dictionary for logfile writting

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSystem, picBattSystem, pnlPowerSystem);
                    //lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
                    lblPowerSystem.Text = curVal.ToString("0.###"); // + "V";
                    break;

                case "voltageIgnition":
                    // ----- VOLTAGE FOR IGNITION BATTERY -----
                    Sensor_1135 sensorVoltage3 = new Sensor_1135();

                    curVal = sensorVoltage3.calculateVoltage(e.Value);
                    //minVal = double.Parse(txtBattIgnitionLevelSet.Text);
                    minVal = (isInt32(txtBattIgnitionLevelSet.Text)) ? double.Parse(txtBattIgnitionLevelSet.Text) : 0;
                    maxVal = maxVoltageBattIgnition;

                    phidgetValues["power-ignition"] = curVal;      // Store value in dictionary for logfile writting

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerIgnition, picBattIgnition, pnlPowerIgnition);
                    //lblPowerIgnition.Text = lblPowerIgnition.Text + curVal.ToString("0.###") + "V";
                    lblPowerIgnition.Text = curVal.ToString("0.###"); // + "V";
                    break;

                case "voltageRocket":
                    // ----- VOLTAGE FOR ROCKET UMBILICAL -----
                    Sensor_1135 sensorVoltage4 = new Sensor_1135();

                    curVal = sensorVoltage4.calculateVoltage(e.Value);
                    //minVal = double.Parse(txtRocketLevelSet.Text);
                    minVal = (isInt32(txtRocketLevelSet.Text)) ? double.Parse(txtRocketLevelSet.Text) : 0;
                    maxVal = maxVoltageRocket;

                    phidgetValues["power-rocket"] = curVal;      // Store value in dictionary for logfile writting

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerRocket, picBattRocket, pnlPowerRocket);
                    //lblPowerRocket.Text = lblPowerRocket.Text + curVal.ToString("0.###") + "V";
                    lblPowerRocket.Text = curVal.ToString("0.###"); // + "V";
                    break;

                case "temperatureEnclosure":
                    // ----- TEMPERATURE INSIDE COMPUTER ENCLOSURE -----
                    Sensor_1124 sensorTemp1 = new Sensor_1124();
                    curVal = sensorTemp1.calculateTempF(e.Value);
                    lblEnclosureTemp.Text = curVal.ToString();
                    phidgetValues["temperature-electronics"] = curVal;      // Store value in dictionary for logfile writting
                    break;

                case "temperatureTower":
                    // ----- TEMPERATURE AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp2 = new Sensor_1125();
                    curVal = sensorTemp2.calculateTempF(e.Value);
                    lblTowerTemp.Text = curVal.ToString();
                    phidgetValues["temperature-air"] = curVal;      // Store value in dictionary for logfile writting
                    break;

                case "humidityTower":
                    // ----- HUMIDITY AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp3 = new Sensor_1125();
                    curVal = sensorTemp3.calculateHumidity(e.Value);
                    lblTowerHumidity.Text = curVal.ToString();
                    phidgetValues["humidity-air"] = curVal;      // Store value in dictionary for logfile writting
                    break;



                case "windDirection":
                    curVal = 0;
                    phidgetValues["wind-direction"] = curVal;      // Store value in dictionary for logfile writting
                    break;
            }


            //if (advSensorForm != null)
            //    advSensorForm.SetValue(e.Index, e.Value);
        }






        /*
         * ====================================================================================================
         * ====================== RELAY INTERFACE KIT FUNCTIONS ===============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void relayKit_Uninitialize_Display()
        {
           //grpRelays.Enabled = false;
            grpRocketFire.Enabled = false;

            picRelayLight.Visible = false;      // hide relay toggle switches
            picRelaySiren.Visible = false;
            picRelayOther.Visible = false;
            picRelayIgnition.Visible = false;
            
            cbRelayStatus0.Checked = false; // set relay checkbox values
            cbRelayStatus1.Checked = false;
            cbRelayStatus2.Checked = false;
            cbRelayStatus3.Checked = false;
        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void relayKit_Initialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            //grpRelays.Enabled = true;
            grpRocketFire.Enabled = true;

            picRelayLight.Visible = true;       // hide relay toggle switches
            picRelaySiren.Visible = true;
            picRelayOther.Visible = true;
            picRelayIgnition.Visible = true;

            cbRelayStatus0.Checked = false; // set relay checkbox values
            cbRelayStatus1.Checked = false;
            cbRelayStatus2.Checked = false;
            cbRelayStatus3.Checked = false;
        }

        // ----- FUNCTION :: Handle relayKit being attached and initialized
        void relayKit_Attach(object sender, AttachEventArgs e)
        {
            InterfaceKit relayKit = (InterfaceKit)sender;

            // stores if phidget device found - should always be TRUE if in this function
            phidgetRelayFound = (relayKit.Attached) ? true : false;
            string msg = (phidgetRelayFound) ? "Phidget relay kit found" : "NO Phidget relay kit found";
            LogScreen("MSG :: " + msg);

            // display various items about this IF Kit
            txtRKAttached.Text = relayKit.Attached.ToString();
            txtRKName.Text = relayKit.Name;
            txtRKSerial.Text = relayKit.SerialNumber.ToString();
            txtRKVersion.Text = relayKit.Version.ToString();
            txtRKInputDigNum.Text = relayKit.inputs.Count.ToString();
            txtRKOutputDigNum.Text = relayKit.outputs.Count.ToString();

            // inititalize relay values to "off"
            for (int i = 0; i < relayKit.outputs.Count; i++)
            {
                relayKit.outputs[i] = false;
            }

            // initialize form display
            relayKit_Initialize_Display();
        }

        // ----- FUNCTION :: Handle relayKit being detached
        void relayKit_Detach(object sender, DetachEventArgs e)
        {
            InterfaceKit relayKit = (InterfaceKit)sender;

            // stores if phidget device found - should always be FALSE if in this function
            phidgetRelayFound = (relayKit.Attached) ? true : false;
            string msg = (phidgetRelayFound) ? "Phidget relay kit found" : "NO Phidget relay kit found";
            LogScreen("MSG :: " + msg);

            // clear various items about this IF Kit
            txtRKAttached.Text = relayKit.Attached.ToString();
            txtRKName.Text = "";
            txtRKSerial.Text = "";
            txtRKVersion.Text = "";
            txtRKInputDigNum.Text = "";
            txtRKOutputDigNum.Text = "";

            // inititalize relay values to "off"
            for (int i = 0; i < relayKit.outputs.Count; i++)
            {
                relayKit.outputs[i] = false;
            }

            // uninitialize form display
            relayKit_Uninitialize_Display();
        }

        // ----- FUNCTION :: Error event handler
        void relayKit_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_PACKETLOST:
                    //Ignore this error - it's not useful in this context.
                    return;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_OVERRUN:
                    //Ignore this error - it's not useful in this context.
                    return;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }

        // ----- FUNCTION :: Handle a relay output change
        void relayKit_OutputChange(object sender, OutputChangeEventArgs e)
        {
            // Note :: We are just storing the status of the relay in the logfile
            //         This could have been done on the button change - but better to store
            //         values when the Phidget actually does something - in case there is
            //         bad code in the button switch.

            string sensorInput = digitalRelayOutput[e.Index];       // get which relay has just triggered
            double curVal = (e.Value) ? 1 : 0;                      // store value of relay (true = N.O. position ???)

            switch (sensorInput)
            {
                case "relayRocketFire":
                    phidgetValues["relay-ignition"] = curVal;       // Store value in dictionary for logfile writting
                    break;
                case "relaySiren":
                    phidgetValues["relay-siren"] = curVal;          // Store value in dictionary for logfile writting
                    break;
                case "relayLight":
                    phidgetValues["relay-light"] = curVal;          // Store value in dictionary for logfile writting
                    break;
                case "relayOther":
                    phidgetValues["relay-other"] = curVal;          // Store value in dictionary for logfile writting
                    break;
            }
        }


        //Modify the digital ouputs
        //From the properties window in the form designer, each of the CheckedChanged events for output 
        //checkboxes point to this event handler. The "tag" property for each check box stores user defined 
        //data associated with the control and has been used here to relate the box with an output index.
        private void CheckedChanged(object sender, EventArgs e)
        {
            CheckBox outputChk = (CheckBox)sender;

            int outputIndex = int.Parse((string)outputChk.Tag);

            ifKit.outputs[outputIndex] = outputChk.Checked;
        }


        //This method will associate the digiOutArray with check boxes that control the state of the
        //digital outputs on the interface kit. It will also associate the digiOutDispArray with check
        //boxes that represent the state of the outputs as reported on the interfacekit, and initialize 
        //the visibility of the check boxes and labeling to false.
        private void makeDigiOutArray()
        {
            for (int i = 0; i < 16; i++)
            {
                /*
                ((Label)digitalOutputsGroupBox.Controls["digitalOutputLabel" + i.ToString()]).Visible = false;
                digiOutArray[i] = (CheckBox)digitalOutputsGroupBox.Controls["checkBox" + (i + 17).ToString()];
                digiOutArray[i].Visible = false;
                digiOutDispArray[i] = (CheckBox)digitalOutputsGroupBox.Controls["checkBoxReport" + i.ToString()];
                digiOutDispArray[i].Visible = false;
                */
            }
        }






        /*
         * ====================================================================================================
         * ====================== ENCODER FUNCTIONS ===========================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void encoder_Uninitialize_Display()
        {
            // FUNCTION :: Change any display elements tied to rotary encoder device - to show disconencted
            lblTowerWindSpeed.Text = "err";
            
            lblTowerWindDirection.Text = "err";
            lblTowerWindDirectionAngle.Text = "err";
        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void encoder_Initialize_Display()
        {
            // FUNCTION :: Initialize any display elements tied to rotary encoder device - to show connected
            lblTowerWindSpeed.Text = "0";

            lblTowerWindDirection.Text = "0";
            lblTowerWindDirectionAngle.Text = (char)176 + "N";
        }

        // ----- FUNCTION :: Handle rotary encoder being attached and initialized
        void encoder_Attach(object sender, AttachEventArgs e)
        {

            Phidgets.Encoder encoderX = (Phidgets.Encoder)sender;

            phidgetEncoderFound = (encoder.Attached) ? true : false;     // stores if phidget device found
            string msg = (phidgetEncoderFound) ? "Phidget rotary encoder found" : "NO Phidget rotary encoder found";
            LogScreen("MSG :: " + msg);

            // ----- display various items about this IF Kit
            txtENCAttached.Text     = encoderX.Attached.ToString();
            txtENCName.Text         = encoderX.Name;
            txtENCSerial.Text       = encoderX.SerialNumber.ToString();
            txtENCVersion.Text      = encoderX.Version.ToString();

            switch (encoderX.ID)
            {
                case Phidget.PhidgetID.ENCODER_HS_4ENCODER:                    
                    lblENCTimeChange.Text = "Time since last change (μs):";
                    break;
                case Phidget.PhidgetID.ENCODER_HS_1ENCODER:
                case Phidget.PhidgetID.ENCODER_1ENCODER_1INPUT:
                    lblENCTimeChange.Text = "Time since last change (ms):";
                    
                    break;
                default:
                    break;
            }

            // initialize form display
            encoder_Initialize_Display();
        }

        // ----- FUNCTION :: Handle rotary encoder being detached
        void encoder_Detach(object sender, DetachEventArgs e)
        {
            Phidgets.Encoder encoderX = (Phidgets.Encoder)sender;

            // display various items about this IF Kit
            txtENCAttached.Text             = encoderX.Attached.ToString();
            txtENCName.Text                 = "";
            txtENCSerial.Text               = "";
            txtENCVersion.Text              = "";
            txtENCTimeSinceLastChange.Text  = "";
            txtENCPosition.Text             = "";

            // uninitialize form display
            encoder_Uninitialize_Display();
        }

        // ----- FUNCTION :: Error event handler
        void encoder_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }

        // ----- FUNCTION :: Handle input change (pushbutton in the knob)
        void encoder_InputChange(object sender, InputChangeEventArgs e)
        {
            // Event arguements contain the input index (on current Phidget Encoders will only be 1) and the value, 
            // a bool to represent clicked or unlcicked state
            
            //((CheckBox)inputArray[e.Index]).Checked = e.Value;

            encoderZeroPosition = encoder.encoders[e.Index];        // get the encoder's value
            lblTowerWindDirection.Text = "0";                       // update angle to 0*
            lblTowerWindDirectionAngle.Text = (char)176 + "N";      // update angle ordinal text
            //pbArrowFinal.Image = RotateImage(pbArrow.Image, -90);   // update arrow graphic
        }

        // ----- FUNCTION :: Handle encoder position change (rotation of knob)
        void encoder_PositionChange(object sender, EncoderPositionChangeEventArgs e)
        {
            //Encoder Position Change event handler...the event arguements will provide the encoder index, value, and 
            //the elapsed time since the last event.  These value, including the current position value stored in the
            //corresponding element in the encoder objects encoder collection could be used to calculate velocity...
            
            int index = 0; // (int)encoderCmb.SelectedItem;
            if (index == e.Index)
            {
                // Note :: Equation is accurate to only 4* because of encoder - possibly 5* with rounding error
                
                string directionCircle = "";                            // will hold ordinal direction
                float angleCircle = -1;                                 // will hold actual caridinal angle
                float angleCircleZero = -1;                             // will hold actual caridinal angle of zero-point offset
                float rotaryCountTotal = 80;                            // how many ticks per complete revolution
                float curPosition = encoder.encoders[e.Index];          // get the encoder's value
                float conversionToAngle = (360 / rotaryCountTotal);     // calculate factor for converting normalize value


                // ----- figure the position in a single 360* loop - convert to positive integer (normalize)
                curPosition = encoderNormalize(curPosition, rotaryCountTotal);                  // normalize the curent position
                encoderZeroPosition = encoderNormalize(encoderZeroPosition, rotaryCountTotal);  // normalize the zero-point position
                
                // ----- calculate final angle with zero-point offset
                curPosition = curPosition + (80 - encoderZeroPosition);


                // ----- figure the position in a single 360* loop - convert to positive integer (re-normalize)
                curPosition = encoderNormalize(curPosition, rotaryCountTotal);                  // normalize the adjusted curent position 
                

                // ----- convert normalized encoder value to angle in circle
                angleCircle = ((rotaryCountTotal - curPosition) * conversionToAngle);   // convert to angle
                angleCircle = (float)Math.Round(angleCircle, 0);                        // round up to nearest whole degree


                // ----- calculate the cardinal and ordinal direction
                directionCircle = (char)176 + "";
                directionCircle = (angleCircle > 337.5 || angleCircle < 22.5) ? (char)176 + "N" : directionCircle;
                directionCircle = (angleCircle > 22.5 && angleCircle < 67.5) ? (char)176 + "NE" : directionCircle;
                directionCircle = (angleCircle > 67.5 && angleCircle < 112.5) ? (char)176 + "E" : directionCircle;
                directionCircle = (angleCircle > 112.5 && angleCircle < 157.5) ? (char)176 + "SE" : directionCircle;
                directionCircle = (angleCircle > 157.5 && angleCircle < 202.5) ? (char)176 + "S" : directionCircle;
                directionCircle = (angleCircle > 202.5 && angleCircle < 247.5) ? (char)176 + "SW" : directionCircle;
                directionCircle = (angleCircle > 247.5 && angleCircle < 292.5) ? (char)176 + "W" : directionCircle;
                directionCircle = (angleCircle > 292.5 && angleCircle < 337.5) ? (char)176 + "NW" : directionCircle;
                

                // ----- output screen values
                //txtENCPosition.Text = e.PositionChange.ToString();
                txtENCPosition.Text = encoder.encoders[e.Index].ToString();
                lblTowerWindDirection.Text = angleCircle.ToString();
                lblTowerWindDirectionAngle.Text = directionCircle;
                //lblTowerWindDirectionAngle.Text = directionCircle + ":" + curPosition.ToString() + ":" + encoderZeroPosition.ToString();


                // ----- rotate arrow on compass
                //pbArrowFinal.Image = RotateImage(pbArrow.Image, angleCircle-90);
                //pbArrowFinal.SizeMode = PictureBoxSizeMode.CenterImage;


                /* --------------------------------------------------------------------------------
                
                try
                {
                    txtENCTimeSinceLastChange.Text = e.Time.ToString();
                }
                catch
                {
                    txtENCTimeSinceLastChange.Text = "Unknown";
                }
                 
                // Velocity calculated in counts per second - averaged over 50 samples
                double veloc = 0;
                try
                {
                    switch (encoder.ID)
                    {
                        case Phidget.PhidgetID.ENCODER_1ENCODER_1INPUT:
                        case Phidget.PhidgetID.ENCODER_HS_1ENCODER:
                            veloc = (((double)e.PositionChange * 1000) / ((double)e.Time));
                            break;
                        case Phidget.PhidgetID.ENCODER_HS_4ENCODER:
                            veloc = (((double)e.PositionChange * 1000000) / ((double)e.Time));
                            break;
                    }
                }
                catch
                { }
                -------------------------------------------------------------------------------- */

            }
        }

        private float encoderNormalize(float value, float rotaryCountTotal)
        {
            // FUNCTION :: Convert a value from an encoder to a single encoder loop value (normalize)

            while (value < 0)
            {
                value += rotaryCountTotal;        // don't let number go negative
            }

            while (value > rotaryCountTotal)
            {
                value -= rotaryCountTotal;        // don't let number go above one encoder loop
            }

            return value;
        }




        /*
         * ====================================================================================================
         * ====================== PARSE COMMAND LINE ARGUMENT FUNCTIONS =======================================
         * ====================================================================================================
        */
        
        #region Command line open functions
        private void openCmdLine(Phidget p)
        {
            openCmdLine(p, null);
        }
        private void openCmdLine(Phidget p, String pass)
        {
            int serial = -1;
            int port = phidgetServerPortNumber;
            String host = null;
            bool remote = false, remoteIP = false;
            string[] args = Environment.GetCommandLineArgs();
            String appName = args[0];

            try
            { //Parse the flags
                for (int i = 1; i < args.Length; i++)
                {
                    if (args[i].StartsWith("-"))
                        switch (args[i].Remove(0, 1).ToLower())
                        {
                            case "n":
                                serial = int.Parse(args[++i]);
                                break;
                            case "r":
                                remote = true;
                                break;
                            case "s":
                                remote = true;
                                host = args[++i];
                                break;
                            case "p":
                                pass = args[++i];
                                break;
                            case "i":
                                remoteIP = true;
                                host = args[++i];
                                if (host.Contains(":"))
                                {
                                    port = int.Parse(host.Split(':')[1]);
                                    host = host.Split(':')[0];
                                }
                                break;
                            default:
                                goto usage;
                        }
                    else
                        goto usage;
                }

                if (remoteIP)
                    p.open(serial, host, port, pass);
                else if (remote)
                    p.open(serial, host, pass);
                else
                    p.open(serial);
                return; //success
            }
            catch { }
        usage:
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("Invalid Command line arguments." + Environment.NewLine);
            sb.AppendLine("Usage: " + appName + " [Flags...]");
            sb.AppendLine("Flags:\t-n   serialNumber\tSerial Number, omit for any serial");
            sb.AppendLine("\t-r\t\tOpen remotely");
            sb.AppendLine("\t-s   serverID\tServer ID, omit for any server");
            sb.AppendLine("\t-i   ipAddress:port\tIp Address and Port. Port is optional, defaults to 5001");
            sb.AppendLine("\t-p   password\tPassword, omit for no password" + Environment.NewLine);
            sb.AppendLine("Examples: ");
            sb.AppendLine(appName + " -n 50098");
            sb.AppendLine(appName + " -r");
            sb.AppendLine(appName + " -s myphidgetserver");
            sb.AppendLine(appName + " -n 45670 -i 127.0.0.1:5001 -p paswrd");
            MessageBox.Show(sb.ToString(), "Argument Error", MessageBoxButtons.OK, MessageBoxIcon.Error);

            Application.Exit();
        }
        #endregion

        




        /*
         * ====================================================================================================
         * ====================== CUSTOM FUNCTIONS ============================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Write message to the on-screen log textbox
        public void LogScreen(string MSG)
        {
            if (MSG != "" && txtLogToScreen != null)
            {
                // create the log message string
                string message = MSG;
                string newline = (txtLogToScreen.Text != "") ? Environment.NewLine : "";        // figure out newline character
                
                // output log message to the program screen
                txtLogToScreen.Text += newline + message;                                       // put message in textbox
                txtLogToScreen.SelectionStart = txtLogToScreen.Text.Length;                     // get length of box
                txtLogToScreen.ScrollToCaret();                                                 // scroll to bottom of textbox
                
                // output log message to the program file (crash analysis)
                TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
                bool result = ZtxtObj.appendFile(outputFileStatus, message);                    // open and write the file
            }
        }

        // ----- FUNCTION :: Determine if string is actually an integer
        private bool isInt32(string checkString)
        {
            // check if string passed in is actually an integer
            int checkVal;

            checkString = Regex.Replace(checkString, @"\t|\n|\r| ", "");    // remove whitespace and tabs from string

            if (checkString == "")
            {
                return false;
            }

            try
            {
                checkVal = Convert.ToInt32(checkString);
                if (checkVal < 0)
                {
                    return false;
                }
                return true;
            }
            catch (FormatException e)
            {
                return false;
            }
            catch (OverflowException e)
            {
                return false;
            }
        }

        




        /*
         * ====================================================================================================
         * ====================== PHIDGET INITIALIZATION FUNCTIONS ============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Initialize phidget encoder device and attach events
        private void InitializePhidgetEncoder()
        {
            // ----- INITIALIZE THE ROTARY ENCODER -----
            if (phidgetEncoderFound)
            {
                MessageBox.Show("ERROR :: Phidget encoder already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget encoder already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget rotary encoder");

                    // initialize the encoder
                    encoder = new Phidgets.Encoder();
                    encoder.open(serialNumEncoder1);

                    // attach events to the encoder
                    encoder.Attach += new AttachEventHandler(encoder_Attach);   // Set the attach handler
                    encoder.Detach += new DetachEventHandler(encoder_Detach);   // Set the detach handler
                    encoder.Error += new ErrorEventHandler(encoder_Error);      // Set the error handler
                    encoder.InputChange += new InputChangeEventHandler(encoder_InputChange);                    // Set the input change handler
                    encoder.PositionChange += new EncoderPositionChangeEventHandler(encoder_PositionChange);    // Set the position change handler

                    openCmdLine(encoder);                       // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString()); // throw phidget errors
                }
            }
        }

        // ----- FUNCTION :: Initialize phidget interface device and attach events
        private void InitializePhidgetInterface()
        {
            // ----- INITIALIZE THE INTERFACE KIT -----
            if (phidgetInterfaceFound)
            {
                MessageBox.Show("ERROR :: Phidget interface already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget interface already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget interface kit");

                    // initialize the ifKit
                    ifKit = new InterfaceKit();
                    ifKit.open(serialNuminterface1, phidgetServerIpAddress, phidgetServerPortNumber, phidgetServerPassword);

                    // attach events to the ifKit
                    ifKit.Attach += new AttachEventHandler(ifKit_Attach);
                    ifKit.Detach += new DetachEventHandler(ifKit_Detach);
                    ifKit.Error += new ErrorEventHandler(ifKit_Error);
                    ifKit.InputChange += new InputChangeEventHandler(ifKit_InputChange);
                    ifKit.OutputChange += new OutputChangeEventHandler(ifKit_OutputChange);
                    ifKit.SensorChange += new SensorChangeEventHandler(ifKit_SensorChange);

                    openCmdLine(ifKit);                         // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString()); // throw phidget errors
                }
            }
        }

        // ----- FUNCTION :: Initialize phidget relay device and attach events
        private void InitializePhidgetRelay()
        {
            // ----- INITIALIZE THE RELAY INTERFACE KIT -----
            if (phidgetRelayFound)
            {
                MessageBox.Show("ERROR :: Phidget relay already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget relay already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget relay");

                    // initialize the relayKit
                    relayKit = new InterfaceKit();
                    //relayKit = new RelayKit();
                    relayKit.open(serialNumRelay1, phidgetServerIpAddress, phidgetServerPortNumber, phidgetServerPassword);

                    // attach events to the relayKit
                    relayKit.Attach += new AttachEventHandler(relayKit_Attach);
                    relayKit.Detach += new DetachEventHandler(relayKit_Detach);
                    relayKit.Error += new ErrorEventHandler(relayKit_Error);
                    //relayKit.InputChange += new InputChangeEventHandler(relayKit_InputChange);
                    relayKit.OutputChange += new OutputChangeEventHandler(relayKit_OutputChange);
                    //relayKit.SensorChange += new SensorChangeEventHandler(relayKit_SensorChange);

                    openCmdLine(relayKit);                      // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString());
                }
            }
        }

        




        /*
         * ====================================================================================================
         * ====================== HOLDING FUNCTIONS OUT OF THE WAY ============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Handle form elements when connected to the network
        private void NetworkDisplayConnected()
        {
            btnConnectPhidgets.Enabled = false;
            btnConnectPhidgets.Visible = false;

            btnDisconnectPhidgets.Enabled = true;
            btnDisconnectPhidgets.Visible = true;

            txtIPAddress.Enabled = false;
            txtPortAddress.Enabled = false;
            txtServerPassword.Enabled = false;

            this.BackColor = Color.FromName("YellowGreen"); //Control
            //tabControl1.
            LogScreen("Network connection established.");
        }

        // ----- FUNCTION :: Handle form elements when disconnected from the network
        private void NetworkDisplayDisconnected()
        {
            btnConnectPhidgets.Enabled = true;
            btnConnectPhidgets.Visible = true;

            btnDisconnectPhidgets.Enabled = false;
            btnDisconnectPhidgets.Visible = false;

            txtIPAddress.Enabled = true;
            txtPortAddress.Enabled = true;
            txtServerPassword.Enabled = true;

            this.BackColor = Color.FromName("DarkRed");
            LogScreen("Network connection disconnected.");
        }

        // ----- FUNCTION :: Disconnect from all phidget devices
        private void PhidgetsDisconnect()
        {
            // ----- Unhook the event handlers for encoder
            if (encoder != null)
            {
                LogScreen("Disconnecting Phidget rotary encoder.");
                encoder.Attach -= new AttachEventHandler(encoder_Attach);
                encoder.Detach -= new DetachEventHandler(encoder_Detach);
                encoder.Error -= new ErrorEventHandler(encoder_Error);
                encoder.PositionChange -= new EncoderPositionChangeEventHandler(encoder_PositionChange);
                encoder.InputChange -= new InputChangeEventHandler(encoder_InputChange);

                encoder.close();
                encoder = null;
            }

            // ----- Unhook the event handlers for interface kit
            if (ifKit != null)
            {
                LogScreen("Disconnecting Phidget interface kit.");
                ifKit.Attach -= new AttachEventHandler(ifKit_Attach);
                ifKit.Detach -= new DetachEventHandler(ifKit_Detach);
                ifKit.InputChange -= new InputChangeEventHandler(ifKit_InputChange);
                ifKit.OutputChange -= new OutputChangeEventHandler(ifKit_OutputChange);
                ifKit.SensorChange -= new SensorChangeEventHandler(ifKit_SensorChange);
                ifKit.Error -= new ErrorEventHandler(ifKit_Error);

                ifKit.close();
                ifKit = null;
            }

            // ----- Unhook the event handlers for relay interface kit
            if (relayKit != null)
            {
                LogScreen("Disconnecting Phidget relay kit.");
                relayKit.Attach -= new AttachEventHandler(relayKit_Attach);
                relayKit.Detach -= new DetachEventHandler(relayKit_Detach);
                //relayKit.InputChange -= new InputChangeEventHandler(relayKit_InputChange);
                relayKit.OutputChange -= new OutputChangeEventHandler(relayKit_OutputChange);
                //relayKit.SensorChange -= new SensorChangeEventHandler(relayKit_SensorChange);
                relayKit.Error -= new ErrorEventHandler(relayKit_Error);

                relayKit.close();
                relayKit = null;
            }

            LogScreen("Phidget disconnect complete.");
        }

        // ----- FUNCTION :: Change the form dispaly for a changing voltage
        private void voltageModifyForm(double curVal, double minVal, double maxVal, Label frmLabel, PictureBox frmPicture, Panel frmPanel)
        {
            //string colorBattOn = "DarkGreen";
            //string colorBattLow = "DarkOrange";
            //string colorBattOff = "DarkRed";

            string colorBattOn = "DarkSlateGray";
            string colorBattLow = "SaddleBrown";
            string colorBattOff = "DarkRed";

            string tmpPanelColor, tmpText;
            int tmpImageIndex;

            if (curVal > minVal && curVal <= maxVal)
            {
                // - good battery level -
                tmpPanelColor = colorBattOn;
                tmpText = "Curr: ";
                tmpImageIndex = 2;
            }
            else if (curVal <= minVal && curVal > 0)
            {
                // - low battery level -
                tmpPanelColor = colorBattLow;
                tmpText = "Low: ";
                tmpImageIndex = 1;
            }
            else
            {
                // - error -
                tmpPanelColor = colorBattOff;
                tmpText = "ERROR: 0V";
                tmpImageIndex = 0;
            }

            //frmLabel.Text = tmpText;
            //frmLabel.ForeColor = Color.FromName(tmpColor);

            frmPanel.BackColor = Color.FromName(tmpPanelColor);

            frmPicture.Image = imgListBatteryLevel.Images[tmpImageIndex];
            frmPicture.Height = 130;
            frmPicture.Width = 130;

        }


        public void initializeLogfile()
        {
            // create the filename based on current time
            string filenamePath = "c:\\";
            string filenamePre = "logfile";
            string filenameExt = ".txt";
            string datetime = string.Format("{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            outputFileSensor = filenamePath + filenamePre + "_" + datetime + filenameExt;

            // create the logfile
            string output = "timestamp, temp, humidity, wind direction, wind speed, temp electronics, pwr-solar, pwr-system, pwr-ignition, pwr-rocket, gpio-umbilical, relay-ignition, relay-light, relay-siren, relay-other";
            TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
            bool result = ZtxtObj.appendFile(outputFileSensor, output);                     // open and write the file
        }


        public void initializePhidgetValueDictionary()
        {
            // FUNCTION :: initialize the dictionaty holding phidget log values
            phidgetValues.Add("temperature-air", -1);
            phidgetValues.Add("humidity-air", -1);
            phidgetValues.Add("wind-direction", -1);
            phidgetValues.Add("wind-speed", -1);
            phidgetValues.Add("temperature-electronics", -1);
            phidgetValues.Add("power-solar", -1);
            phidgetValues.Add("power-system", -1);
            phidgetValues.Add("power-ignition", -1);
            phidgetValues.Add("power-rocket", -1);
            phidgetValues.Add("gpio-umbilical", -1);
            phidgetValues.Add("relay-ignition", -1);
            phidgetValues.Add("relay-light", -1);
            phidgetValues.Add("relay-siren", -1);
            phidgetValues.Add("relay-other", -1);
        }

        public void timerLogfileInitialize()
        {
            // FUNCTION :: initialize the logfile timer

            tmrLogfile.Interval = 1000;     // time interval in milliseconds
            tmrLogfile.Enabled = true;      // enable the timer
        }

        private void tmrLogfile_Tick(object sender, EventArgs e)
        {
            // FUNCTION :: timer has incremented - write log

            string output = "";
            double value = 0;
            string datetime = string.Format("{0:yyyy-MM-dd_hh-mm-ss-tt}",DateTime.Now);

            /*
            DATETIME FORMATTING
            y (year), M (month), d (day), h (hour 12), H (hour 24), m (minute), s (second), f (second fraction), F (second fraction, trailing zeroes are trimmed), t (P.M or A.M) and z (time zone).
            */

            /*
            LOGFILE LINE
            timestamp, temp, humidity, wind direction, wind speed, temp electronics, pwr-solar, pwr-system, pwr-ignition, pwr-rocket, gpio-umbilical, relay-ignition, relay-light, relay-siren, relay-other
            */


            // create the logfile line for output
            output += datetime;
            output += (phidgetValues.TryGetValue("temperature-air", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("humidity-air", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("wind-direction", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("wind-speed", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("temperature-electronics", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-solar", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-system", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-ignition", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-rocket", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("gpio-umbilical", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-ignition", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-light", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-siren", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-other", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;

            // output log message to the program file (crash analysis)
            TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
            bool result = ZtxtObj.appendFile(outputFileSensor, output);                     // open and write the file

        }

        
        
        
        
        
        public int topPosition = 0;

        private void tmrFakeBattData_Tick(object sender, EventArgs e)
        {
            /*
            //lblBattFake1
            //lblBattFake1Volts
            int boxTop = pnlBattFake1Box.Location.Y;    // top of box    
            int boxH = pnlBattFake1Box.Height;          // height of box
            int boxBot = boxTop + boxH;                 // bottom of box


            int minVoltage = 0;
            int maxVoltage = 25;

            int incrementHeight = boxH / (maxVoltage - minVoltage);     // how many pixels tall is each 1v increment


            Random random = new Random();
            int voltage = random.Next(minVoltage, maxVoltage);

            

            int lblVMiddle = lblBattFake1.Height / 2;
            //lblBattFake1.Top;


            lblBattFake1.Text = voltage.ToString();
            lblBattFake1.Top = boxBot - (voltage * incrementHeight);


            
            //System.Drawing.Pen myPen = new System.Drawing.Pen(System.Drawing.Color.Red);
            //System.Drawing.SolidBrush myBrush = new System.Drawing.SolidBrush(System.Drawing.Color.Black);

            //System.Drawing.Graphics formGraphics = this.panel9.CreateGraphics();


            //formGraphics.DrawRectangle(myPen, new Rectangle(topPosition, topPosition, 200, 300));
            //formGraphics.DrawLine(myPen, topPosition, topPosition, 200, 200);

            pnlPowerSolar.Refresh();

            int t1 = topPosition + 10;

            //formGraphics.FillRectangle(myBrush, new Rectangle(t1, t1, 180, 280));


            topPosition += 10;
            
            //myPen.Dispose();
            //myBrush.Dispose();
            //formGraphics.Dispose();
            */
        }

        int graphX = 0;
        private void tmrFakeWindData_Tick(object sender, EventArgs e)
        {
            // FUNCTION :: Fake data pulses for wind speed
            /*
            Random random = new Random();
            int maxTick = random.Next(3, 15);
            int fakeTick = random.Next(0, maxTick);
            
            //ZsensorWindspeed.totalTick += fakeTick;
            ZsensorWindspeed.curTick += fakeTick;

            
            // UPDATE THE CHART WITH DATA
            graphX++;
            int graphY = fakeTick;
            chart1.Series["Series1"].Points.AddXY(graphX, graphY);
            chart1.Series["Series1"].ChartType = SeriesChartType.Spline;


            if (chart1.Series.IndexOf("Series2") != -1)
            {
                // Series Exists
            }
            else
            {
                // Series Does Not Exist
                chart1.Series.Add("Series2");
                chart1.Series["Series2"].ChartType = SeriesChartType.Spline;
                chart1.Series["Series2"].BorderWidth = 3;
                chart1.Series["Series2"].Color = Color.Red;

                chart1.BorderlineColor = Color.Red;
                chart1.BorderlineWidth = 5;
                chart1.ForeColor = Color.OrangeRed;
                //chart1.Padding = "5";
            }


            graphY -= 10;
            chart1.Series["Series2"].Points.AddXY(graphX, graphY);


            var series = chart1.Series.FindByName("Series1");
            //series.ChartType = SeriesChartType.Line;
            //series.XValueType = ChartValueType.Int32;

            // set view range to [0,max]
            var chartArea = chart1.ChartAreas[series.ChartArea];
            chartArea.AxisX.Minimum = 0;
            chartArea.AxisX.Maximum = graphX;
            
            */





            //chart1.Series["test1"].Color = Color.Red;

            /*
            Random rdn = new Random();
            for (int i = 0; i < 50; i++)
            {
                chart1.Series["test1"].Points.AddXY(rdn.Next(0, 10), rdn.Next(0, 10));
                chart1.Series["test2"].Points.AddXY(rdn.Next(0, 10), rdn.Next(0, 10));
            }

            chart1.Series["test1"].ChartType =SeriesChartType.FastLine;
            chart1.Series["test1"].Color = Color.Red;

            chart1.Series["test2"].ChartType =SeriesChartType.FastLine;
            chart1.Series["test2"].Color = Color.Blue; 
            */


            //lblTicksTotal.Text = ZsensorWindspeed.totalTick.ToString();
            //lblTicksCur.Text = ZsensorWindspeed.curTick.ToString();

        }





        /// <summary>
        /// method to rotate an image either clockwise or counter-clockwise
        /// </summary>
        /// <param name="img">the image to be rotated</param>
        /// <param name="rotationAngle">the angle (in degrees).
        /// NOTE: 
        /// Positive values will rotate clockwise
        /// negative values will rotate counter-clockwise
        /// </param>
        /// <returns></returns>
        public static Image RotateImage(Image img, float rotationAngle)
        {
            //create an empty Bitmap image
            Bitmap bmp = new Bitmap(img.Width, img.Height);

            //turn the Bitmap into a Graphics object
            Graphics gfx = Graphics.FromImage(bmp);

            //now we set the rotation point to the center of our image
            gfx.TranslateTransform((float)bmp.Width / 2, (float)bmp.Height / 2);

            //now rotate the image
            gfx.RotateTransform(rotationAngle);

            gfx.TranslateTransform(-(float)bmp.Width / 2, -(float)bmp.Height / 2);

            //set the InterpolationMode to HighQualityBicubic so to ensure a high
            //quality image once it is transformed to the specified size
            //gfx.InterpolationMode = InterpolationMode.HighQualityBicubic;

            //now draw our new image onto the graphics object
            int x = (int)((236 - bmp.Width) / 2);
            int y = (int)((236 - bmp.Height) / 2);
            //gfx.DrawImage(img, new Point(x, y));

            //img.Size.Width = 50;
            //img.Size.Height = 50;

            gfx.DrawImage(img, new Point(-20, -20));
            
            //dispose of our Graphics object
            gfx.Dispose();

            //return the image
            return bmp;
        }


        private float curAngle = 0;

        private void tmrRotateArrow_Tick(object sender, EventArgs e)
        {
            //Random random = new Random();
            //float angle = random.Next(0, 361);

            curAngle += 10;
            //pbArrowFinal.Image = RotateImage(pbArrow.Image, curAngle);
            //pbArrowFinal.SizeMode = PictureBoxSizeMode.CenterImage;
        }

        private void lblResetNorth_Click(object sender, EventArgs e)
        {
            encoderZeroPosition = encoder.encoders[0];              // get and store the encoder's value
            lblTowerWindDirection.Text = "0";                       // update angle to 0*
            lblTowerWindDirectionAngle.Text = (char)176 + "N";      // update angle ordinal text
            //pbArrowFinal.Image = RotateImage(pbArrow.Image, -90);   // update arrow graphic
        }

        private void btnDevEnableRotaryEncoder_Click(object sender, EventArgs e)
        {
            InitializePhidgetEncoder();     // INITIALIZE THE ROTARY ENCODER
        }


        private void txtBattSystemLevelSet_TextChanged(object sender, EventArgs e)
        {
            // FUNCTION :: Update battery display when alert voltage is set
            // Note :: Have to do it here because a steady voltage won't trigger an update the normal way
            //         The steady voltage doesn't trigget ifKit function call so it doesn't check if
            //         voltage is now above or below alert.

            double tValue = 0;
            double curVal = (phidgetValues.TryGetValue("power-system", out tValue)) ? tValue : 0;

            double minVal = (isInt32(txtBattSystemLevelSet.Text)) ? double.Parse(txtBattSystemLevelSet.Text) : 0;
            double maxVal = maxVoltageBattSystem;

            voltageModifyForm(curVal, minVal, maxVal, lblPowerSystem, picBattSystem, pnlPowerSystem);
            //lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
            lblPowerSystem.Text = curVal.ToString("0.###"); // + "V";
        }
        
        private void txtRocketLevelSet_TextChanged(object sender, EventArgs e)
        {
            // FUNCTION :: Update battery display when alert voltage is set
            // Note :: Have to do it here because a steady voltage won't trigger an update the normal way
            //         The steady voltage doesn't trigget ifKit function call so it doesn't check if
            //         voltage is now above or below alert.

            double tValue = 0;
            double curVal = (phidgetValues.TryGetValue("power-rocket", out tValue)) ? tValue : 0;

            double minVal = (isInt32(txtRocketLevelSet.Text)) ? double.Parse(txtRocketLevelSet.Text) : 0;
            double maxVal = maxVoltageRocket;

            voltageModifyForm(curVal, minVal, maxVal, lblPowerRocket, picBattRocket, pnlPowerRocket);
            //lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
            lblPowerRocket.Text = curVal.ToString("0.###"); // + "V";
        }

        private void txtBattIgnitionLevelSet_TextChanged(object sender, EventArgs e)
        {
            // FUNCTION :: Update battery display when alert voltage is set
            // Note :: Have to do it here because a steady voltage won't trigger an update the normal way
            //         The steady voltage doesn't trigget ifKit function call so it doesn't check if
            //         voltage is now above or below alert.

            double tValue = 0;
            double curVal = (phidgetValues.TryGetValue("power-ignition", out tValue)) ? tValue : 0;

            double minVal = (isInt32(txtBattIgnitionLevelSet.Text)) ? double.Parse(txtBattIgnitionLevelSet.Text) : 0;
            double maxVal = maxVoltageBattIgnition;

            voltageModifyForm(curVal, minVal, maxVal, lblPowerIgnition, picBattIgnition, pnlPowerIgnition);
            //lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
            lblPowerIgnition.Text = curVal.ToString("0.###"); // + "V";
        }

        private void txtBattSolarLevelSet_TextChanged(object sender, EventArgs e)
        {
            // FUNCTION :: Update battery display when alert voltage is set
            // Note :: Have to do it here because a steady voltage won't trigger an update the normal way
            //         The steady voltage doesn't trigget ifKit function call so it doesn't check if
            //         voltage is now above or below alert.

            double tValue = 0;
            double curVal = (phidgetValues.TryGetValue("power-solar", out tValue)) ? tValue : 0;

            double minVal = (isInt32(txtBattSolarLevelSet.Text)) ? double.Parse(txtBattSolarLevelSet.Text) : 0;
            double maxVal = maxVoltageSolar;

            voltageModifyForm(curVal, minVal, maxVal, lblPowerSolar, picBattSolar, pnlPowerSolar);
            //lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
            lblPowerSolar.Text = curVal.ToString("0.###"); // + "V";
        }







    } //end class
} //end namespace
























// =================== FUNCTINS FOR GRAPHING ===================
/*
private void RefreshGraph()
{
    display.Refresh();
}

protected void CalcSinusFunction_0(DataSource src, int idx)
{
    for (int i = 0; i < src.Length; i++)
    {
        src.Samples[i].x = i;
        src.Samples[i].y = (float)(((float)200 * Math.Sin((idx + 1) * (i + 1.0) * 48 / src.Length)));
    }
}

protected void CalcSinusFunction_1(DataSource src, int idx)
{
    for (int i = 0; i < src.Length; i++)
    {
        src.Samples[i].x = i;

        src.Samples[i].y = (float)(((float)20 *
                                    Math.Sin(20 * (idx + 1) * (i + 1) * 3.141592 / src.Length)) *
                                    Math.Sin(40 * (idx + 1) * (i + 1) * 3.141592 / src.Length)) +
                                    (float)(((float)200 *
                                    Math.Sin(200 * (idx + 1) * (i + 1) * 3.141592 / src.Length)));
    }
    src.OnRenderYAxisLabel = RenderYLabel;
}

protected void CalcSinusFunction_2(DataSource src, int idx)
{
    for (int i = 0; i < src.Length; i++)
    {
        src.Samples[i].x = i;

        src.Samples[i].y = (float)(((float)20 *
                                    Math.Sin(40 * (idx + 1) * (i + 1) * 3.141592 / src.Length)) *
                                    Math.Sin(160 * (idx + 1) * (i + 1) * 3.141592 / src.Length)) +
                                    (float)(((float)200 *
                                    Math.Sin(4 * (idx + 1) * (i + 1) * 3.141592 / src.Length)));
    }
    src.OnRenderYAxisLabel = RenderYLabel;
}

protected void CalcSinusFunction_3(DataSource ds, int idx, float time)
{
    cPoint[] src = ds.Samples;
    for (int i = 0; i < src.Length; i++)
    {
        src[i].x = i;
        src[i].y = 200 + (float)((200 * Math.Sin((idx + 1) * (time + i * 100) / 8000.0))) +
                        +(float)((40 * Math.Sin((idx + 1) * (time + i * 200) / 2000.0)));
    }

}


private void ApplyColorSchema()
{
    switch (CurColorSchema)
    {
                
        case "WHITE":
            {
                Color[] cols = { Color.DarkRed, 
                                 Color.DarkSlateGray,
                                 Color.DarkCyan, 
                                 Color.DarkGreen, 
                                 Color.DarkBlue ,
                                 Color.DarkMagenta,                              
                                 Color.DeepPink };

                for (int j = 0; j < NumGraphs; j++)
                {
                    display.DataSources[j].GraphColor = cols[j % 7];
                }

                display.BackgroundColorTop = Color.White;
                display.BackgroundColorBot = Color.White;
                display.SolidGridColor = Color.LightGray;
                display.DashedGridColor = Color.LightGray;
            }
            break;

        case "GRAY":
            {
                Color[] cols = { Color.DarkRed, 
                                 Color.DarkSlateGray,
                                 Color.DarkCyan, 
                                 Color.DarkGreen, 
                                 Color.DarkBlue ,
                                 Color.DarkMagenta,                              
                                 Color.DeepPink };

                for (int j = 0; j < NumGraphs; j++)
                {
                    display.DataSources[j].GraphColor = cols[j % 7];
                }

                display.BackgroundColorTop = Color.White;
                display.BackgroundColorBot = Color.LightGray;
                display.SolidGridColor = Color.LightGray;
                display.DashedGridColor = Color.LightGray;
            }
            break;

    }

}

protected void CalcDataGraphs()
{

    this.SuspendLayout();

    display.DataSources.Clear();
    display.SetDisplayRangeX(0, 400);

    for (int j = 0; j < NumGraphs; j++)
    {
        display.DataSources.Add(new DataSource());
        display.DataSources[j].Name = "Graph " + (j + 1);
        display.DataSources[j].OnRenderXAxisLabel += RenderXLabel;

        switch (CurExample)
        {
            case "NORMAL":
                this.Text = "Normal Graph";
                display.DataSources[j].Length = 5800;
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.NORMAL;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].SetDisplayRangeY(-300, 300);
                display.DataSources[j].SetGridDistanceY(100);
                display.DataSources[j].OnRenderYAxisLabel = RenderYLabel;
                CalcSinusFunction_0(display.DataSources[j], j);
                break;

            case "NORMAL_AUTO":
                this.Text = "Normal Graph Autoscaled";
                display.DataSources[j].Length = 5800;
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.NORMAL;
                display.DataSources[j].AutoScaleY = true;
                display.DataSources[j].SetDisplayRangeY(-300, 300);
                display.DataSources[j].SetGridDistanceY(100);
                display.DataSources[j].OnRenderYAxisLabel = RenderYLabel;
                CalcSinusFunction_0(display.DataSources[j], j);
                break;

            case "STACKED":
                this.Text = "Stacked Graph";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.STACKED;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].SetDisplayRangeY(-250, 250);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_1(display.DataSources[j], j);
                break;

            case "VERTICAL_ALIGNED":
                this.Text = "Vertical aligned Graph";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.VERTICAL_ARRANGED;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].SetDisplayRangeY(-300, 300);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "VERTICAL_ALIGNED_AUTO":
                this.Text = "Vertical aligned Graph autoscaled";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.VERTICAL_ARRANGED;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = true;
                display.DataSources[j].SetDisplayRangeY(-300, 300);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "TILED_VERTICAL":
                this.Text = "Tiled Graphs (vertical prefered)";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.TILES_VER;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].SetDisplayRangeY(-300, 600);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "TILED_VERTICAL_AUTO":
                this.Text = "Tiled Graphs (vertical prefered) autoscaled";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.TILES_VER;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = true;
                display.DataSources[j].SetDisplayRangeY(-300, 600);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "TILED_HORIZONTAL":
                this.Text = "Tiled Graphs (horizontal prefered)";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.TILES_HOR;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].SetDisplayRangeY(-300, 600);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "TILED_HORIZONTAL_AUTO":
                this.Text = "Tiled Graphs (horizontal prefered) autoscaled";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.TILES_HOR;
                display.DataSources[j].Length = 5800;
                display.DataSources[j].AutoScaleY = true;
                display.DataSources[j].SetDisplayRangeY(-300, 600);
                display.DataSources[j].SetGridDistanceY(100);
                CalcSinusFunction_2(display.DataSources[j], j);
                break;

            case "ANIMATED_AUTO":

                this.Text = "Animated graphs fixed x range";
                display.PanelLayout = PlotterGraphPaneEx.LayoutMode.TILES_HOR;
                display.DataSources[j].Length = 402;
                display.DataSources[j].AutoScaleY = false;
                display.DataSources[j].AutoScaleX = true;
                display.DataSources[j].SetDisplayRangeY(-300, 500);
                display.DataSources[j].SetGridDistanceY(100);
                display.DataSources[j].XAutoScaleOffset = 50;
                CalcSinusFunction_3(display.DataSources[j], j, 0);
                display.DataSources[j].OnRenderYAxisLabel = RenderYLabel;
                break;
        }
    }

    ApplyColorSchema();

    this.ResumeLayout();
    display.Refresh();

}

private String RenderXLabel(DataSource s, int idx)
{
    if (s.AutoScaleX)
    {
        //if (idx % 2 == 0)
        {
            int Value = (int)(s.Samples[idx].x);
            return "" + Value;
        }
        return "";
    }
    else
    {
        int Value = (int)(s.Samples[idx].x / 200);
        String Label = "" + Value + "\"";
        return Label;
    }
}

private String RenderYLabel(DataSource s, float value)
{
    return String.Format("{0:0.0}", value);
}

protected override void OnClosing(CancelEventArgs e)
{
    display.Dispose();

    base.OnClosing(e);
}
*/
