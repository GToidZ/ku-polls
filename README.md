# Online Polls for KU

<!-- BEGIN BADGES -->
![tests status](https://img.shields.io/github/workflow/status/GToidZ/ku-polls/Test%20KU%20Polls?label=tests&logo=github)
[![codecov](https://codecov.io/gh/GToidZ/ku-polls/branch/feat/ci/graph/badge.svg?token=0SCEVDMAU0)](https://codecov.io/gh/GToidZ/ku-polls)
<!-- END BADGES -->

A web application for conducting online polls and surveys written in Python using Django web framework.<br>
The application is based off the [Django Tutorial][django-tutorial] but with tweaks.

The application is a part of the [Individual Software Process](https://cpske.github.io/ISP) course at [Kasetsart University](https://ku.ac.th/).

# Prerequisites
## Required on any OS
* Python 3.9 or greater
* Python with ensurepip available
## For Linux / Mac (x64)
* sh
* cURL
## For Windows
* System running on 64-bit
* Powershell 5 or greater

*Note: The application might not work on Gentoo, Alpine. For Linux users, it is recommended to install `lscpu` before setup.*

# Installation
*Note: This is recommended for fresh installs, existing databases might be affected if installed in non-fresh repo.*

Clone this repository into your desired location,

```sh
git clone https://github.com/GToidZ/ku-polls.git ku-polls
```

Change your directory into the repository,

```sh
cd ku-polls
```

**Before doing anything else, you will need to configure your server using `settings.ini`!**<br>Take a look at `settings.example.ini` on how you can create your own `settings.ini`

> Alternatively, you can provide environment variables with the same name as options in the `settings.example.ini` instead, but it is recommended to use files since they are more persistant.

The next step is to setup the application by executing a script, choose the script that satisfies your operating system:

|OS|File|
|:-:|:-:|
|Linux/GNU|`setup-linux.sh`|
|Mac|`setup-mac.sh`|
|Windows|`setup-win.ps1`|

For example, in Linux:
```sh
./setup-linux.sh
```

*For Linux/Mac: You might need to `chmod +x` the script before running it.*

*For Linux/Mac (2): You can also specify which Python installation you will use by passing an argument to the script. `./setup-linux.sh python3.9`*

**Now, follow the instructions on your prompt/terminal, and let the automation do the work.**

```sh
Congratualations! Application successfully installed!
To start the application enter:
. ./.venv/bin/activate && python3 ./manage.py runserver 8000
```

When you see this message, it means that you have successfully installed the application! You can start running it by using the command at the bottom of message.

# Running

After installing, you should be able to start the server by using (while sourcing venv),

```sh
python3 ./manage.py runserver 8000
```

You can then visit, `http://localhost:8000`

## Web Structure
The site has two links you can go to, `/polls` and `/admin`.

The main page is at `/polls`. You can display polls that are currently open, view results of a poll and login to the application in order to vote. You can also visit this page via `/`. 

The admin page is at `/admin`. You can create, edit, delete polls and users in here. It is **recommended** to setup your website here before going production.

# Project Documentation

[Vision Statement](https://github.com/GToidZ/ku-polls/wiki/Vision-Statement)

[Requirements](https://github.com/GToidZ/ku-polls/wiki/Requirements)

[Development Plan](https://github.com/GToidZ/ku-polls/wiki/Development-Plan)

## Iterations

* Iteration 1 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-1-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/2)
* Iteration 2 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-2-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/5)
* Iteration 3 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-3-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/6)
* Iteration 4 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-4-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/7)

<!-- Using absolute paths for wiki, since it could break clones and forks. -->

[django-tutorial]: https://docs.djangoproject.com/en/4.1/intro/tutorial01/
[howto-venv]: https://docs.python.org/3/library/venv.html#creating-virtual-environments
