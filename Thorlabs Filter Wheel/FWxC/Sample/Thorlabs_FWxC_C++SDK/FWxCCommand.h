#pragma once
#ifdef __cplusplus
#ifdef FILTERWHEEL102_EXPORTS
#define DllExport extern "C" __declspec( dllexport )
#else
#define DllExport extern "C" __declspec( dllimport )
#endif
#else
#define DllExport 
#endif

/// <summary>
/// list all the possible port on this computer.
/// </summary>
/// <param name="serialNo">port list returned string include serial number and device descriptor, separated by comma</param>
/// <param name="length">max size of buf</param>
/// <returns>non-negative number: number of device in the list; negative number: failed.</returns>
DllExport int List(unsigned char *serialNo, unsigned int length);

/// <summary>
///  open port function.
/// </summary>
/// <param name="serialNo">serial number of the device to be opened, use GetPorts function to get exist list first.</param>
/// <param name="nBaud">bit per second of port</param>
/// <param name="timeout">set timeout value in (s)</param>
/// <returns> non-negtive number: hdl number returned successfully; negtive number : failed.</returns>
DllExport int Open(char* serialNo, int nBaud, int timeout);

/// <summary>
/// check opened status of port
/// </summary>
/// <param name="serialNo">serial number of the device to be checked.</param>
/// <returns> 0: port is not opened; 1 : port is opened.</returns>
DllExport int IsOpen(char *serialNo);

/// <summary>
/// close current opend port
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <returns> 0: success; negtive number : failed.</returns>
DllExport int Close(int hdl);

/// <summary>
/// <p>read string from device through opened port.</p>
/// <p>make sure the port was opened SUCCESSful before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="b">returned string buffer</param>
/// <param name="limit">
/// <p>ABS(limit): max length value of b buffer. </p>
/// <p>SIGN(limit) == 1 : wait RX event until time out value expired;</p>
/// <p>SIGN(limit) == -1: INFINITE wait event untill RX has data;</p>
/// </param>
/// <returns>non-negative number: size of actual read data in byte; negative number: failed.</returns>
DllExport int Read(int hdl, unsigned char *b, int limit);

/// <summary>
/// <p>write string to device through opened port.</p>
/// <p>make sure the port was opened SUCCESSful before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="b">input string</param>
/// <param name="size">size of string to be written.</param>
/// <returns>non-negative number: number of bytes written; negative number: failed.</returns>
DllExport int Write(int hdl, char *b, int size);

/// <summary>
/// <p>set command to device according to protocol in manual.</p>
/// <p>make sure the port was opened SUCCESSful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="c">input command string</param>
/// <param name="size">lenth of input command string (<255)</param>
/// <returns>
/// <p>0: SUCCESS; negative number: failed.</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int Set(int hdl, char *c, int size);

/// <summary>
/// <p>set command to device according to protocol in manual and get the return string.</p>
/// <p>make sure the port was opened SUCCESSful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="c">input command string (<255)</param>
/// <param name="d">output string (<255)</param>
/// <returns>
/// <p>0: SUCCESS; negative number: failed.</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int Get(int hdl, unsigned char *c, unsigned char *d);

/// <summary>
/// Purge the RX and TX buffer on port.
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="flag">
/// <p>FT_PURGE_RX: 0x01</p>
/// <p>FT_PURGE_TX: 0x02</p>
/// <returns> 0: SUCCESS; negative number: failed.</returns>
DllExport int Purge(int hdl, int flag);

/// <summary>
/// <p>set fiterwheel's position</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="pos">fiterwheel position</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int SetPosition(int hdl,int pos);

/// <summary>
/// <p>set fiterwheel's position count</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="count">fiterwheel PositionCount</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int SetPositionCount(int hdl,int count);

/// <summary>
/// <p>set fiterwheel's speed mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="mode">fiterwheel speed mode:speed=0 Sets the move profile to slow speed:speed=1 Sets the move profile to high speed</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int SetSpeedMode(int hdl,int mode);

/// <summary>
/// <p>set fiterwheel's trigger mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="mode">fiterwheel trigger mode:trig=0 Sets the external trigger to the input mode, Respond to an active low pulse by advancing position by 1;trig=1 Sets the external trigger to the output mode, Generate an active high pulse when selected position arrived at</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int SetTriggerMode(int hdl,int mode);

/// <summary>
/// <p>set fiterwheel's sensor mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="mode">fiterwheel sensor mode:sensors=0 Sensors turn off when wheel is idle to eliminate stray light;sensors=1 Sensors remain active</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int SetSensorMode (int hdl,int mode);

/// <summary>
/// <p>save all the settings as default on power up </p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int Save(int hdl);

/// <summary>
/// <p>get the fiterwheel current position</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="pos">fiterwheel actual position</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetPosition(int hdl,int* pos);

/// <summary>
/// <p>get the fiterwheel current position count</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="poscount">fiterwheel actual position count</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetPositionCount(int hdl,int* poscount);

/// <summary>
/// <p>get the fiterwheel current speed mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="speed">fiterwheel actual speed mode:0,slow speed:1,high speed</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetSpeedMode(int hdl,int* speed);

/// <summary>
/// <p>get the fiterwheel current trigger mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="triggermode">fiterwheel actual trigger mode:tr0, input mode;1, output mode</param></param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetTriggerMode(int hdl,int* triggermode);

/// <summary>
/// <p>get the fiterwheel current sensor mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="sensormode">fiterwheel actual sensor mode:0, Sensors turn off;1, Sensors remain active</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetSensorMode (int hdl,int* sensormode);

/// <summary>
/// <p>get the fiterwheel current sensor mode</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="time">the time from last position to current position</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetTimeToCurrentPos (int hdl,int* time);

/// <summary>
/// <p>get the fiterwheel id</p>
/// <p>make sure the port was opened successful before call this function.</p>
/// <p>make sure this is the correct device by checking the ID string before call this function.</p>
/// </summary>
/// <param name="hdl">handle of port.</param>
/// <param name="d">output string (<255)</param>
/// <returns>
/// <p>0: success;</p>
/// <p>0xEA: CMD_NOT_DEFINED;</p>
/// <p>0xEB: time out;</p>
/// <p>0xED: invalid string buffer;</p>
/// </returns>
DllExport int GetId(int hdl,char* d);
