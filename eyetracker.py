#!/usr/bin/env python2
# encoding: utf-8

"""

This file provides a wrapper class to pylink, Eyetracker. This is mainly to
ease the use of EyeLink eye-tracker (SR research).


Copyright 2015 Takao Noguchi (tkngch@runbox.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import pygame
import pylink
import os

from pygame_utils import Text


class Eyetracker:

    def __init__(self, subjID, dataDir):
        self._init_graphics()
        self._init_datafiles(subjID, dataDir)
        self._init_tracker()
        self._init_calibration()

        pylink.flushGetkeyQueue()
        self.tracker.setOfflineMode()
        self.tracker.openDataFile(self.trackerDatafile)

    def _init_graphics(self):
        self.screen = pygame.display.get_surface()
        self.screenRect = self.screen.get_rect()
        pylink.openGraphics()

    def _init_datafiles(self, datafilename, datadir):
        # define datafiles
        # trackerDatafile is a temporary file saved onto the tracker PC
        self.trackerDatafile = '%s.edf' % datafilename
        # localDatafile is where the trackerDatafile is saved
        # on the local (presentation) PC
        self.localDatafile = datadir + '\\' + self.trackerDatafile

    def _init_tracker(self):
        self.tracker = pylink.EyeLink()
        # Gets the display surface and sends a mesage to EDF file;
        self.tracker.sendCommand(
                "screen_pixel_coords =  0 0 %d %d" % self.screenRect.size)
        self.tracker.sendMessage(
                "DISPLAY_COORDS  0 0 %d %d" % self.screenRect.size)

        tracker_software_ver = 0
        eyelink_ver = self.tracker.getTrackerVersion()
        if eyelink_ver == 3:
            tvstr = self.tracker.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(
                tvstr[(vindex + len("EYELINK CL")):].strip()))

        if eyelink_ver >= 2:
            self.tracker.sendCommand("select_parser_configuration 0")
            if eyelink_ver == 2:  # turn off scenelink camera stuff
                self.tracker.sendCommand("scene_camera_gazemap = NO")
            else:
                self.tracker.sendCommand("saccade_velocity_threshold = 35")
                self.tracker.sendCommand(
                        "saccade_acceleration_threshold = 9500")

        # set EDF file contents
        self.tracker.sendCommand(
                "file_event_filter = " +
                "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        if tracker_software_ver >= 4:
            self.tracker.sendCommand(
                    "file_sample_data = " +
                    "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
        else:
            self.tracker.sendCommand(
                    "file_sample_data = " +
                    "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

        # set link data (used for gaze cursor)
        self.tracker.sendCommand(
                "link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        if tracker_software_ver >= 4:
            self.tracker.sendCommand(
                    "link_sample_data = " +
                    "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
        else:
            self.tracker.sendCommand(
                    "link_sample_data = " +
                    "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")

        self.tracker.sendCommand("button_function 5 'accept_target_fixation'")

    def _init_calibration(self):
        # Sets the calibration target and background color
        pylink.setCalibrationColors((0, 0, 0), (255, 255, 255))
        # select best size for calibration target
        pylink.setTargetSize(self.screenRect.width / 70,
                             self.screenRect.width / 300)
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")

    def checkUp(self):
        # Does drift correction and handles the re-do camera setup situations
        self.display_message(
                'Starting drift correction. ' +
                'Press ESC to enter the eyelink setup.')
        try:
            error = self.tracker.doDriftCorrect(self.screenRect.width / 2,
                                                self.screenRect.height / 2,
                                                1, 1)
            if error <= 27:
                pass
            else:
                self.calibrate()
        except:
            self.calibrate()

        self.resume_recording()
        self.display_message('Resuming the experiment...')

    def calibrate(self):
        self.display_message('Starting the eyelink setup...')
        self.tracker.doTrackerSetup()
        self.eye_used = self.tracker.eyeAvailable()
        self.resume_recording()

    def resume_recording(self):
        error = self.tracker.startRecording(1, 1, 1, 1)
        if error:
            self.display_message('Error occured.')
            print error
            raise RuntimeError(error)
        else:
            # introduce 100 millisecond delay after recording begins
            # to ensure that no data is missed before the trial starts.
            pylink.beginRealTimeMode(100)

    def start_recording(self):
        self.calibrate()
        self.resume_recording()

        self.display_message('Recording started.')

        # determine which eye(s) are available
        self.eye_used = self.tracker.eyeAvailable()
        if self.eye_used in (1, "RIGHT_EYE"):
            self.tracker.sendMessage("EYE_USED 1 RIGHT")
        elif self.eye_used in (0, "LEFT_EYE"):
            self.tracker.sendMessage("EYE_USED 0 LEFT")

    def stop_recording(self):
        '''Ends recording: adds 100 msec of data to catch final events'''

        pylink.endRealTimeMode()
        pylink.pumpDelay(100)
        self.tracker.stopRecording()
        # self.display_message('Recording stopped.')

        while self.tracker.getkey():
            pass

    def terminate(self):
        # File transfer and cleanup!
        self.tracker.setOfflineMode()
        pylink.msecDelay(500)

        # Close the file and transfer it to Display PC
        self.tracker.closeDataFile()
        self.tracker.receiveDataFile(self.trackerDatafile, self.localDatafile)
        self.tracker.close()

        self.display_message('Eyelink disconnected.')

        # Close the experiment graphics
        pylink.closeGraphics()

        # convert the edf file to asc file
        self.edf2asc()

    def send_message(self, message):
        self.tracker.sendMessage(message)

    def edf2asc(self):
        command = 'edf2asc ' + self.localDatafile
        os.system(command)

    def display_message(self, message):
        self.screen.fill((255, 255, 255))
        Text(message, self.screen).write(self.screenRect.center)
        pygame.display.flip()
        pygame.time.wait(2000)

    def get_gazePosition(self):
        dt = self.tracker.getNewestSample()

        if (dt is not None):
            # Gets the gaze position of the latest sample,
            if self.eye_used in (1, "RIGHT_EYE") and dt.isRightSample():
                gaze_position = dt.getRightEye().getGaze()
            elif self.eye_used in (0, "LEFT_EYE") and dt.isLeftSample():
                gaze_position = dt.getLeftEye().getGaze()
        else:
            gaze_position = None

        return gaze_position

    def wait_startfixation(self):
        waiting = True
        while waiting:
            event = self.tracker.getNextData()
            if event == pylink.STARTFIX:
                gaze_position = self.get_gazePosition()

                # getStartGaze gives me a negative values (not sure why)
                # gaze_position = self.tracker.getFloatData().getStartGaze()

                waiting = False

        return gaze_position

    def wait_endfixation(self):
        waiting = True
        while waiting:
            event = self.tracker.getNextData()
            if event == pylink.ENDFIX:
                gaze_position = self.get_gazePosition()

                # getAverageGaze gives me a strange values...
                # gaze_position = self.tracker.getFloatData().getAverageGaze()

                waiting = False

        return gaze_position


class Test:

    def fixation(self, eyetracker):
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

    def calibrate(self, eyetracker):
        self.track(eyetracker, duration=300)
        eyetracker.calibrate()
        eyetracker.resume_recording()
        self.track(eyetracker, duration=300)


if __name__ == "__main__":
    import datetime

    pygame.init()
    screen = pygame.display.set_mode((1280, 1024),
                                     pygame.DOUBLEBUF | pygame.FULLSCREEN)

    subjID = datetime.datetime.now().strftime("%d%H%M%S")
    dataDir = '..\\data\\'
    eyetracker = Eyetracker(subjID=subjID, dataDir=dataDir)
    eyetracker.start_recording()

    try:
        Test().calibrate(eyetracker)
    except Exception as e:
        print e

    eyetracker.stop_recording()
    eyetracker.terminate()
    pygame.quit()
