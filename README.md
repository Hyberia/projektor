HYBERIA README
============

Version  : 0.2.1

1) Authors and thanks
---------------------

* Mathieu Charron  (LP: elwillow)
* Jamie Nadeau     (LP: james2432)
* Martin Samson    (LP: pyrolian)

Thanks to:
- The MPlayer Project
- The Matroska Project

2) Licensing
------------

Eiffel Forum License, version 2

1. Permission is hereby granted to use, copy, modify and/or
   distribute this package, provided that:
      * copyright notices are retained unchanged,
      * any distribution of this package, whether modified or not,
        includes this license text.
2. Permission is hereby also granted to distribute binary programs
   which depend on this package. If the binary program depends on a
   modified version of this package, you are encouraged to publicly
   release the modified version of this package.

THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.

3) Requirements
---------------

* Python 2.6
* C compiler (gcc)
* mkvtoolnix
* MPlayer with demuxer for you video files


5) Installation
---------------

Until there is a better way to install this setup, follow these instructions:

- Execute as root:
    ./install.sh
  It will build and install hyberiactl and readconfig then execute setup.py.

  This accepts the following arguments: install, uninstall, clean

  -install: This option is selected by default, and will build and install the application
  -uninstall: This will uninstall the application
  -clean: cleans the temporary files created during build

- Now run Projektor and check if there is any error in the logs
  Just hit ctrl+c when you're done (Projektor will send SIGTERM to mplayer and
  hyberiactl. hyberiactl does not output anything to the console. You should
  run a `tail -f` in the log file (default is /tmp/hyberia_main.log)

- Set whatever script you will use to monitor the status of Projektor
  (The inittab is a good location).

- Enjoy

6) Configuration
----------------

Please see the hyberia.conf for the configuration instruction.

The default location is /etc/hyberia.conf. You can set a different path
in the hyberia_run file (located in /usr/local/bin) but it will break the
daemon. hyberiactl can also be run manually if you also start mplayer manually.

Log file are located in /tmp by default. Be aware that they are deleted at
reboot. You should change that behavior. I wanted to place them in /var
but a regular user doesn't have write access.


7) Reference
------------

Subtitle: http://www.matroska.org/technical/specs/subtitles/ssa.html
Video Container: http://www.matroska.org/node/46

8) Todo
-------

* change behavior to support the .xinitrc setup
