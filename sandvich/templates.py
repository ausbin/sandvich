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

import re

# XXX support basic looping and conditionals

# this regex makes me want to stab my eye out with a pencil
valref = r"\s*(#?\w+(\(\))?(\s*[:\.]\s*#?\w+(\(\))?)*)\s*"
valregex = re.compile(r"\{(%(v)s(\s*\|%(v)s)*)\}" % {"v" : valref})
splitregex = re.compile(r"((?P<opts>#)?(?P<name>\w+)(?P<func>\(\))?|[\|\.:#])")

def valsub (match, data) :
    text = match.group(1)
    # it's the past tense form of split. 
    splat = splitregex.finditer(text)
    mode = "getitem"
    parent = data

    for i, match in enumerate(splat) :
        token = match.group(0)

        # if it's an operator
        if i % 2 :
            if token == ":" :
                mode = "getitem"
            elif token == "." :
                mode = "getattr"
            elif token == "|" :
                if parent :
                    break
                else :
                    mode = "getitem"
                    parent = data
        else :
            # if the last value in the chain is empty, then work our way
            # down to the end (or a pipe)
            if not parent :
                continue

            groups = match.groupdict()
            opts = groups["opts"]
            func = groups["func"]
            name = groups["name"]

            if opts and "#" in opts :
                name = int(name)

            if mode == "getitem" :
                try :
                    val = parent[name]
                # XXX support more errors than just those for dicts and lists
                except (IndexError, KeyError) :
                    val = None
            elif mode == "getattr" :
                try :
                    val = getattr(parent, name)
                except AttributeError :
                    val = None

            if val and func :
                val = val()

            parent = val

    result = str(parent) if parent else ""

    return result

def process (victim, data) :
    return valregex.sub(lambda match: valsub(match, data), victim)


