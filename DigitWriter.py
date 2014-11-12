################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

"""Write the numerals 0-9 using gestures with Leap Motion"""

import os, sys, thread, time, math
import numpy as np
import cPickle as cp
import Analyzer as An
import TextDisplay as TD
import Leap
from Leap import SwipeGesture

BOARD_SIZE = 400    #Size of our virtual writing surface
DRAW_RADIUS = 7     #Radius (mm) of our virtual 'pen' (fingers)
V_SHIFT = 50        #Min height above the device for writing
BOARD_THRESH = 2500 #Min marked pixels to be considered for analysis


class SampleListener(Leap.Listener):
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

        # Initialize our writing tracker
        self.writing = False
        self.last_swipe = 0 
        self.analyzer = An.Analyzer("nn_params")
        self.board = np.zeros((BOARD_SIZE + 2 * DRAW_RADIUS, 
                                BOARD_SIZE + 2 * DRAW_RADIUS))

        # Simple graphics for text display
        self.text = ''
        self.display = TD.TextDisplay((640, 480), "droid", 64)

    def on_connect(self, controller):
        print "Connected"

        # Gestures for carriage return and backspace
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        fps = frame.current_frames_per_second

        # Set neutral distance for when no hands are present
        d = 32
        for hand in frame.hands:

            # Index-Middle distance determines if we are writing
            dist = [0, 0, 0]
            for finger in hand.fingers:
                if finger.type() == finger.TYPE_INDEX:
                    pos = finger.bone(3).next_joint
                    for i in range(3):
                        dist[i] += pos[i]
                    # Mark up a matrix based on 2d projection of our motion
                    if self.writing and check_bounds(pos):
                        w_x = pos[0] + BOARD_SIZE / 2 + DRAW_RADIUS
                        w_y = pos[1] - V_SHIFT + DRAW_RADIUS
                        self.display.draw_circle([int(w_x / 2), int(w_y / 2)])
                        self.board[w_y-DRAW_RADIUS:w_y+DRAW_RADIUS,
                                w_x-DRAW_RADIUS:w_x+DRAW_RADIUS] = 1

                if finger.type() == finger.TYPE_MIDDLE:
                    for i in range(3):
                        dist[i] -= finger.bone(3).next_joint[i]
            d = math.sqrt(dist[0]**2 + dist[1]**2 + dist[2]**2)

        # Fingers together, reset board and set to writing mode
        if d < 30 and not self.writing:
            self.board *= 0
            self.writing = True
        # Fingers apart, send board for analysis if it contains enough signal
        elif d > 35 and self.writing:
            if np.sum(self.board) > BOARD_THRESH:
                self.text += self.analyzer.analyze_writing(self.board[::-1])
                self.display.write(self.text)
            self.writing = False

        # Swipe gesture erases a character
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                # Only use swipes every 30 frames
                if not self.writing and frame.id - self.last_swipe > 30:
                    self.last_swipe = frame.id
                    self.text = self.text[:-1]
                    self.display.write(self.text)


    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


def check_bounds(pos):
    """Checks if the writing position is on the board area"""
    if abs(pos[0]) < BOARD_SIZE/2 and pos[1] > V_SHIFT:
        if pos[1] < (BOARD_SIZE + V_SHIFT):
            return True
    return False

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
