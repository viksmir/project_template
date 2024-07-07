// clang-format off
// windows header must be imported first
#include <windows.h>
// clang-format on


#include <iostream>

/// @brief Initializes the processor instance
/// @return 0 if no errors
extern "C" __declspec(dllexport) int ProjTemplate_SampleFunction()
{
    std::cout << "DLL's sample function called" << std::endl;
    return 0;
}

/// @brief DLL's entry point
/// @return TRUE on success
BOOL WINAPI DllMain(HINSTANCE hinstDLL,   // handle to DLL module
                    DWORD     fdwReason,  // reason for calling function
                    LPVOID    lpvReserved)
{
    // Perform actions based on the reason for calling.
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            break;

        case DLL_THREAD_ATTACH:
            break;

        case DLL_THREAD_DETACH:
            break;

        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}