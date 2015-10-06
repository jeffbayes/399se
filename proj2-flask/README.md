# proj2-flask
A starter project for using the Flask framework

## Basic task

* Fork on github (or bitbucket)
* Clone in your workspace and on ix
* Enhance the class schedule display
  * The starting date of each week should display
  * The current week (just the column with the week number, or the
    whole row if you prefer) should be highlighted in some way. 

## In your workspace

Copy CONFIG.base.py to CONFIG.py, and edit it. You can probably use
the standard port 5000 if you are the only user of the computer.

type `make install`

You might have to edit the Makefile to find the right version of
pyvenv.  The Makefile has a hacky workaround for a bug in the ubuntu
version on ix.cs.uoregon.edu; I think this will still work in most
environments, although it will be slower.  Try it and let me know. 

If you can run flask applications in your development environment, the
application would might be run by
`   python3 syllabus.py`
and then reached with url
`   http://localhost:5000`

Note that we do not use app.cgi when we can run flask applications
directly. 

This should work on MacOS, or on your own Linux box if you have one. I
don't know about Windows.  It won't work this way on ix, for a couple
of reasons:  First, there is only one port 5000 on ix, and we can't
all share it.  Also, I think the built-in flask server is not working
with Python3 on ix (although I could be wrong about that).

## On ix.cs.uoregon.edu

If you don't already have a top-level 'public_html' directory, create one: 

`  mkdir public_html`

within the public_html directory, it's probably a good idea to create a cis399
or cis322 subdirectory.  I've optimistically called mine cis322: 

`   cd public_html;  mkdir cis322`

Public_html is for serving web pages from your personal account.  We're going to be using the department's Apache web server to run our application as a 'cgi-bin' subprocess.  To do that, we'll need to keep our application in a subdirectory called 'htbin'. 

`   cd cis322;  mkdir htbin`

This is where we'll clone the project from Github.  

`   cd htbin;  git clone https://theURLofYourForkedProject`

Then `cd` into that directory.  From here it's going to be similar but 
not quite identical to working in your own workspace. 

Copy CONFIG.base.py to CONFIG.py, and edit it. You can't use the default
port 5000 there ... in fact we probably won't be able to use the default 
Flask server at all, but just in case set it to use a randomly chosen port.

type `make install`

 The Makefile has a hacky workaround for a bug in the ubuntu
version on ix, so this should work. 

What's really different is that we won't be running syllabus.py directly from the command line.  Instead, it is loaded as a Python module by a tiny Python program called app.cgi.  The 'cgi' suffix tells our web server to run the script, so we can reach it through the url `http://ix.cs.uoregon.edu/~michal/cis322/htbin/proj2-flask/app.cgi/`.  

The URLs are long and ugly, but it will do for testing. 

