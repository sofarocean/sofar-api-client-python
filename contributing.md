# Steps for Contributing


### Contribution info
- If you see a bug or want to request a feature open an issue on github
    and label it with either `feature` or `bug` appropriately. We will try 
    to respond as quickly as possible to either. 
    
- If you wish to contribute to an existing bug please comment to let us know 
    that you are working on the issue and for updates on progress.
    
- Similarly if you want to work on a open `feature` request, comment on the issue
    to let us know.

### Development Setup
1. Fork this repository to your local account. You will not be allowed to push straight to 
    master, so forking will allow you to push your changes. 

2. Git clone the forked repository to a local location
    `git clone <location>`

2. Make sure you have Python3 (3.7 Preferred) as well as pip 
    installed and working correctly. If you don't have pip because you are using 
    a python version 3 < x < 3.4 then you should install it according to [this](https://pip.pypa.io/en/stable/installing/).
    This project may work on Python2 but we will not be supporting any development towards Python2 related issues
    since Python2 is being depreciated.

3. CD to where you downloaded the repository

   Note: Its recommended to use a virtual environment to help manage your python projects and 
    dependencies. You can set one up by first installing virtualenv with `pip install virtualenv`
    and then `python3 -m venv <venv name>`. Usually people will run `python3 -m venv venv` which 
    creates a virtual environment named `venv` to keep things simple. Activate the virtual environment
    with `source venv/bin/activate`. To exit the virtual environment run `deactivate`. While inside the 
    virtual environment your python and all of its packages are associated with that specific virtualenvironment.
    Any `pip install <pkg_name` will install that package to your specific venv. This helps keep dependencies 
    for different projects simple, since you won't have to worry about changing installed packages globally.
    Just remember to activate when you start working on the project, and deactivate when you are done.
    
4. Cd into the directory and install the requirements. You can install them manually or `pip install -r requirements.txt`

5. Add an upstream remote to get updates from our branch with `git remote add upstream https://www.github.com/sofarocean/wavefleet-client-python.git`

6. You must do your work on a branch otherwise it will not be accepted. If you are working on a bug name your branch `bug/<bug_name`,
    and if you are working on a feature, comment `feature/<feature_name>`. You can create the branch locally with 
    `git checkout -b branch_name` and then push it to github with `git push --set-upstream origin branch_name`.

7.  For smaller contributions like updating a readme,
    or fixing a small bug that is already covered by the test suite then you are most likely find with not adding any.
    Otherwise when you finish your work, add tests to the `tests` folder. Test your code by running `pytest` in the main 
    repo directory.
    
8. If everything passes feel free to open a pull request to the staging branch and we will review the code. If you are stuck on a certain issue
    feel free to add more comments and questions to the issue thread and we will do our best to help you out!
    
9. Thank you for contributing!!
