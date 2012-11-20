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
import sys
import core
import yaml
from templates import process
from collections import namedtuple
from errors import SandvichError, DataPoolError, ArgError

def inithooks (hooks) :
    hookobjects = [None] * len(hooks)
    imports = {} 
    ClassItem = namedtuple("ClassItem", ["name", "index"])

    # assemble the dictionary of modules and classes
    for i, h in enumerate(hooks) :
        modulename, classname = h.rsplit(".", 1)

        item = ClassItem(classname, i)

        if modulename in imports and classname not in imports[modulename]:
            imports[modulename].append(item)
        else :
            imports[modulename] = [item]

    for modulename in imports :
        module = __import__(modulename, fromlist=imports[modulename])

        for item in imports[modulename] :
            classname = item.name

            try :
                obj = getattr(module, classname)()
            except AttributeError :
                raise DataPoolError("the module %s does not contain a class named %s" % (modulename, classname))
            
            hookobjects[item.index] = obj

    return hookobjects

def build (where=None) :
    d = {}
    
    if where :
        os.chdir(where)

    # XXX get this to be configurable somehow(?)
    cfgfile = "config.yml"

    if os.path.isfile(cfgfile) :
        cfg = yaml.load(open(cfgfile).read())

        # initialize hook objects
        if cfg["hooks"] :
            if "hooksdir" in cfg and cfg["hooksdir"] :
                sys.path.insert(0, cfg["hooksdir"])
                
            cfg["hookobjects"] = inithooks(cfg["hooks"])

        d.update(cfg)

    core.build(d)

# XXX use better argument parsing procedure
def main () :
    args = sys.argv[1:]
    command = None
    subargs = []

    if not len(args) :
        raise ArgError("you didn't specify any arguments. try `-h`")
    else :
        command = args[0]
        subargs = args[1:]

    if command in ("-h", "--help", "help") :
        print "usage: sandvich build [location]"
    elif command == "build" :
        where = None

        argcount = len(subargs)

        if argcount > 1 :
            raise ArgError("too many args for build! (%s > 2)" % len(subargs))
        elif argcount == 1 :
            where = subargs[1]

        build(where)
    else :
        raise ArgError("unknown subcommmand: %s" % command)
            

if __name__ == "__main__" : 
    try :
        main()
    except SandvichError as e :
        if e.message :
            print >>sys.stderr, "%s error: %s" % (e.desc, e.message)

        sys.exit(e.exitcode)

