from setuptools import setup

setup(
    name = "PyBrowserStack", # easy_install pocket
    description = "api wrapper for browserstack.com",
    long_description=open('README.md', 'rt').read(),

    # version
    # third part for minor release
    # second when api changes
    # first when it becomes stable someday
    version = "0.1.1",
    author = 'Hemendra Srivastava',
    author_email = "hemendra26@gmail.com",

    url = 'http://github.com/tapanpandita/pocket/',
    license = 'BSD',

    # as a practice no need to hard code version unless you know program wont
    # work unless the specific versions are used
    install_requires = ["requests", "simplejson"],

    py_modules = ["PyBrowserStack"],

    zip_safe = True,
)

# TODO: Do all this and delete these lines
# register: Create an accnt on pypi, store your credentials in ~/.pypirc:
#
# [pypirc]
# servers =
#     pypi
#
# [server-login]
# username:<username>
# password:<pass>
#
# $ python setup.py register # one time only, will create pypi page for pocket
# $ python setup.py sdist --formats=gztar,zip upload # create a new release
#
