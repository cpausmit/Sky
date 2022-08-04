#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Install the Sky package.
#---------------------------------------------------------------------------------------------------
# generate the setup file
rm -f setup.sh
touch setup.sh

# first the base directory and the path
echo "# CAREFUL THIS FILE IS GENERATED AT INSTALL"              >> setup.sh
echo "export SKY_BASE=`pwd`"                                    >> setup.sh
echo "export PATH=\"\${PATH}:\${SKY_BASE}/bin\""                >> setup.sh
echo "export PYTHONPATH=\"\${PYTHONPATH}:\${SKY_BASE}/python\"" >> setup.sh

exit 0
