// FW102CConsole.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include "FWxCCommand.h"
using namespace std;

int main()
{
	cout << "Welcome to FW102C command library test\n";
	cout << "Below are connected devices, please input com port:\n";
	unsigned char listStr[2048] = { 0 };
	int count = List(listStr, 2048);
	if (count == 0)
	{
		cout << "There is no FW102C device connected!\n";
		return 0;
	}
	cout << listStr << endl;

	char com[20] = { 0 };
	cin >> com;
	int hdl = Open(com, 115200, 10);
	if (hdl < 0)
	{
		cout << "open " << com << " failed!\n";
		return 0;
	}
	else
	{
		cout << "open successful!\n";
	}

	cout << "Key => q 'exit'\n";
	cout << "Key => c 'get position count'\n";
	cout << "Key => p 'position'\n";
	cout << "Key => d 'speed mode'\n";
	cout << "Key => s 'sensor mode'\n";
	cout << "Key => t 'trigger mode'\n";
	cout << "Key => o 'get time to current pos'\n";

	char ch = getchar();
	int pos = 0, posCount = 0, timeToCurrent = 0, speedMode = 0, triggerMode = 0, sensorMode = 0;

	while (ch != 'q')
	{
		switch (ch)
		{
		case 'c':
			GetPositionCount(hdl, &posCount);
			cout << "position count " << posCount << endl;
			break;
		case 'p':
		{
			if (posCount == 0)
			{
				GetPositionCount(hdl, &posCount);
			}
			int iPos = 0;
			while (iPos < 1 || iPos > posCount)
			{
				cout << "Inptut the pos 1~" << posCount << endl;
				cin >> iPos;
			}
			SetPosition(hdl, iPos);
			GetPosition(hdl, &pos);
			cout << "position get=> " << pos << endl;
		}
		break;
		case 'd':
		{
			int iSpeed = -1;
			while (iSpeed != 0 && iSpeed != 1)
			{
				cout << "Inptut the speed mode  0 slow speed ~ 1 high speed" << endl;
				cin >> iSpeed;
			}
			SetSpeedMode(hdl, iSpeed);
			GetSpeedMode(hdl, &speedMode);
			cout << "speed mode get=> " << speedMode << endl;
		}
		break;
		case 's':
		{
			int iSensor = -1;
			while (iSensor != 0 && iSensor != 1)
			{
				cout << "Inptut the sensor mode  0 trun off ~ 1 remain active" << endl;
				cin >> iSensor;
			}
			SetSensorMode(hdl, iSensor);
			GetSensorMode(hdl, &sensorMode);
			cout << "sensor mode get=> " << sensorMode << endl;
		}
		break;
		case 't':
		{
			int iTrigger = -1;
			while (iTrigger != 0 && iTrigger != 1)
			{
				cout << "Inptut the trigger mode  0 input mode ~ 1 output mode" << endl;
				cin >> iTrigger;
			}
			SetTriggerMode(hdl, iTrigger);
			GetTriggerMode(hdl, &triggerMode);
			cout << "trigger mode get=> " << triggerMode << endl;
		}
		break;
		case 'o':
		{
			GetTimeToCurrentPos(hdl, &timeToCurrent);
			cout << "Time to current pos is " << timeToCurrent << " milliseconds" << endl;
		}
		break;
		case '\n':
			break;
		default:
		{
			cout << ch << " is a not valid input" << endl;
		}
		}
		ch = getchar();
	}
	Close(hdl);
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
