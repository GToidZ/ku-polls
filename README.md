# Online Polls for KU

A web application for conducting online polls and surveys written in Python using Django web framework.<br>
The application is based off the [Django Tutorial][django-tutorial] but with tweaks.

The application is a part of the [Individual Software Process](https://cpske.github.io/ISP) course at [Kasetsart University](https://ku.ac.th/).

# Installation and Running

Clone this repository into your desired location,

```bash
git clone https://github.com/GToidZ/ku-polls.git ku-polls
```

Next, you will need to configure your server using `settings.ini`. Take a look at `settings.example.ini` on how you can create your own `settings.ini`

> Alternatively, you can provide environment variables with the same name as options in the `settings.example.ini` instead.

The next step is to install the packages required by this repository, for any Python users it is recommended to isolate the packages index by [making a virtual environment][howto-venv].

Once you have your virtual environment set up, activate it then,

```bash
# Run while sourcing the venv.
pip install -r requirements.txt
```

The final step is to run the development server by,

```bash
python ./manage.py runserver
```

You can now visit, `http://localhost:8000`

## Web Structure
The site has two links you can go to, `/polls` and `/admin`. At the current state, going to the **index** of site will give you an error.

The main page is at `/polls`.

The admin page is at `/admin`. The database comes with an insecure admin credentials, make sure to login and setup better admin credentials before deploying!

**Admin Credentials**
|Username|Password|
|:-:|:-:|
|admin|1234|

**User Credentials (for demo)**
|Username|Password|
|:-:|:-:|
|testuser1|12345678|
|testuser2|11223344|

# Project Documentation

[Vision Statement](https://github.com/GToidZ/ku-polls/wiki/Vision-Statement)

[Requirements](https://github.com/GToidZ/ku-polls/wiki/Requirements)

[Development Plan](https://github.com/GToidZ/ku-polls/wiki/Development-Plan)

## Iterations

Iteration 1 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-1-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/2)

Iteration 2 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-2-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/5)

Iteration 3 [Plan](https://github.com/GToidZ/ku-polls/wiki/Iteration-3-Plan) and [Project Board](https://github.com/users/GToidZ/projects/4/views/6)

<!-- Using absolute paths for wiki, since it could break clones and forks. -->

[django-tutorial]: https://docs.djangoproject.com/en/4.1/intro/tutorial01/
[howto-venv]: https://docs.python.org/3/library/venv.html#creating-virtual-environments
