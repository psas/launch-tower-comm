# Launch Tower Comm
Launch Tower Comm is the Portland State Aerospace Society's launch tower 
control.  

It is run by [Kivy](http://kivy.org), a multi-touch GUI framework, and 
[Phidgets](https://www.phidgets.com), "Unique and Easy to Use USB Interfaces."

[Portland State Aerospace Society](https://psas.pdx.edu)

---

## How to use it if you don't have a launch tower

If you have a remote Beagleboard or Raspberry Pi or similar connected to
Phidget Interface Kit boards, and want to control and observe them remotely,
this app could work for you.  

We use it to control relays connected to a Beagleboard on our launch
tower computer, and to display voltages and temperatures on the tower.


## Dependencies

The following list is not complete, in other words, each of the three items
may require dependencies not listed here.

* [Phidgets C library, Python module and Webservice](http://www.phidgets.com/docs/Software_Overview#Operating_System_Support)
* [Kivy](http://kivy.org/#download)
* At least one Phidgets Interfacekit connected throught the Phidgets webservice 

# Installation of Kivy and Twisted

## OS X 10.9 (Mavericks) 

* Valid as of Jan 25th 2014

Install Homebrew and get it setup properly, follow the suggestions it might
make.

    brew install python
    brew install virtualenvwrapper # might require additional setup
    brew install sdl sd_image sdl_mixer sdl_ttf portmidi
    brew install mercurial

    mkvirtualenv kivy
    pip install cython
    # pil might need a symlink to freetype, try it first
    pip install pil 
    pip install hg+http://bitbucket.org/pygame/pygame
    pip install kivy

At this point, grab a copy of the Kivy source that matches your installed
version. Copy the examples somewhere and try to run one of them. If things
don't work, get to googling.  If successful, you now need Twisted.

    pip install Twisted
