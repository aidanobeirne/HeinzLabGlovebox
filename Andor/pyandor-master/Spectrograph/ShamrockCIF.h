#pragma hdrstop

#define SHAMROCK_COMMUNICATION_ERROR 20201
#define SHAMROCK_SUCCESS 20202
#define SHAMROCK_P1INVALID 20266
#define SHAMROCK_P2INVALID 20267
#define SHAMROCK_P3INVALID 20268
#define SHAMROCK_P4INVALID 20269
#define SHAMROCK_NOT_INITIALIZED 20275
#define SHAMROCK_NOT_AVAILABLE 20292

#define SHAMROCK_ACCESSORYMIN 1
#define SHAMROCK_ACCESSORYMAX 2
#define SHAMROCK_FILTERMIN 1
#define SHAMROCK_FILTERMAX 6
#define SHAMROCK_TURRETMIN 1
#define SHAMROCK_TURRETMAX 3
#define SHAMROCK_GRATINGMIN 1
#define SHAMROCK_SLITWIDTHMIN 10
#define SHAMROCK_SLITWIDTHMAX 2500
#define SHAMROCK_I24SLITWIDTHMAX 24000
#define SHAMROCK_SHUTTERMODEMIN 0
#define SHAMROCK_SHUTTERMODEMAX 1
#define SHAMROCK_DET_OFFSET_MIN -240000
#define SHAMROCK_DET_OFFSET_MAX 240000
#define SHAMROCK_GRAT_OFFSET_MIN -20000
#define SHAMROCK_GRAT_OFFSET_MAX 20000

#define SHAMROCK_SLIT_INDEX_MIN    1
#define SHAMROCK_SLIT_INDEX_MAX    4

#define SHAMROCK_INPUT_SLIT_SIDE   1
#define SHAMROCK_INPUT_SLIT_DIRECT  2
#define SHAMROCK_OUTPUT_SLIT_SIDE  3
#define SHAMROCK_OUTPUT_SLIT_DIRECT 4

#define SHAMROCK_FLIPPER_INDEX_MIN    1
#define SHAMROCK_FLIPPER_INDEX_MAX    2
#define SHAMROCK_PORTMIN 0
#define SHAMROCK_PORTMAX 1

#define SHAMROCK_INPUT_FLIPPER   1
#define SHAMROCK_OUTPUT_FLIPPER  2
#define SHAMROCK_DIRECT_PORT  0
#define SHAMROCK_SIDE_PORT    1

#define SHAMROCK_ERRORLENGTH 64

#include "windows.h"
#ifdef __cplusplus
extern "C" {
#endif

#ifdef linux
  #define EXPSHAMTYPE
#else
  #define EXPSHAMTYPE __declspec(dllexport)
#endif

//sdkbasic functions
EXPSHAMTYPE unsigned int WINAPI ShamrockInitialize(char * IniPath);
EXPSHAMTYPE unsigned int WINAPI ShamrockClose(void);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetNumberDevices(int *nodevices);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetFunctionReturnDescription(int error,char *description, int MaxDescStrLen);
//sdkeeprom functions
EXPSHAMTYPE unsigned int WINAPI ShamrockGetSerialNumber(int device,char *serial);
EXPSHAMTYPE unsigned int WINAPI ShamrockEepromGetOpticalParams(int device,float *FocalLength,float *AngularDeviation,float *FocalTilt);
//sdkgrating functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetGrating(int device,int grating);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetGrating(int device,int *grating);
EXPSHAMTYPE unsigned int WINAPI ShamrockWavelengthReset(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetNumberGratings(int device,int *noGratings);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetGratingInfo(int device,int Grating, float *Lines,  char* Blaze, int *Home, int *Offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetDetectorOffset(int device,int offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetDetectorOffset(int device,int *offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetDetectorOffsetPort2(int device,int offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetDetectorOffsetPort2(int device,int *offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetGratingOffset(int device,int Grating, int offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetGratingOffset(int device,int Grating, int *offset);
EXPSHAMTYPE unsigned int WINAPI ShamrockGratingIsPresent(int device,int *present);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetTurret(int device,int Turret);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetTurret(int device,int *Turret);
//sdkwavelength functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetWavelength(int device, float wavelength);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetWavelength(int device, float *wavelength);
EXPSHAMTYPE unsigned int WINAPI ShamrockGotoZeroOrder(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockAtZeroOrder(int device, int *atZeroOrder);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetWavelengthLimits(int device, int Grating, float *Min, float *Max);
EXPSHAMTYPE unsigned int WINAPI ShamrockWavelengthIsPresent(int device,int *present);
//sdkslit functions

// New Slit Functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetAutoSlitWidth(int device, int index, float width);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetAutoSlitWidth(int device, int index, float *width);
EXPSHAMTYPE unsigned int WINAPI ShamrockAutoSlitReset(int device, int index);
EXPSHAMTYPE unsigned int WINAPI ShamrockAutoSlitIsPresent(int device, int index, int *present);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetAutoSlitCoefficients(int device, int index, int x1, int y1, int x2, int y2);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetAutoSlitCoefficients(int device, int index, int &x1, int &y1, int &x2, int &y2);

///// Deprecated Slit Functions
// Deprecated Input Slit Functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetSlit(int device,float width);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetSlit(int device,float *width);
EXPSHAMTYPE unsigned int WINAPI ShamrockSlitReset(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockSlitIsPresent(int device,int *present);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetSlitCoefficients(int device, int x1, int y1, int x2, int y2);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetSlitCoefficients(int device, int &x1, int &y1, int &x2, int &y2);

// Deprecated Ouput Slit functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetOutputSlit(int device,float width);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetOutputSlit(int device,float *width);
EXPSHAMTYPE unsigned int WINAPI ShamrockOutputSlitReset(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockOutputSlitIsPresent(int device,int *present);
/////

//sdkshutter functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetShutter(int device,int mode);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetShutter(int device, int *mode);
EXPSHAMTYPE unsigned int WINAPI ShamrockIsModePossible(int device,int mode,int *possible);
EXPSHAMTYPE unsigned int WINAPI ShamrockShutterIsPresent(int device,int *present);
//sdkfilter functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetFilter(int device,int filter);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetFilter(int device,int *filter);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetFilterInfo(int device,int Filter, char* Info);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetFilterInfo(int device,int Filter, char* Info);
EXPSHAMTYPE unsigned int WINAPI ShamrockFilterReset(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockFilterIsPresent(int device,int *present);

//sdkflipper functions

// New flipper functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetFlipperMirror(int device, int flipper, int port);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetFlipperMirror(int device, int flipper, int * port);
EXPSHAMTYPE unsigned int WINAPI ShamrockFlipperMirrorReset(int device, int flipper);
EXPSHAMTYPE unsigned int WINAPI ShamrockFlipperMirrorIsPresent(int device, int flipper, int *present);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetCCDLimits(int device, int port, float *Low, float *High);

// Deprecated
EXPSHAMTYPE unsigned int WINAPI ShamrockSetPort(int device,int port);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetPort(int device, int*port);
EXPSHAMTYPE unsigned int WINAPI ShamrockFlipperReset(int device);
EXPSHAMTYPE unsigned int WINAPI ShamrockFlipperIsPresent(int device,int *present);

//sdkaccessory functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetAccessory(int device,int Accessory, int State);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetAccessoryState(int device,int Accessory, int *state);
EXPSHAMTYPE unsigned int WINAPI ShamrockAccessoryIsPresent(int device,int *present);
//sdkcalibration functions
EXPSHAMTYPE unsigned int WINAPI ShamrockSetPixelWidth(int device, float Width);
EXPSHAMTYPE unsigned int WINAPI ShamrockSetNumberPixels(int device, int NumberPixels);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetPixelWidth(int device, float* Width);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetNumberPixels(int device, int* NumberPixels);
EXPSHAMTYPE unsigned int WINAPI ShamrockGetCalibration(int device, float* CalibrationValues, int NumberPixels);
#ifdef __cplusplus
}
#endif
