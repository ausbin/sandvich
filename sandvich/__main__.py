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
from utils import merge
from shutil import copytree
from templates import process
from collections import namedtuple
from config import parse, ConfigError

# exit codes:
# 0 -> success
# 1 -> general failure
# 2 -> commmand line syntax error
# 3 -> configuration error

# XXX replace sys.exit calls with exceptions subclassing SystemExit
# XXX: THIS ****SUCKS****. global variables are an atrocity! do something else!
d = {}

# create a convenience function for firing hooks
def hook (hookname) :
    global d

    for hook in d["hookobjects"] :
        returned = getattr(hook, hookname)(d) 
        
        if returned is not None :
            d = returned

def init (where=None) :
    print "not implemented. try cp -r repo/skel yourdir"
    pass

def build (where=None, template=None) :
    global d

    if where :
        d["home"] = where
    else :
        d["home"] = "."

    # XXX do this in the config parser instead?
    # simple function to find a path relative to d["home"] if it isn't absolute
    homerel = lambda x : x if os.path.isabs(x) else os.path.join(d["home"], x)

    cfgfile = os.path.join(d["home"], "config.yml")

    try :
        cfg = parse(cfgfile)
    except ConfigError as e :
        print >> sys.stderr, "configuration error: " + e.message
        sys.exit(3)

    d = merge(d, cfg)

    d["hooksdir"] = homerel(d["hooksdir"])

    # TODO: check more thoroughly that hooksdir isn't already in pythonpath
    if d["hooksdir"] and d["hooksdir"] not in sys.path : 
        sys.path.append(d["hooksdir"]) 

    # create a list of empty values
    d["hookobjects"] = [None] * len(d["hooks"])

    # this is so cool
    if d["hooks"] :
        imports = {} 
        ClassItem = namedtuple("ClassItem", ["name", "index"])

        # assemble the dictionary of modules and classes
        for i, h in enumerate(d["hooks"]) :
            modulename, classname = h.rsplit(".", 1)
            # should be fixed
            # FIXME: classes are in the right order within modules, but not globally. example:
            #
            #   # RIGHT! stored as { "module" : ["class", "otherclass"], "othermodule" : ["class"] }
            #   hooks :  
            #   - module.class
            #   - module.otherclass
            #   - othermodule.class
            #
            #   # WRONG! still stored as { "module" : ["class", "otherclass"], "othermodule" : ["class"] }
            #   hooks :  
            #   - module.class
            #   - othermodule.class
            #   - module.otherclass
            #
            #  this is important because it could break the delicate order in which hooks execute (html modification
            #  should occur after markdown processing, for example). this could be fixed by simply adding the
            #  class objects into d["hookobjects"] in the order they occur in config.yml
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
                    print >> sys.stderr, "error: the module %s does not contain a class named %s" % (modulename, classname)
                    sys.exit(3)
                
                d["hookobjects"][item.index] = obj

    # HOOK: start
    hook("start")

    # HOOK: config 
    hook("config")

    # HOOK: template
    hook("template")

    if template :
        for t in d["templates"] :
            if t["name"] == template :
                d["template"] = t
                break
        else :
            print >> sys.stderr, "error: there is no template named %s" % template
            sys.exit(2)
    else :
        d["template"] = d["templates"][0]
  
    d["template"]["location"] = homerel(d["template"]["location"]) 
    
    if not os.path.isfile(d["template"]["location"]) :
        print >> sys.stderr, "error: the template %s does not exist as a file at %s" % (d["template"]["name"], d["template"]["location"])
        sys.exit(3)

    d["template"]["content"] = open(d["template"]["location"]).read() 

    # HOOK: prepages
    hook("prepages")
    
    d["src"] = homerel(d["src"])

    for i, p in enumerate(d["pages"]) :
        pageloc = os.path.join(d["src"], p["name"]+d["ext"])

        if not os.path.isfile(pageloc) :
            print >> sys.stderr, "error: page %s does not exist as a file at %s" % (p["name"], pageloc)
            sys.exit(3)

        p["content"] = open(pageloc).read()

        d["page"] = p
        d["nextpage"] = d["pages"][i+1] if i+1 < len(d["pages"]) else None
        d["prevpage"] = d["pages"][i-1] if i-1 > -1 else None

        # HOOK: page
        hook("page")
       
        # process code in page 
        d["page"]["content"] = process(d["page"]["content"], d)

        # HOOK: merge
        hook("premerge")

        # merge template and page
        d["page"]["content"] = process(d["template"]["content"], d)

        # HOOK: postmerge
        hook("postmerge")

        destination = os.path.join(d["dest"], p["name"]+d["newext"])

        if os.path.exists(destination) :
            print >> sys.stderr, "error: destination file for %s (%s) exists!" % (d["name"], destination)

            sys.exit(1)

        open(destination, "w").write(d["page"]["content"])

    # HOOK: postpages
    hook("postpages")

    # let clients implement this themselves in their own skel/build
    # HOOK: pretransfer
    #hook("pretransfer")
   
    #if "transfer" in d : 
    #    for directory in d["transfer"] :
    #        name = homerel(os.path.split(directory)[-1])

    #        dest = os.path.join(d["dest"], name)

    #        if os.path.exists(dest) :
    #            print >> sys.stderr, "can't transfer %s because something already exists at %s!" % (name, dest)
    #            sys.exit(3)
    #        if not os.path.isdir(directory) :
    #            print >> sys.stderr, "can't transfer %s because it's not a directory" % name
    #            sys.exit(3)
    #        else :    
    #            copytree(directory, dest, True)

    # HOOK: posttransfer
    #hook("posttransfer")

    # HOOK: final
    hook("final")

# XXX should we be doing a more efficient argument parsing procedure? 
def main () :
    args = sys.argv[1:]
    command = None
    subargs = []

    if not len(args) :
        print >> sys.stderr, "you didn't specify any arguments. try `-h`"
        sys.exit(2)
    else :
        command = args[0]
        subargs = args[1:]

    if command in ("-h", "--help", "help") :
        # TODO: add a help message that isn't worthless
        print "NO HELP FOR YOU"
    elif command == "build" :
        template = None
        where = None

        argcount = len(subargs)

        if argcount > 2 :
            print >> sys.stderr, "too many args for build! (%s > 2)" % len(subargs)
            sys.exit(2)

        if argcount >= 1 :
            template = subargs[0]
        if argcount >= 2 :
            where = subargs[1]

        #print where,template
        #return

        build(where, template)
    elif command == "init" : 
        where = None

        if len(subargs) > 1 :
            print >> sys.stderr, "too many args for init! (%s > 1)" % len(subargs)
            sys.exit(2)
        elif len(subargs) == 1 :
            where = subargs[0]

        init(where)
    else :
        print >> sys.stderr, "unknown subcommmand: %s" % command
        sys.exit(2)
            

if __name__ == "__main__" : 
    main()

