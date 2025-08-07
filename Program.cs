using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace WifiReaper
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.Title = "WiFi Reaper - Legal Windows Wi-Fi Info Tool";
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine(@"
 __      __._____________.__         __________                                   
/  \    /  \__\_   _____/|__|        \______   \ ____ _____  ______   ___________ 
\   \/\/   /  ||    __)  |  |  ______ |       _// __ \\__  \ \____ \_/ __ \_  __ \
 \        /|  ||     \   |  | /_____/ |    |   \  ___/ / __ \|  |_> >  ___/|  | \/
  \__/\  / |__|\___  /   |__|         |____|_  /\___  >____  /   __/ \___  >__|   
       \/          \/                        \/     \/     \/|__|        \/       
");
            Console.ResetColor();
            Console.WriteLine("WiFi Reaper v1.0 (Legal Windows Wi-Fi Toolkit)\n");

            while (true)
            {
                Console.WriteLine("Select an option:");
                Console.WriteLine("1. Show saved Wi-Fi profiles with passwords");
                Console.WriteLine("2. Scan nearby Wi-Fi networks");
                Console.WriteLine("0. Exit");
                Console.Write("\nChoice: ");
                var choice = Console.ReadLine();

                switch (choice)
                {
                    case "1":
                        ShowSavedWifiPasswords();
                        break;
                    case "2":
                        ScanNearbyWifi();
                        break;
                    case "0":
                        return;
                    default:
                        Console.WriteLine("[!] Invalid choice.\n");
                        break;
                }

                Console.WriteLine("\nPress Enter to continue...");
                Console.ReadLine();
                Console.Clear();
            }
        }

        static void ShowSavedWifiPasswords()
        {
            Console.WriteLine("\n[*] Getting saved Wi-Fi profiles...\n");
            var profilesOutput = RunCommand("netsh wlan show profiles");

            var profileRegex = new Regex(@"All User Profile\s*:\s*(.+)");
            var matches = profileRegex.Matches(profilesOutput);

            if (matches.Count == 0)
            {
                Console.WriteLine("[!] No profiles found.");
                return;
            }

            foreach (Match match in matches)
            {
                var profileName = match.Groups[1].Value.Trim();
                Console.WriteLine($"> {profileName}");

                var profileDetails = RunCommand($"netsh wlan show profile name=\"{profileName}\" key=clear");

                var passwordMatch = Regex.Match(profileDetails, @"Key Content\s*:\s(.+)");
                var password = passwordMatch.Success ? passwordMatch.Groups[1].Value : "[No password found]";
                Console.WriteLine($"   Password: {password}\n");
            }
        }

        static void ScanNearbyWifi()
        {
            Console.WriteLine("\n[*] Scanning for nearby Wi-Fi networks...\n");
            var output = RunCommand("netsh wlan show networks mode=bssid");

            string[] lines = output.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            string currentSSID = "";
            foreach (var line in lines)
            {
                if (line.Contains("SSID"))
                {
                    var ssidMatch = Regex.Match(line, @"SSID \d+ : (.+)");
                    if (ssidMatch.Success)
                    {
                        currentSSID = ssidMatch.Groups[1].Value;
                        Console.ForegroundColor = ConsoleColor.Green;
                        Console.WriteLine($"> SSID: {currentSSID}");
                        Console.ResetColor();
                    }
                }
                else if (line.Contains("Signal"))
                {
                    var signalMatch = Regex.Match(line, @"Signal\s*:\s*(.+)");
                    if (signalMatch.Success)
                    {
                        Console.WriteLine($"   Signal: {signalMatch.Groups[1].Value}");
                    }
                }
                else if (line.Contains("Authentication"))
                {
                    var authMatch = Regex.Match(line, @"Authentication\s*:\s*(.+)");
                    if (authMatch.Success)
                    {
                        Console.WriteLine($"   Auth: {authMatch.Groups[1].Value}");
                    }
                }
                else if (line.Contains("Channel"))
                {
                    var chanMatch = Regex.Match(line, @"Channel\s*:\s*(.+)");
                    if (chanMatch.Success)
                    {
                        Console.WriteLine($"   Channel: {chanMatch.Groups[1].Value}");
                    }
                }
            }
        }

        static string RunCommand(string command)
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo("cmd.exe", "/c " + command)
                {
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };
            process.Start();
            string output = process.StandardOutput.ReadToEnd();
            process.WaitForExit();
            return output;
        }
    }
}