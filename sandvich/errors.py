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

class SandvichError (Exception) :
    desc = "general"
    exitcode = 1

# mainly used in __main__
class ArgError (SandvichError) :
    desc = "argument"
    exitcode = 2

class DataPoolError (SandvichError) :
    desc = "data pool/config"
    exitcode = 3
