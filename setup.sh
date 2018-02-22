# Setup for local environment

PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PYTHONPATH=$PWD:$PYTHONPATH
export PATH=$PWD/scripts:$PATH
