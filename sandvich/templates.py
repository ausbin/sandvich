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

# syntax for templates (simple yet effective!):
#
# to insert a value into the document use brackets containing the name of the value. for a value named "muffin":
#  { muffin }
#
# that will convert the value of "muffin" into a string and insert it into the html verbatim (no escaping). 
#
# if "muffin" is a dictionary and we want to insert the value of the "color" key:
#  { muffin : color }
#
# in essence, the colon is your path to __getitem__!
#
# however, if you try to access a member of a list with the colon, it won't work because you can't access
# list items with strings containing digits. solution? the pound (#).
#  { muffin # 0 }
# 
# pound works the same as the colon except that it converts what follows it to a int. you can use it with
# a dict too if you're accessing an item with a key that is an integer. 
#
# if "muffin['color']" is a list and we want whatever is at the third indice:
#  { muffin : color # 3 }
# 
# if we want to get a property of one of the items, use a dot:
#  { muffin : color # 3 . alpha }
# 
# if the property is callable, whatever it returns will be placed in the document instead of itself:
#  { muffin : color # 3 . getalpha }
# 
# all this value retrieval is great, but if we want some logic we use a pipe. if the value before the pipe
# is empty, the second value is inserted istead. you can stack these for some uber-1337 templates. example:
#  { muffin : color # 3 . getalpha | defaults : alpha  }
#
# another example:
#  <div class="muffins">
#     <a href="google.com/muffin/color/{muffin:color|defaults:color}">click</a>
#  </div>

valref = r"\s*(\w+(\s*[:\.#]\s*\w+)*)\s*"
valregex = re.compile(r"\{(%(v)s(\s*\|%(v)s)*)\}" % {"v" : valref})
splitregex = re.compile(r"(\w+|[\|\.:#])")

def valsub (match, data) :
    text = match.group(1)
    # it's the past tense form of split. 
    splat = splitregex.findall(text)
    mode = "getitem"
    parent = data

    for i, token in enumerate(splat) :
        print mode, "d" if parent == data else parent, token
        # if it's an operator
        if i % 2 :
            if token == ":" :
                mode = "getitem"
            elif token == "#" :
                mode = "intgetitem"
            elif token == "." :
                mode = "getattr"
            elif token == "|" :
                if parent :
                    break
                else :
                    mode = "getitem"
                    parent = data

        else :
            if not parent :
                continue

            if mode in ("getitem", "intgetitem") :
                index = token

                if mode == "intgetitem" :
                    index = int(index)

                try :
                    val = parent[index]
                # XXX support more errors than just those for dicts and lists
                except (IndexError, KeyError) :
                    val = None
            elif mode == "getattr" :
                try :
                    val = getattr(parent, token)
                except AttributeError :
                    val = None
                else :
                    if callable(val) :
                        # XXX should we be catching errors here? probably not
                        val = val()

            parent = val

    result = str(parent) if parent else ""

    print "done: "+result
    print

    return result

def process (victim, data) :
    return valregex.sub(lambda match: valsub(match, data), victim)


