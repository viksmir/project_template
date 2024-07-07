// clang-format off
// windows header must be imported first
#include <windows.h>
// clang-format on


#include "sampleClass.hpp"

#include <memory>

int main(int argc, char* argv[])
{
    std::shared_ptr<SampleClass> sampleClass = std::make_shared<SampleClass>();
    sampleClass->SampleFunction();
}