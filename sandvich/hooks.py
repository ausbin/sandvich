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

from errors import SandvichError

# import modules as we need them (useful because jinja2, for example,
# takes like half a second to load on my box)
def tryimporting (module) :
    if module not in globals() :
        try :
            globals()[module] = __import__(module)
        except ImportError :
            raise SandvichError("module %s is not installed")

# subclass this and override functions to make your own hooks
# d is a mixture of config and runtime variables
class Hook (object) :

    # called just after hook objects are initialed from config
    def start (self, d) :
        pass
    
    # called before the templates are read from the disk 
    # (if you want to change the template before it is parsed)
    def template (self, d) :
        pass
    
    # called before pages are looped through and processed
    # (for changing filenames or something)
    def prepages (self, d) :
        pass

    # called for every page after its path is computed but *before* it's
    # read from disk
    # (useful for gracefully handling pages that don't exist in src but
    #  are specified in config.yml)
    def pageload (self, d) :
        pass
    
    # called before loaded page begins processing/validation
    # (for changing page contents before processing)
    def page (self, d) :
        pass
   
    # called before template is processed for vars (processed page being one of them) 
    # (if you want to modify the template before it is processed)
    def premerge (self, d) :
        pass
    
    # called after template has been processed for local vars
    # (if you want to modify the finished template+page before it is written to the disk)
    def postmerge (self, d) :
        pass

    # called after page has been processed
    # (if you want to change the end result)
    def postpage (self, d) :
        pass
    
    # called after all pages have been written to disk and processed
    def postpages (self, d) :
        pass
    
    # called just before the program exits successfully
    def final (self, d) :
        pass

### example hooks ###

class JinjaTemplates (Hook) :
    def __init__ (self) :
        tryimporting("jinja2")

        # we shouldn't store the given template as a jinja2 Template object
        # the next time templatecall() is called because all sandvich is doing
        # is processing the tags of the page from disk
        # we will cache the object, however, when we are given the text of the
        # template (which is used more than once) after the premerge hook
        self.merge = False    
        self.jtemplate = None

    def templatecall (self, content, d) :
        if self.merge and self.jtemplate :
            template = self.jtemplate
        else :
            template = jinja2.Template(content)

            if self.merge :
                self.jtemplate = template

        return template.render(d)

    def start (self, d) :
        d["templatecall"] = self.templatecall
        return d

    def premerge (self, d) :
        self.merge = True

    def postmerge (self, d) :
        self.merge = False

class Markdown (Hook) :
    def __init__  (self) :
        tryimporting("markdown")

    def page (self, d) :
        d["page"]["content"] = markdown.markdown(d["page"]["content"], extensions=d.get('markdown-extensions', []))

        return d
