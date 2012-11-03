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

try :
    import markdown
except ImportError :
    markdownsupport = False
else :
    markdownsupport = True

# subclass this and override functions to make your own hooks
# d is a mixture of config and runtime variables
class Hook (object) :

    # called just after hook objects are initialed from config
    # (it's a good idea to use the config hook if you want to do something config-related)
    def start (self, d) :
        pass
    
    # called after configuration validiation 
    # (if you want to validate custom config keys)
    def config (self, d) :
        pass
    
    # called before the templates are read from the disk 
    # (if you want to change the template before it is parsed)
    def template (self, d) :
        pass
    
    ### NOT IMPLEMENTED ###
    # called after the template has been processed for global vars
    # (if you want change the template after it is parsed)
    def posttemplate (self, d) :
        pass
    
    # called just before the pages are looped through 
    # (for changing filenames or something)
    def prepages (self, d) :
        pass
    
    # called before loaded page begins processing/validation
    # (for changing page contents before processing)
    def page (self, d) :
        pass
   
    ### NOT IMPLEMENTED ### 
    # called after page has been processed
    # (if you want to change the end result)
    def postpage (self, d) :
        pass
    
    # called before template is processed for vars (processed page being one of them) 
    # (if you want to modify the template before it is processed)
    def premerge (self, d) :
        pass
    
    # called after template has been processed for local vars
    # (if you want to modify the finished template+page before it is written to the disk
    def postmerge (self, d) :
        pass
    
    # called after all pages have been written to disk and processed
    def postpages (self, d) :
        pass
    
    # called before static files are copied over
    def pretransfer (self, d) : 
        pass
    
    # called after static files are copied over
    def posttransfer (self, d) :
        pass
    
    # called just before the program exits successfully
    def final (self, d) :
        pass

### example hooks ###

class HtaccessIndex (Hook) :
    def postpages (self, d) :
        firstpage = d["pages"][0]["name"]
        # write the data to a .htaccess file in dest 
        open(os.path.join(d["dest"], ".htaccess"), "w").write("DirectoryIndex %s%s\n" % (firstpage, d["newext"]))
    
class Markdown (Hook) :
    def __init__  (self) :
        if not markdownsupport :
            raise Exception("install python(2)-markdown to use the Markdown hook")
            #print >> sys.stderr, "error: please install python-markdown for python 2 to use the Markdown hook"
            #sys.exit(1)

    def page (self, d) :
        d["page"]["content"] = markdown.markdown(d["page"]["content"])

        return d

class Toc (Hook) :
    pass
    
