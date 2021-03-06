# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import sys
import json
import os.path
import logging

log = logging.getLogger("config")


# --------------------------------------------------------------------
# public interface

def load(*files, format="json", strict=False):
    """Load JSON configuration files"""
    configfiles = files or _default_configs

    if format == "yaml":
        try:
            import yaml
            parsefunc = yaml.safe_load
        except ImportError:
            log.error("Could not import 'yaml' module")
            return
    else:
        parsefunc = json.load

    for conf in configfiles:
        try:
            path = os.path.expanduser(os.path.expandvars(conf))
            with open(path) as file:
                confdict = parsefunc(file)
            _config.update(confdict)
        except FileNotFoundError:
            if strict:
                log.error("Configuration file '%s' not found", path)
                sys.exit(1)
        except Exception as exception:
            log.warning("Could not parse '%s'", path)
            log.warning(exception)
            if strict:
                sys.exit(2)


def clear():
    """Reset configuration to en empty state"""
    globals()["_config"] = {}


def get(keys, default=None):
    """Get the value of property 'key' or a default-value if it doenst exist"""
    conf = _config
    try:
        for k in keys:
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def interpolate(keys, default=None):
    """Interpolate the value of 'key'"""
    conf = _config
    try:
        for k in keys:
            default = conf.get(keys[-1], default)
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def set(keys, value):
    """Set the value of property 'key' for this session"""
    conf = _config
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    conf[keys[-1]] = value


def setdefault(keys, value):
    """Set the value of property 'key' if it doesn't exist"""
    conf = _config
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    return conf.setdefault(keys[-1], value)


# --------------------------------------------------------------------
# internals

_config = {}

if os.name == "nt":
    _default_configs = [
        r"~\.config\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl\config.json",
        r"~\.gallery-dl.conf",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${HOME}/.config/gallery/config.json",
        "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]
