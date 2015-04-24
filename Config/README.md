Config.py is a utility for archiving, restoring, and examining the configuration
stored on a TinyG board.

#Options (must be specified before the command)

##-h

Displays help information.

##-p port

The -p option specifies the port to use when communicating with the TinyG. If
no port is specified, then /dev/ttyUSB0 will be used.

##-b baud

The -b option specifies the baud rate to use when communicating with the TinyG.
If no baud is specified then 115200 will be used.

##-v

The -v option causes verbose information to be printed during the parsing of
configuration files and communicating with the TinyG.

#Commands

##archive [filename]

The archive command will download the configuration from the TinyG board and
store it in JSON format in a file on your host computer. If you don't provide
a filename, then a filename of the format TinyG-YYYYMMDD-HHMMSS.config will be
used.

##restore filename

The restore command will read a configuration file from your host computer and
send the appropriate commands to the TinyG to set its configuration to match.

The filename may be either a JSON style file produced by the archive command,
or it will also accept a text file with output produced by using the $$ command
in TinyG.

Note that the configuration file provided doesn't need to be a complete
configuration file. It might provide just configuration information for the
spindle, or perhaps just a single axis, or whatever combination of things
you might want to set.

##dump [filename]

The dump command will read a configuration file from your host computer (if a
filename was provided), or read the configuration from your TinyG (if no
filename was provided) and display it in a formatted JSON format. More
specifically it will print the output of json.dumps() using indent=2.

Snippet of output produced by the dump command:
```
> ./Config.py dump TinyG-20150423-135312.config 
{
  "1": {
    "ma": 0, 
    "mi": 8, 
    "pm": 2, 
    "po": 1, 
    "sa": 1.8, 
    "tr": 40.0
  }, 
...
```

##show [filename]

The dump command will read a configuration file from your host computer (if a
filename was provided), or read the configuration from your TinyG (if no
filename was provided) and display it in a manner similar to the $$ command.

Snippet of output produced by the show command:
```
> ./Config.py show TinyG-20150423-135312.config 
[fb]  firmware build            440.14
[fv]  firmware version            0.97
[hp]  hardware platform           1.00
[hv]  hardware version            8.00
...
```
#Typical Usage

I wrote this so that I could preserve my TinyG configuration when upgrading
the firmware. When you upgrade the firmware it resets everything back to
factory defaults.

Steps to upgrade your firmware and preserve your settings:

##Archive (backup) your old configuration
```
Config.py archive old.config
```
##Upgrade your firmware
Use the TinyG updater app, or avrdude for linux. See: https://github.com/synthetos/TinyG/wiki/TinyG-Updating-Firmware
##Restore your old configuration
Use the name from the archive step.
```
Config.py restore old.config
```
##Re-archive your new configuration
```
Config.py archive new.config
```
##Compare the old and new configurations
```
Config.py dump old.config > old.dump
Config.py dump new.config > new.dump
diff old.dump new.dump
```
Use the comparison tool of your choice, `diff` is just an example. I normally
use a GUI tool called `meld` from http://meldmerge.org/

#Configuration File Format

The configuration information is stored using JSON format. It will look like
a dictionary containing groups, and each group will contain the configuration
parameters for that group.

The raw JSON file will be on a single line.

You can read it into memory using the following python snippet (in case you
feel like writing some code to manipulate it):
```python
import json
with open('TinyG.config', 'r') as file:
    config = json.load(file)
```

The TinyG-20150423-135312.config file included in this directory is my
configuration file stored using the archive command.
