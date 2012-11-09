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
from templates import process

# XXX improve error handling for bad config

defaults = {
    # sane data pool defaults
    "src" : "src"+os.sep,
    "dest" : "dest"+os.sep,
    "newext" : ".html",
    "template" : { "location" : "template.html" },
    "hookobjects" : [],
    "pages" : [],

    # empty values to keep string concats from failing
    "ext" : "",
    "templatedir" : "",
    "templateext" : "",
}

def firehook (d, name) :
    for hook in d["hookobjects"] :
        # XXX if they're subclassing Hook we shouldn't have to do this, right?
        if hasattr(hook, name) :
            dnew = getattr(hook, name)(d)

            if dnew is not None :
                d = dnew
    return d

def build (d = {}) :
    # apply default values to the data pool
    defd = defaults.copy()
    defd.update(d)
    d = defd

    # HOOK: start
    d = firehook(d, "start")
    
    # HOOK: template
    d = firehook(d, "template")

    if "content" not in d["template"] :
        if "location" not in d["template"] :
            path = d["templatedir"]+d["template"]["name"]+d["templateext"]
            d["template"]["location"] = path

        d["template"]["content"] = open(d["template"]["location"]).read()
    
    # HOOK: prepages 
    d = firehook(d, "prepages")

    for p in d["pages"] :
        d["page"] = p
        # XXX nextpage and lastpage?

        if "content" not in d["page"] :
            if "location" not in d["page"] :
                d["page"]["location"]  = d["src"]+d["page"]["name"]+d["ext"]

            d["page"]["content"] = open(d["page"]["location"]).read()

        # HOOK: page 
        d = firehook(d, "page")

        # process this page
        d["page"]["content"] = process(d["page"]["content"], d)

        # HOOK: premerge
        d = firehook(d, "premerge")

        d["page"]["content"] = process(d["template"]["content"], d)

        # HOOK: postmerge
        d = firehook(d, "postmerge")

        if "destination" not in d["page"] :
            d["page"]["destination"]  = d["dest"]+d["page"]["name"]+d["newext"]

        # write the finished page to its destination
        open(d["page"]["destination"], "w").write(d["page"]["content"])

        # HOOK: postpage 
        d = firehook(d, "postpage")

    # HOOK: postpages 
    d = firehook(d, "postpages")

    # HOOK: final 
    d = firehook(d, "final")
    
