#!/usr/bin/python -u

"""Module for reading the TinyG config.

"""

from __future__ import print_function

import argparse
from argparse import RawDescriptionHelpFormatter
import json
import re
import serial
import sys
import time

CONFIG_STR = {
    'sys' : (
        ( 'fb',     'firmware build',               '{:.2f}' ),
        ( 'fv',     'firmware version',             '{:.2f}' ),
        ( 'hp',     'hardware platform',            '{:.2f}' ),
        ( 'hv',     'hardware version',             '{:.2f}' ),
        ( 'id',     'TinyG ID',                     '{}' ),
        ( 'ja',     'junction acceleration',        '{:d} mm' ),
        ( 'ct',     'chordal tolerance',            '{:.4f} mm' ),
        ( 'sl',     'soft limit enable',            '{:d}' ),
        ( 'st',     'switch type',                  '{:d} [0=NO,1=NC]' ),
        ( 'mt',     'motor idle timeout',           '{:.2f} Sec' ),
        ( 'ej',     'enable json mode',             '{:d} [0=text,1=JSON]' ),
        ( 'jv',     'json verbosity',               '{:d} [0=silent,1=footer,2=messages,3=configs,4=linenum,5=verbose]' ),
        ( 'js',     'json serialize style',         '{:d} [0=relaxed,1=strict]' ),
        ( 'tv',     'text verbosity',               '{:d} [0=silent,1=verbose]' ),
        ( 'qv',     'queue report verbosity',       '{:d} [0=off,1=single,2=triple]' ),
        ( 'sv',     'status report verbosity',      '{:d} [0=off,1=filtered,2=verbose]' ),
        ( 'si',     'status interval',              '{:d} ms' ),
        ( 'ec',     'expand LF to CRLF on TX',      '{:d} [0=off,1=on]' ),
        ( 'ee',     'enable echo',                  '{:d} [0=off,1=on]' ),
        ( 'ex',     'enable flow control',          '{:d} [0=off,1=XON/XOFF, 2=RTS/CTS]' ),
        ( 'baud',   'USB baud rate',                '{:d} [1=9600,2=19200,3=38400,4=57600,5=115200,6=230400]' ),
        ( 'net',    'network mode',                 '{:d} [0=master]' ),
        ( 'gpl',    'default gcode plane',          '{:d} [0=G17,1=G18,2=G19]' ),
        ( 'gun',    'default gcode units mode',     '{:d} [0=G20,1=G21]' ),
        ( 'gco',    'default gcode coord system',   '{:d} [1-6 (G54-G59)]' ),
        ( 'gpa',    'default gcode path control',   '{:d} [0=G61,1=G61.1,2=G64]' ),
        ( 'gdi',    'default gcode distance mode',  '{:d} [0=G90,1=G91]' ),
    ),

    '1' : (
        ( 'ma',     'map to axis',                  '{:d} [0=X,1=Y,2=Z...]' ),
        ( 'sa',     'step angle',                   '{:.3f} deg' ),
        ( 'tr',     'travel per revolution',        '{:.4f} mm' ),
        ( 'mi',     'microsteps',                   '{:d} [1,2,4,8]' ),
        ( 'po',     'polarity',                     '{:d} [0=normal,1=reverse]' ),
        ( 'pm',     'power management',             '{:d} [0=disabled,1=always on,2=in cycle,3=when moving]' ),
    ),

    'x' : (
        ( 'am',     'axis mode',                    '{:d} [standard]' ),
        ( 'vm',     'velocity maximum',             '{:d} mm/min' ),
        ( 'fr',     'feedrate maximum',             '{:d} mm/min' ),
        ( 'tn',     'travel minimum',               '{:.3f} mm' ),
        ( 'tm',     'travel maximum',               '{:.3f} mm' ),
        ( 'jm',     'jerk maximum',                 '{:d} mm/min^3 * 1 million' ),
        ( 'jh',     'jerk homing',                  '{:d} mm/min^3 * 1 million' ),
        ( 'jd',     'junction deviation',           '{:.4f} mm (larger is faster)' ),
        ( 'sn',     'switch min',                   '{:d} [0=off,1=homing,2=limit,3=limit+homing]' ),
        ( 'sx',     'switch max',                   '{:d} [0=off,1=homing,2=limit,3=limit+homing]' ),
        ( 'sv',     'search velocity',              '{:d} mm/min' ),
        ( 'lv',     'latch velocity',               '{:d} mm/min' ),
        ( 'lb',     'latch backoff',                '{:.3f} mm' ),
        ( 'zb',     'zero backoff',                 '{:.3f} mm' ),
    ),

    'a' : (
        ( 'am',     'axis mode',                    '{:d} [radius]' ),
        ( 'vm',     'velocity maximum',             '{:d} deg/min' ),
        ( 'fr',     'feedrate maximum',             '{:d} deg/min' ),
        ( 'tn',     'travel minimum',               '{:.3f} deg' ),
        ( 'tm',     'travel maximum',               '{:.3f} deg' ),
        ( 'jm',     'jerk maximum',                 '{:d} deg/min^3 * 1 million' ),
        ( 'jh',     'jerk homing',                  '{:d} deg/min^3 * 1 million' ),
        ( 'jd',     'junction deviation',           '{:.4f} deg (larger is faster)' ),
        ( 'ra',     'radius value',                 '{:.4f} deg' ),

        ( 'sn',    'switch min',                   '{:d} [0=off,1=homing,2=limit,3=limit+homing]' ),
        ( 'sx',    'switch max',                   '{:d} [0=off,1=homing,2=limit,3=limit+homing]' ),
        ( 'sv',    'search velocity',              '{:d} deg/min' ),
        ( 'lv',    'latch velocity',               '{:d} deg/min' ),
        ( 'lb',    'latch backoff',                '{:.3f} deg' ),
        ( 'zb',    'zero backoff',                 '{:.3f} deg' ),
    ),

    'p': (
        ( 'frq',    'pwm frequency',                '{:d} Hz' ),
        ( 'csl',    'pwm cw speed lo',              '{:d} RPM' ),
        ( 'csh',    'pwm cw speed hi',              '{:d} RPM' ),
        ( 'cpl',    'pwm cw phase lo',              '{:.3f} [0..1]' ),
        ( 'cph',    'pwm cw phase hi',              '{:.3f} [0..1]' ),
        ( 'wsl',    'pwm ccw speed lo',             '{:d} RPM' ),
        ( 'wsh',    'pwm ccw speed hi',             '{:d} RPM' ),
        ( 'wpl',    'pwm ccw phase lo',             '{:.3f} [0..1]' ),
        ( 'wph',    'pwm ccw phase hi',             '{:.3f} [0..1]' ),
        ( 'pof',    'pwm phase off',                '{:.3f} [0..1]' ),
    ),

    'g': (
        ( 'x',      'x offset',                     '{:.3f} mm' ),
        ( 'y',      'y offset',                     '{:.3f} mm' ),
        ( 'z',      'z offset',                     '{:.3f} mm' ),
        ( 'a',      'a offset',                     '{:.3f} deg' ),
        ( 'b',      'b offset',                     '{:.3f} deg' ),
        ( 'c',      'c offset',                     '{:.3f} deg' ),
    ),

    'h': (
        ( 'x',      'x position',                   '{:.3f} mm' ),
        ( 'y',      'y position',                   '{:.3f} mm' ),
        ( 'z',      'z position',                   '{:.3f} mm' ),
        ( 'a',      'a position',                   '{:.3f} deg' ),
        ( 'b',      'b position',                   '{:.3f} deg' ),
        ( 'c',      'c position',                   '{:.3f} deg' ),
    ),
}

CONFIG_MAP  = (
    ('sys', 'sys'),
    ('1',   '1'), 
    ('2',   '1'),
    ('3',   '1'),
    ('4',   '1'),
    ('x',   'x'),
    ('y',   'x'),
    ('z',   'x'),
    ('a',   'a'),
    ('b',   'a'),
    ('c',   'a'),
    ('p1',  'p'),
    ('g54', 'g'),
    ('g55', 'g'),
    ('g56', 'g'),
    ('g57', 'g'),
    ('g58', 'g'),
    ('g59', 'g'),
    ('g92', 'g'),
    ('g28', 'h'),
    ('g30', 'h'),
)

# Put baud in the read-only list. We don't support changing it on the fly.
CONFIG_READ_ONLY = { "sys" : { 'fb', 'fv', 'hp', 'hv', 'id', 'baud' }}

AXIS_MODE = ['[disabled]', '[standard]', '[inhibited]', '[radius]']

def is_number(s):
    """Determines if a string looks like a number or not."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_val(val_str):
    """Converts a string into a, integer, float, or string."""
    try:
        val = int(val_str)
        return val
    except ValueError:
        try:
            val = float(val_str)
            return val
        except ValueError:
            return val_str

def get_group_strs(group_id):
    """Returns the group strings for the indicated group_id."""
    for mapEntry in CONFIG_MAP:
        if mapEntry[0] == group_id:
            return CONFIG_STR[mapEntry[1]]

def is_id_in_group(id, group_id):
    """Scans the indicated group array, and returns True if the id is
       found, False, otherwise."""
    group_strs = get_group_strs(group_id)
    for entry in group_strs:
        if entry[0] == id:
            return True
    return False

def id_to_group_key(id):
    """Converts a key from the text output into a (group, key) tuple."""
    # Check to see if the ey exists in the sys group
    if is_id_in_group(id, 'sys'):
        return ('sys', id)
    for mapEntry in CONFIG_MAP:
        group_id = mapEntry[0]
        if id.startswith(group_id):
            group_key = id[len(group_id):]
            if is_id_in_group(group_key, group_id):
                return (group_id, group_key)


class Config(object):
    """This class holds the TinyG configuration data in a 2 level dictionary.
       In the top level, the key is a string containing the group_id
       (i.e. "sys", "x", etc)
    """

    def __init__(self, verbose=False):
        self.config = {}
        self.verbose = verbose

    def dump(self):
        """Dumps the contents of the confuration using JSON, with a bit more
           formatting than raw JSON (keys are sorted).
        """
        print(json.dumps(self.config, indent=2, sort_keys=True))

    def dump_formatted(self):
        """Dumps the contents of the configuration using the text output
           that TinyG produces. This will be almost identical to the output
           produced by the $$ command in TinyG.
        """
        for mapEntry in CONFIG_MAP:
            prefix = mapEntry[0]
            if prefix not in self.config:
                continue
            vals = self.config[prefix]
            mapPrefix = mapEntry[1]
            strs = CONFIG_STR[mapPrefix]
            for strEntry in strs:
                key = strEntry[0]
                if key in vals:
                    descr = strEntry[1]
                    if mapPrefix == '1':
                        descr = 'm{:s} {:s}'.format(prefix, descr)
                    elif mapPrefix in 'xagh':
                        descr = '{:s} {:s}'.format(prefix, descr)
                    units = strEntry[2]
                    if prefix == 'sys':
                        fmt_key = '[' + key + ']'
                    else:
                        fmt_key = '[' + prefix + key + ']'
                    val = vals[key]
                    if key == "am":
                        units = '{{:d}} {:s}'.format(AXIS_MODE[val])
                    left = '{:5s} {:29s}'.format(fmt_key, descr)[:35]
                    right = units.format(val)
                    space = right.find(' ')
                    period = right.find('.')
                    align = space
                    if period > 0 and ((space < 0) or (space > 0 and period < space)):
                        align = period
                    if align < 0:
                        align = 1
                    #print("space =", space, "period =", period, "align =",  align)
                    print(left[:-(align + 1)] + ' ' + right)

    def add_group(self, group_dict):
        """Merges a set of parameters described by group_dict, into the
           configuration.
        """
        # self.config is a dictionary of groups, and each group is itself
        # a dictionary. So we can't call update on the top level (it doesn't
        # update recursively). We walk the top level ourselves.
        for key in group_dict:
            if key in self.config:
                self.config[key].update(group_dict[key])
            else:
                self.config[key] = group_dict[key]

    def get_group(self, group_id):
        """Returns the configuration items which belong to the group named
           by group_id.
        """
        if group_id in self.config:
            return self.config[group_id].copy()

    def read(self, file):
        """Checks to see if the first character is '{". If so, it considers
           this to be a JSON file. otherwise it assumes it's a text format.
        """
        lines = file.readlines()
        if lines and lines[0] and lines[0][0] != '{':
            if self.verbose:
                print("Looks like a TEXT file")
            self.read_text(lines)
            return
        if self.verbose:
            print("Looks like a JSON file")
        cfg_dict = json.loads(' '.join(lines))
        for key in cfg_dict:
            if self.verbose:
                print('JSON:', key, ':', json.dumps(cfg_dict[key]))
            self.add_group({key : cfg_dict[key]})

    def read_text(self, lines):
        """Parses a text file which contains lines produced by TinyG's $$
           command in text mode.
        """
        for line in lines:
            if line[0] != '[':
                continue
            line = line.strip()
            fields = line.split()
            key = re.search(r'\[(.*)\]', fields[0]).group(1)
            val_str = None
            if key == 'id':
                # id is the only non-numeric field
                val_str = fields[3]
            else:
                for field in fields[1:]:
                    if is_number(field):
                        val_str = field
                        break
            if self.verbose:
                print("Parsed key '%s' val '%s'" % (key,  val_str))
            (group_id, group_key) = id_to_group_key(key)
            self.add_group({group_id : {group_key : get_val(val_str)}})

    def write(self, file):
        """Writes the configuration out as a JSON file.
        """
        file.write(json.dumps(self.config))
        file.write('\n')


class TinyG(object):
    """Class for talking to the TinyG. Currently this is just a hacked
       together class. Eventually, I'll split this into a Bus style class
       which has classes for talking serial, SPJS, and some type of simulation.
    """

    def __init__(self, verbose=False):
        self.serial_port = None
        self.verbose = verbose

    def open_serial(self, port_name, baud):
        """Opens the serial port for communicating with the TinyG board.
        """
        if self.serial_port:
            # Already open
            return
        try:
            self.serial_port = serial.Serial(port=port_name,
                                             baudrate=baud,
                                             timeout=1, # seconds
                                             bytesize=serial.EIGHTBITS,
                                             parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE,
                                             xonxoff=False,
                                             rtscts=False,
                                             dsrdtr=False)
        except serial.serialutil.SerialException:
            raise IOError("Unable to open port '%s'\r" % port_name)
        # Make sure that we're in metric mode.
        self.send_json({'gc' : 'G21'})
        self.read_response()

    def send_line(self, line):
        self.serial_port.write(line.encode('ascii'))
        self.serial_port.write(b'\n')
        if self.verbose:
            print("Sent: '%s'" % line)

    def send_json(self, cmd_dict):
        """Formats 'cmd_dict' as JSON, and sends it over the serial port to
           the TinyG.
        """
        self.send_line(json.dumps(cmd_dict))

    def recv_json(self):
        """Reads a line of data from the TinyG and decodes is as JSON. Returns
           the parsed dictionay.
        """
        line = self.serial_port.readline(512).decode('ascii')
        if line:
            if self.verbose:
                print("Rcvd: '%s'" % line.strip())
            return json.loads(line)
        print("Timed out")

    def read_response(self):
        """Reads lines from the TinyG until it gets one which contains a
           response.
        """
        # We need the while loop because sometimes we get 'sr' style
        # responses as well.
        while True:
            response = self.recv_json()
            if not response:
                # We timed out
                return None
            if 'r' in response:
                return response['r']

    def read_config(self, config):
        """Reads the configuration from the TinyG and merges it into the
           configuration object given by 'config'.
        """
        for mapEntry in CONFIG_MAP:
            group = mapEntry[0]
            self.send_json({group:None})
            response = self.read_response()
            if response:
                config.add_group(response)

    def write_config(self, config):
        """Writes the configuration object given by 'config' to the TinyG.
           This will break the configuration up into sendable chunks.
        """
        for mapEntry in CONFIG_MAP:
            group_id = mapEntry[0]
            group_config = config.get_group(group_id)
            if not group_config:
                continue
            # Remove any read-only configs
            filtered_config = group_config.copy()
            if group_id in CONFIG_READ_ONLY:
                for ro_key in CONFIG_READ_ONLY[group_id]:
                    if ro_key in filtered_config:
                        del filtered_config[ro_key]
            # We only write 10 parameters at a time to ensure that we don't
            # exceed the 254 character line length
            # Python3 dict.keys returns a view (rather than a list), which is
            # not sliceable.
            filtered_keys = list(filtered_config.keys())
            while filtered_keys:
                key_slice = filtered_keys[:10]
                del filtered_keys[:10]
                self.send_json({group_id:{key : filtered_config[key] for key in key_slice}})
                response = self.read_response()
                if not response:
                    print("Write of group config '%s' failed" % group)
                    break


def main():
    """The main program."""
    default_baud = 115200
    default_port = '/dev/ttyUSB0'
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] command [filename]",
        description="Archives, restores, or shows the TinyG configuration\n"
        "  archive - retrieves the configuration from the TinyG and stores it in a file\n"
        "  restore - reads a configuration file and writes it to the TinyG\n"
        "  show    - displays the TinyG configuration, or the configuration from a file",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-b", "--baud",
        dest="baud",
        action="store",
        type=int,
        help="Set the baudrate used (default = %d)" % default_baud,
        default=default_baud
    )
    parser.add_argument(
        "-p", "--port",
        dest="port",
        action="store",
        type=str,
        help="Set the port used (default = %s)" % default_port,
        default=default_port
    )
    parser.add_argument(
        "-v", "--verbose",
        dest="verbose",
        action="store_true",
        help="Turn on verbose messages",
        default=False
    )
    parser.add_argument(
        "cmd",
        help="Command (one of archive, restore, or show)"
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="Filename to use (optional for show command)"
    )
    args = parser.parse_args(sys.argv[1:])
    if args.verbose:
        print("baud port: %s" % args.port)
        print("baud rate: %d" % args.baud)
        print("cmd = '%s'" % args.cmd)
        if args.filename:
            print("filename = '%s'" % args.filename)

    config = Config(verbose=args.verbose)
    tinyg = TinyG(verbose=args.verbose)

    if args.cmd == 'archive':

        filename = args.filename
        if not filename:
            filename = time.strftime('TinyG-%Y%m%d-%H%M%S.config')
            print("Writing TinyG configuration into", filename)
        tinyg.open_serial(args.port, args.baud)
        tinyg.read_config(config)
        with open(filename, 'w') as file:
            config.write(file)

    elif args.cmd == 'dump':

        if args.filename:
            with open(args.filename, 'r') as file:
                config.read(file)
        else:
            tinyg.open_serial(args.port, args.baud)
            tinyg.read_config(config)
        config.dump()

    elif args.cmd == 'restore':

        if not args.filename:
            print("restore command needs the name of a file to read the configuration from")
            return

        with open(args.filename, 'r') as file:
            config.read(file)
        tinyg.open_serial(args.port, args.baud)
        tinyg.write_config(config)

    elif args.cmd == 'show':

        if args.filename:
            with open(args.filename, 'r') as file:
                config.read(file)
        else:
            tinyg.open_serial(args.port, args.baud)
            tinyg.read_config(config)
        config.dump_formatted()

    else:
        print("Unrecognied command '%s'" % args.cmd)
        return


if __name__ == "__main__":
    main()
