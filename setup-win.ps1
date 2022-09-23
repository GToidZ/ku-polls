<#
.Description
This is a script for setting up your KU Polls server application.
#>

if (Test-Path -Path .\polls\fixtures) {
    Remove-Item .\polls\fixtures -Recurse
}

if (!(Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host @'
Requires Python 3 to be installed on your system!
Make sure it is installed then run setup again...
'@
    exit 1
}

py -c "import sys; assert sys.version_info >= (3, 9)" 2>&1>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host @'
Python executed was outdated!
Requires Python 3.9 or greater to be installed on your system!
Make sure it is installed then run setup again...
'@
    exit 1
}

Write-Host "Requirements met, starting setup..."
Write-Host ""

# Download jq
Write-Host "Downloading jq... (one-time use)"
Invoke-WebRequest -Uri "https://github.com/stedolan/jq/releases/download/jq-1.5/jq-win64.exe" -OutFile "jq.exe"

# Make a Python virtualenv (venv)
Write-Host "Preparing venv..."
py -m venv .venv
.\.venv\Scripts\activate.ps1

# pip install
Write-Host "Installing dependencies..."
pip install -r requirements.txt 2>&1>$null

# Migrate database
Write-Host "Applying migrations to database..."
py .\manage.py migrate 2>&1>$null

# Test the polls app
Write-Host "Testing app before setting up..."
$TEST_STATUS = 0
py .\manage.py test polls > tests.log 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Testing failed! This might be a developer's fault!"
    Write-Host "You should create a new issue on https://github.com/GToidZ/ku-polls/issues and attach the 'tests.log' file"
    Write-Host ""
}
else {
    Write-Host "Tests passed!"
    $TEST_STATUS = 1
}

if ($TEST_STATUS -ge 1) {
    Write-Host ""
    $continue = $true
    $setup = $false
    while ($continue) {
        $yn = Read-Host "Do you want to setup a poll now? [Y/n]"
        switch -Regex ($yn) {
            "^[yY]$" { 
                $setup = $true
                $continue = $false
                break
            }
            "^[nN]$" {
                $continue = $false
                break
            }
            "^.{0}$" {
                $setup = $true
                $continue = $false
                break
            }
            "^.+$" {
                Write-Host "Please answer y or n."
            }
        }
    }
    if ($setup -eq $true) {
        $NOW = (Get-Date).ToUniversalTime()
        $DATETIME_NOW = (Get-Date $NOW -Format "yyyy-MM-ddTHH:mm:ssZ")
        Write-Host @"

INFO: This will setup only one poll, with the time of when the script is executed!
INFO: To setup more polls, do so in Admin page of the application.

"@
        $continue = $true
        while ($continue) {
            $q = Read-Host "Poll question"
            switch -Regex ($q) {
                "^.{0}$" {
                    Write-Host "Question cannot be blank!"
                }
                "^.+$" {
                    $continue = $false
                    break
                }
            }
        }

        $question_json = @"
{
    "model": "polls.question",
    "pk": 1,
    "fields":
    {
        "question_text": "$q",
        "publish_date":  "$DATETIME_NOW",
        "end_date": null,
        "visibilty": true
    }
},
"@

        $choices_json = ""
        $count = 1
        $continue = $true
        while ($continue) {
            $inner_cont = $true
            while ($inner_cont) {
                $c = Read-Host "Poll choice #$count"
                switch -Regex ($c) {
                    "^.{0}$" {
                        Write-Host "Choice cannot be blank!"
                    }
                    "^.+$" {
                        $inner_cont = $false
                        break
                    }
                }
            }
            $choice_partial = @"
{
    "model": "polls.choice",
    "pk": $count,
    "fields":
    {
        "question": 1,
        "choice_text": "$c"
    }
}
"@
            $choices_json = "$choices_json$choice_partial"
            $next = $true
            if ($count -ge 3) {
                $inner_cont = $true
                while ($inner_cont) {
                    $c = Read-Host "Do you want to add more choice? [y/N]"
                    switch -Regex ($c) {
                        "^[yY]$" {
                            $inner_cont = $false
                            break
                        }
                        "^[nN]$" {
                            $next = $false
                            $inner_cont = $false
                            break
                        }
                        "^.{0}$" {
                            $next = $false
                            $inner_cont = $false
                            break
                        }
                        "^.+$" {
                            Write-Host "Please answer y or n."
                        }
                    }
                }
            }
            if ($next -eq $true) {
                $count = $count + 1
                $choices_json = "$choices_json,"
            }
            else {
                $continue = $false
                break
            }
        }
        $json = "[$question_json$choices_json]"
        mkdir .\polls\fixtures\ 2>&1>$null
        echo $JSON | .\jq.exe '.' | Out-File -Encoding ascii .\polls\fixtures\data.json
        Start-Sleep -Seconds 1.5

        Write-Host "Applying data fixtures..."
        py .\manage.py loaddata data 2>&1>$null
    }

    Write-Host ""
    Write-Host "INFO: You are required to create an admin account for Django dashboard"
    py .\manage.py createsuperuser

    Write-Host @"
Congratulations! Application successfully installed!
To start the application enter:
.\.venv\Scripts\activate; py ./manage.py runserver 8000
"@
}

deactivate
Remove-Item .\jq.exe
if ($TEST_STATUS -ge 1) {
    Remove-Item .\tests.log
}
else {
    $continue = $true;
    while ($continue) {
        $yn = Read-Host "Setup failed, do you want to keep the virtual environment? [y/N]"
        switch -Regex ($yn) {
            "^[yY]$" {
                $continue = $false
            }
            "^[nN]$" {
                Remove-Item .\.venv -Recurse
                $continue = $false
                break
            }
            "^.{0}$" {
                Remove-Item .\.venv -Recurse
                $continue = $false
                break
            }
            "^.+$" {
                Write-Host "Please answer y or n."
            }
        }
    }
}