#!/usr/bin/env python2
# encoding: utf-8

"""

This is an example script to show how to use Eyetracker class.

"""

import datetime
import pygame

try:
    from eyetracker import Eyetracker
except ImportError:
    Eyetracker = None


def calibrate(self, eyetracker):
    eyetracker.calibrate()
    eyetracker.resume_recording()


def detect_fixation(self, eyetracker):
    screen.fill((100, 100, 100))
    pygame.display.flip()

    loc = eyetracker.wait_startfixation()
    print 'fixation started: %d, %d' % loc

    loc = eyetracker.wait_endfixation()
    print 'fixation ended: %d, %d' % loc


def track(self, eyetracker, duration=1000):
    screen = pygame.display.get_surface()

    for i in range(duration):
        screen.fill((255, 255, 255))
        position = eyetracker.get_gazePosition()
        Text('+').write(screen, position)
        pygame.display.flip()


def main():
    pygame.init()

    subjID = datetime.datetime.now().strftime("%d%H%M%S")
    dataDir = '..\\data\\'

    screen = pygame.display.set_mode((1280, 1024),
                                     pygame.DOUBLEBUF | pygame.FULLSCREEN)

    eyetracker = Eyetracker(subjID=subjID, dataDir=dataDir)
    eyetracker.start_recording()

    try:
        calibrate(eyetracker)
        detect_fixation(eyetracker)
        track(eyetracker)

    except Exception as e:
        print e

    eyetracker.stop_recording()
    eyetracker.terminate()

    pygame.quit()


if __name__ == "__main__":

    if Eyetracker is None:
        print 'eyetracker not found'

    else:
        print 'eyetracker found'
        main()
