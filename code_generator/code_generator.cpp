// code_generator.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "code_generator.h"


// This is an example of an exported variable
CODE_GENERATOR_API int ncode_generator=0;

// This is an example of an exported function.
CODE_GENERATOR_API int fncode_generator(void)
{
    return 42;
}

// This is the constructor of a class that has been exported.
// see code_generator.h for the class definition
Ccode_generator::Ccode_generator()
{
    return;
}
