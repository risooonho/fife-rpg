# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  This module is based on the behaviour package from PARPG

"""This module contains the basic behaviour for agents.

.. module:: base
    :synopsis: Contains the basic behaviour for agents.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from collections import deque

from fife import fife

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.components.general import General
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.behaviours import AGENT_STATES

class Base (fife.InstanceActionListener):
    """Behaviour that contains the basic methods for actors
    
    Properties:
        agent: A :class:`fife.Instance` that represents the agent
        
        state: The current state of the behaviour
        
        animation_queue: A deque that contains the queued animations
        
        next_action: The :class:`fife_rpg.actions.base.Base` that will be 
        executed after the current animation is finished

        registered_as: Class property that sets under what name the class is
        registered
        
        dependencies: Class property that sets the classes this System depends
        on
    """
    __registered_as = None

    def __init__(self):
        fife.InstanceActionListener.__init__(self)
        self.agent = None
        self.state = None
        self.animation_queue = deque()
        self.next_action = None

    @property
    def location(self):
        """Returns the location of the agent"""
        return self.agent.getLocation().getLayerCoordinates()
    
    @property
    def rotation(self):
        """Returns the rotation of the agent"""
        return self.agent.getRotation()
    
    @rotation.setter
    def rotation(self, rotation):
        """Sets the rotation of the agent"""
        self.agent.setRotation(rotation)
    
    def attach_to_layer(self, agent_id, layer):
        """Attaches to a certain layer

        Args:
           agent_id: ID of the layer to attach to.
           
           layer: :class:`fife.Layer` of the agent to attach the behaviour to
        """
        self.agent = layer.getInstance(agent_id)
        self.agent.addActionListener(self)
        self.state = AGENT_STATES.TALK

    def on_new_map(self, layer):
        """Called when the agent is moved to a different map

        Args:
            layer: The :class:`fife.Layer` that the agent was moved to
        """
        if self.agent is not None:
            self.agent.removeActionListener(self)
        general = getattr(self.parent, General.registered_as)
        self.agent = layer.getInstance(general.identifier)
        self.agent.addActionListener(self)
        self.state = AGENT_STATES.NONE

    def idle(self):
        """Set the state to idle"""
        self.state = AGENT_STATES.IDLE

    def onInstanceActionFinished(self, instance, animation):
        #pylint: disable=C0103,W0613,W0221
        """Called by FIFE when an animation of an agent is finished

        Args:
            instance: The agent instance
            
            animation: The animation that the agent was doing
        """
        # First we reset the next behavior 
        act = self.next_action
        self.next_action = None 
        self.idle()

        if act:
            act.execute()
        try:
            animtion = self.animation_queue.popleft()
            self.animate(**animtion)
        except IndexError:
            self.idle()

    def onInstanceActionFrame(self, instance, animation, frame):
        #pylint: disable=C0103,W0613,W0221
        """Called by FIFE when a frame of an animation of an agent is finished

        Args:
            instance: The agent instance
            
            animation: The animation that the agent was doing
            
            frame: The frame that the was done
        """
        pass

    def talk(self):
        """Set the agent to their talking animation"""
        self.state = AGENT_STATES.TALK
        self.clear_animations()
        self.idle()

    def animate(self, animation, direction = None, repeating = False):
        """Perform an animation

        Args:
            animation: The animation to perform
            
            direction: The direction to which the agent should face
            
            repeating: Whether to repeat the animation or not
        """
        direction = direction or self.agent.getFacingLocation()
        self.agent.act(animation, direction, repeating)

    def queue_animation(self, animation, direction = None, repeating = False):
        """Add an animation to the queue

        Args:
            animation: The animation to perform
            
            direction: The direction to which the agent should face
            
            repeating: Whether to repeat the animation or not
        """
        self.animation_queue.append({"animation": animation, 
                                     "direction": direction,
                                  "repeating": repeating})
        
    def clear_animations(self):
        """Remove all actions from the queue"""
        self.animation_queue.clear()

    @classmethod
    def register(cls, name="Base"):
        """Registers the class as a behaviour

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the behaviour was registered, False if not.
        """
        try:
            BehaviourManager.register_behaviour(name, cls)
            cls.__registered_as = name
            return True
        except AlreadyRegisteredError as error:
            print error
            return False