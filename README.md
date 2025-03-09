# PyQt5ToCpp
A conversion utility that I'm coding for PyQt5 to C++ desktop application ease.

## How it works
The way it works now is that necessary code is embedded into (a copy of) the source Python app, 
which for certain statements will record and communicate type information to this GUI. 

The user is expected to interact with as many parts of the app as possible in order for good code coverage to happen. 
The user can then complete this table of types or later complete the C++ types manually. 
