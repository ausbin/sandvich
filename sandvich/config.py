# sandvich - simple html document generation
# Copyright (C) 2012 Austin Adams
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import re
import yaml
from utils import merge

# i was using some hacky if statement before this, then i realized i'm are idit and regexes are superior
classregex = re.compile(r"(\w+\.)+\w+")

defaults = {
    "name" : "Example name",
    "title" : "%s | Example title",
    "src" : ".",
    "ext" : ".html",
    "dest" : ".",
    "newext" : ".html",
    "templates" : [],
    # XXX should this be None?
    "hooksdir" : "",
    "hooks" : [],
    "pages" : [],
    "flags" : [],
}

class ConfigError (Exception) :
    def __init__ (self, message) :
        super(Exception, self).__init__(message)

# TODO: check that files exist
# TODO: better/prettier/more effective config validation, especially in cases of a container object's type being right but 
#  whatever objects it contains being the wrong type
def validate (cfg) :
    for key, obj in cfg.items() :
        if key in defaults :
            #cfgclass = type(cfg[key])
            cfgclass = type(obj)
            defaultclass = type(defaults[key])

            if cfgclass is not defaultclass :
                cn = lambda x : x.__name__
                raise ConfigError("%s is the wrong type: %s instead of %s" % (key, cn(cfgclass), cn(defaultclass)))

        # other validation
        # check that hook classes are valid (they must be in the form of /(module\.)+class)/
        if key == "hooks" and obj :
            for k in obj :
                if not classregex.match(k) :
                    raise ConfigError("%s is not valid. must be in the form of module.[submodule.anothersubmodule. ...]class" % k)
        # check that directories exist
        elif key in ("src", "dest", "hooksdir") :
            if not os.path.isdir(cfg[key]) :
                raise ConfigError("%s does not exist as a directory!" % cfg[key])

def parse (where) :
    if os.path.exists(where) :
        if not os.path.isfile(where) :
            if os.path.isdir(where) :
                raise IOError("%s is a directory" % where)
            else :
                raise IOError("%s is not a file" % where)
    else : 
        raise IOError("%s does not exist" % where)

    # raw parsed config data
    cfg = yaml.load(open(where).read())

    validate(cfg)

    padded = merge(cfg, defaults)

    return padded

