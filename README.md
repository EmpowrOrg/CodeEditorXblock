# CodeEditorXblock

An XBlock for Empowr's course platform that allows for the input and checking of any programming language.

![Code Editor Screenshot](code-editor.png)

<!-- TOC -->
* [CodeEditorXblock](#codeeditorxblock)
  * [Installation](#installation)
    * [Run the Django development server](#run-the-django-development-server)
<!-- TOC -->


## Installation

1. Make sure you have have Python 3.8 installed on your computer.

2. Clone the repo with `git clone --recurse-submodules git@github.com:EmpowrOrg/CodeEditorXblock.git`. This will give
   you the repo including the xblock-sdk submodule.

3. Create and Activate the Virtual Environment:

You must have a virtual environment tool installed on your computer. For more information,
see [Install XBlock Prerequisites](https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/getting_started/prereqs.html)
.

Then create the virtual environment in your CodeEditorXblock directory.

At the command prompt in CodeEditorXblock, run the following command to create the virtual environment.

`virtualenv venv`

Run the following command to activate the virtual environment.

`source venv/bin/activate`

Install the plugin with

`pip install -e swiftplugin`

4. Navigate to the xblock-sdk directory and run the following command to install the requirements.

`pip install -r requirements/base.txt`

### Run the Django development server

Navigate to the xblock-sdk directory and run the following commands.

`make install`

`python manage.py migrate`

`python manage.py runserver`
