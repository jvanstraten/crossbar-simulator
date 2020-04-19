/** This test is for the bell example qasm file **/
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <iostream>
#include <vector>
#include <string>
#include "qasm_semantic.hpp"
#include "doctest/doctest.h"

TEST_CASE("Test for the bell.qasm file")
{
    #if YYDEBUG == 1
    extern int yydebug;
    yydebug = 1;
    #endif

    // open a file handle to a particular file:
    FILE *myfile = fopen("bell.qasm", "r");
    
    compiler::QasmSemanticChecker sm(myfile);

    auto qasm_representation = sm.getQasmRepresentation();
    
    int result = sm.parseResult();

    CHECK(result == 0);   // Stop here if it fails.
}