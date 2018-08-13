/* pymcpat swig interface file */

%module mcpat

%{
#define SWIG_FILE_WITH_INIT
#include "processor.h"
#include "XML_Parse.h"
#include "globalvar.h"
#include "version.h"
%}

%include "stdint.i"
%include "processor.h"
%include "XML_Parse.h"
%include "globalvar.h"
%include "version.h"
