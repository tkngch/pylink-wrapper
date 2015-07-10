#!/usr/bin/env python2
# encoding: utf-8

"""

This is an example script to show how to use Eyetracker class.

"""

import pygame
import eyetracker


if __name__ == "__main__":
    try:
        from eyetracker import Eyetracker
    except ImportError:
        Eyetracker = None

    pygame.init()

    if Eyetracker is None:
        print 'eyetracker not found'
        screen = pygame.display.set_mode((1280, 1024), pygame.DOUBLEBUF)
        eyetracker = None
        test(eyetracker)

    else:
        print 'eyetracker found'
        screen = pygame.display.set_mode((1280, 1024),
                                         pygame.DOUBLEBUF | pygame.FULLSCREEN)
        tracker = Eyetracker(datetime.datetime.now().strftime("%d%H%M%S"),
                             '..\\data\\')
        tracker.start_recording()
        test(eyetracker)
        tracker.stop_recording()
        tracker.terminate()

    pygame.quit()
