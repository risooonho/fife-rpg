# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from base import Base

class Containable(Base):
    """Component that allows an entity to be contained by Container entity."""
    
    def __init__(self):
        """Constructor"""
        Base.__init__(self, bulk=int, weight=int, item_type=str, image=str, container=object, slot=int)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        fields.remove("container")
        return fields