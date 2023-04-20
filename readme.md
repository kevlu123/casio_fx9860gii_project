# Casio fx9860gii Project

This is a template for a Casio fx9860gii AddIn project, intended to make the development process easier as it does not require modifying obscure configuration files or interaction with the Casio fx9860gii SDK IDE.

## Building

Neither the Casio fx9860gii SDK nor Casio FA-124 should be required to build the project (not tested).

Place your source files in the `src` directory and run `build.py` to build the project.

Run `build.py --help` for more information.

## Debugging

You need to have the Casio fx9860gii SDK installed.

Open the generated .g1w file located in the `ide` directory and debug with the IDE.

## Deploying

You need to have Casio FA-124 installed.

Load the generated .g1a file located in the `build` directory into Casio FA-124.

Connect the calculator to your computer.

Copy the AddIn to the calculator with Casio FA-124.