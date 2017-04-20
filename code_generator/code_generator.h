// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the CODE_GENERATOR_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// CODE_GENERATOR_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef CODE_GENERATOR_EXPORTS
#define CODE_GENERATOR_API __declspec(dllexport)
#else
#define CODE_GENERATOR_API __declspec(dllimport)
#endif

// This class is exported from the code_generator.dll
class CODE_GENERATOR_API Ccode_generator {
public:
	Ccode_generator(void);
	// TODO: add your methods here.
};

extern CODE_GENERATOR_API int ncode_generator;

CODE_GENERATOR_API int fncode_generator(void);
