#!/usr/bin/sh

usage() {
    echo "Usage: $0 [python executable]"
    echo "* python executable: which Python to use (e.g. python3, python3.9)"
    exit 2
}

while getopts ":h" arg; do
    case $arg in
        h ) usage;;
        * ) usage;;
    esac
done

REPOSITORY="https://github.com/GToidZ/ku-polls"
PYTHON=${1:-python3}

err() {
    echo "$@" 1>&2;
}

report_requires() {
    err "Requires $1 to be installed on your system!"
    err "Make sure it is installed then run setup again..."
    exit 1
}

[ -d ./polls/fixtures ] && rm -rf ./polls/fixtures

# Requiring cURL
if ! command -v curl > /dev/null 2>&1
then
    report_requires "cURL"
fi

# Requiring Python>=3.8 w/ venv support
if ! command -v $PYTHON > /dev/null 2>&1
then
    report_requires "Python 3"
else
    if ! $PYTHON -c "import sys; assert sys.version_info >= (3, 9)" > /dev/null 2>&1
    then
        err "Python executed was outdated!"
        report_requires "Python 3.9 or greater"
    else
        if ! $PYTHON -c "import ensurepip" > /dev/null 2>&1
        then
            err "Python's ensurepip not found!"
            report_requires "Python virtual environment support"
        fi
    fi
fi

echo "Requirements met, starting setup..."
echo ""

# Download 'jq'
# Check CPU architecture for compatibility, then download jq
echo "Downloading jq... (one-time use)"
if (lscpu | grep -q "64-bit") ; then
    curl -L "https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64" -o ./jq > /dev/null 2>&1;
else
    curl -L "https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux32" -o ./jq > /dev/null 2>&1;
fi

# Make jq executable
chmod +x ./jq

# Make a Python virtualenv (venv)
echo "Preparing venv..."
$PYTHON -m venv .venv
. .venv/bin/activate

# pip install
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1;

# Migrate database
echo "Applying migrations to database..."
$PYTHON ./manage.py migrate > /dev/null 2>&1;

# Test the polls app
TEST_STATUS=0
echo "Testing app before setting up..."
if ! $PYTHON ./manage.py test polls > tests.log 2>&1;
then
    err "Testing failed! This might be a developer's fault!"
    err "You should create a new issue on $REPOSITORY/issues and attach the 'tests.log' file"
    echo ""
else
    echo "Tests passed!"
    TEST_STATUS=1
fi

# This will run if testing passes
if [ $TEST_STATUS -ge 1 ]; then
    echo ""
    # Prompt to create a poll
    while true; do
        read -p "Do you want to setup a poll now? [Y/n] " yn
        case $yn in
            [Yy]* ) SETUP=1; break;;
            [Nn]* ) break;;
            "" ) SETUP=1; break;;
            * ) echo "Please answer y or n.";;
        esac
    done

    if [ $SETUP -ge 1 ]; then
        DATETIME_NOW=$(date -u +%FT%TZ)
        echo ""
        echo "INFO: This will setup only one poll, with the time of when the script is executed!"
        echo "INFO: To setup more polls, do so in Admin page of the application."
        echo ""
        while true; do
            read -p "Poll question: " q
            case $q in
                ""|\ ) echo "Question cannot be blank!";;
                * ) QUESTION_TEXT=$q; break;;
            esac
        done
        
        QUESTION="{
            \"model\": \"polls.question\",
            \"pk\": 1,
            \"fields\":
            {
                \"question_text\": \"$QUESTION_TEXT\",
                \"publish_date\":  \"$DATETIME_NOW\",
                \"end_date\": null,
                \"visibilty\": true
            }
        },"

        CHOICES=""
        COUNT=1
        while true; do
            while true; do
                read -p "Poll choice #$COUNT: " c
                case $c in
                    ""|\ ) echo "Choice cannot be blank!";;
                    * ) CHOICE_TEXT=$c; break;;
                esac
            done
            CHOICE_JSON="{
                \"model\": \"polls.choice\",
                \"pk\": $COUNT,
                \"fields\":
                {
                    \"question\": 1,
                    \"choice_text\": \"$CHOICE_TEXT\"
                }
            }"
            CHOICES="$CHOICES$CHOICE_JSON"
            if [ $COUNT -ge 3 ]; then
                while true; do
                    read -p "Do you want to add more choice? [y/N] " yn
                    case $yn in
                        [yY]* ) break;;
                        [nN]* ) FINISHED=1; break;;
                        "" ) FINISHED=1; break;;
                        * ) echo "Please answer yes or no.";;
                    esac
                done
            fi
            if [ ! -z "$FINISHED" ] && [ $FINISHED -ge 1 ]; then
                break;
            else
                COUNT=`expr $COUNT + 1`
                CHOICES="$CHOICES,"
            fi
        done
    
        JSON="[$QUESTION$CHOICES]"
        [ -d ./polls/fixtures ] || mkdir -p ./polls/fixtures
        echo $JSON | ./jq '.' > ./polls/fixtures/data.json

        echo "Applying data fixtures..."
        $PYTHON ./manage.py loaddata data > /dev/null 2>&1
    fi

    echo ""
    echo "INFO: You are required to create an admin account for Django dashboard"
    $PYTHON ./manage.py createsuperuser

    # Finishing touches
    echo "Congratulations! Application successfully installed!"
    echo "To start the application enter:"
    echo ". ./.venv/bin/activate && $PYTHON ./manage.py runserver 8000"
fi

# Clean-up
rm ./jq
if [ $TEST_STATUS -ge 1 ];
then
    rm tests.log
else
    while true; do
        read -p "Setup failed, do you want to keep the virtual environment? [y/N] " yn
        case $yn in
            [Yy]* ) exit 1;;
            [Nn]* ) rm -rf .venv; exit 1;;
            "" ) rm -rf .venv; exit 1;;
            * ) echo "Please answer y or n.";;
        esac
    done
fi
