using System;
using System.IO;
using System.Text.RegularExpressions;

namespace Servo_Multi
{
    public class TextFromFile
    {
        //private const string FILE_NAME = "MyFile.txt";

        public string readFile(string filename)
        {
            string FILE_NAME = filename;
            string output = "";

            if (!File.Exists(FILE_NAME))
            {
                output = FILE_NAME + " does not exist.";
                return output;
            }
            using (StreamReader sr = File.OpenText(FILE_NAME))
            {
                String input;
                
                while ((input = sr.ReadLine()) != null)
                {
                    //Console.WriteLine(input);
                    output += Environment.NewLine + input;
                }
                //Console.WriteLine("The end of the stream has been reached.");
                output += Environment.NewLine + "The end of the stream has been reached.";
                return output;
            }
        }
               
        public bool appendFile(string filename, string content)
        {

            // FUNCTION :: Append a line to an existing file
            // Note: if file does not exist it will be created

            using (System.IO.StreamWriter file = new System.IO.StreamWriter(@filename, true))
            {
                file.WriteLine(content);
            }

            return true;
        }






        public string readConfigFile(string filename, string[] analogSensorInput, string[] digitalRelayOutput, string[] gpioOutput, string[] digitalSensorInput)
        {
            string FILE_NAME = filename;
            string output = "";

            if (!File.Exists(FILE_NAME))
            {
                output = FILE_NAME + " does not exist.";
                return output;
            }
            using (StreamReader sr = File.OpenText(FILE_NAME))
            {
                String input;

                string curSection = "";
                int curKey = 0;
                string curValue = "";

                while ((input = sr.ReadLine()) != null)
                {
                    input = Regex.Replace(input, @"\t|\n|\r| ", "");    // remove whitespace and tabs from string

                    switch (input)
                    {
                        case "[analogSensorInput]":
                            curSection = "analogSensorInput";
                            break;
                        case "[digitalRelayOutput]":
                            curSection = "digitalRelayOutput";
                            break;
                        case "[gpioOutput]":
                            curSection = "gpioOutput";
                            break;
                        case "[digitalSensorInput]":
                            curSection = "digitalSensorInput";
                            break;
                        default:

                            if (input != "")
                            {
                                string[] parts = input.Split('=');      // explode the line
                                curKey = Convert.ToInt32(parts[0]);     // figure out the key - convert it to integer
                                curValue = parts[1];                    // figure out the value


                                switch (curSection)
                                {
                                    case "analogSensorInput":
                                        analogSensorInput[curKey] = curValue;
                                        break;
                                    case "digitalRelayOutput":
                                        digitalRelayOutput[curKey] = curValue;
                                        break;
                                    case "gpioOutput":
                                        gpioOutput[curKey] = curValue;
                                        break;
                                    case "digitalSensorInput":
                                        digitalSensorInput[curKey] = curValue;
                                        break;
                                }

                                curKey = -1;
                                curValue = "";

                            } // end blank line check

                            break;
                    }

                }
                //Console.WriteLine("The end of the stream has been reached.");
                output += Environment.NewLine + "The end of the stream has been reached.";
                return output;
            }
        }






    } //end class
} //end namespace