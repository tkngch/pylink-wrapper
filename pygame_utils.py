#!/usr/bin/env python2
# encoding: utf-8

"""

This file provides classes to use with pygame.

Font class requires font files, located under ./fonts
Mouseresponse class requires cursor files, located under ./cursors


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

import os
import pygame


class Button:

    def __init__(self, font, value='Click Me!',
                 boxsize=(400, 150), screen=None):
        self.font = font
        self.value = value
        self.boxsize = boxsize
        self.colour = (0, 0, 0)
        self.bgColour = (200, 200, 200)
        if screen is None:
            self.screen = pygame.display.get_surface()
        else:
            self.screen = screen
        self.center = (300, 200)

    def render(self):
        self.surface = pygame.Surface(self.boxsize)
        self.rect = pygame.Rect(self.surface.get_rect())
        self.rect.center = self.center

        rendered = self.font.render(self.value, 1, self.colour)
        renderedRect = rendered.get_rect()
        renderedRect.center = [s / 2 for s in self.rect.size]

        self.surface.fill(self.bgColour)
        self.surface.blit(rendered, renderedRect)

    def show(self):
        self.render()
        self.screen.blit(self.surface, self.rect)

    def clear(self):
        self.surface.fill((255, 255, 255))
        self.screen.blit(self.surface, self.rect)


class Font:

    def __init__(self, fontname='DejaVuSans', fontsize=25):
        self.fontsize = fontsize
        if not pygame.font.get_init():
            pygame.font.init()

        fontfile = 'fonts/%s.ttf' % fontname
        if os.path.exists(fontfile):
            self.font = pygame.font.Font(fontfile, fontsize)
        elif os.path.exists(fontfile):
            self.font = pygame.font.Font(fontfile, fontsize)
        else:
            raise Exception('Font file does not exist')

    def get(self):
        return self.font


class Image:

    def __init__(self, surface=None, imagefile=None,
                 scale=1, edge=True, edgewidth=1):
        if surface is not None:
            rawImage = surface
        elif imagefile is not None:
            rawImage = pygame.image.load(imagefile)

        if scale is 1:
            image = rawImage
        else:
            imageRect = rawImage.get_rect()
            size = (int(imageRect.size[0] * scale),
                    int(imageRect.size[1] * scale))
            image = pygame.transform.scale(rawImage, size)

        if edge:
            self.imageSurface = self.blackEdge(image, edgewidth)
        else:
            self.imageSurface = image

    def get(self):
        return self.imageSurface

    def blackEdge(self, surface, edgewidth):
        rect = surface.get_rect()

        background = pygame.Surface((rect.width + (edgewidth * 2),
                                     rect.height + (edgewidth * 2)))
        background.fill((0, 0, 0))
        background.get_rect().center = rect.center
        background.blit(surface, pygame.Rect((edgewidth, edgewidth,
                                              rect.width, rect.height)))

        return background


class Keyresponse:

    def __init__(self, acceptedKeys):
        self.acceptedKeys = acceptedKeys

    def wait(self):
        starttime = pygame.time.get_ticks()
        waiting = True
        while waiting:
            key = self.accept_key()
            if key in self.acceptedKeys:
                waiting = False

        keyname = pygame.key.name(key)
        responseTime = pygame.time.get_ticks() - starttime
        return keyname, responseTime

    def accept_key(self):
        """
        accept_key(self)

        returns a pressed key
        """
        pygame.event.clear()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    targetKey = event.key
                    running = False

        return targetKey


class Mouseresponse:

    def __init__(self, rectangles):
        # rectangles are tuple of pygame rect
        self.rectangles = rectangles

        self.handcursor = pygame.cursors.load_xbm(
                            "cursors/handcursor.xbm",
                            "cursors/handcursor_mask.xbm")

    def wait(self):
        pygame.mouse.set_visible(True)
        self.showSystemcursor()

        pygame.event.clear()
        self.waitRelease()

        starttime = pygame.time.get_ticks()

        handcursor = 0
        running = True
        while running:

            collision = self.checkCollision()
            if ((collision in range(len(self.rectangles))) and
               (handcursor is 0)):

                handcursor = 1
                self.showHandcursor()

            elif ((collision not in range(len(self.rectangles))) and
                  (handcursor is 1)):

                handcursor = 0
                self.showSystemcursor()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0]:
                        selected = self.checkCollision()
                        if selected is not None:
                            running = False

        responseTime = pygame.time.get_ticks() - starttime

        self.waitRelease()
        self.showSystemcursor()

        return selected, responseTime

    def showHandcursor(self):
        pygame.mouse.set_cursor(*self.handcursor)

    def showSystemcursor(self):
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def waitRelease(self):
        while any(pygame.mouse.get_pressed()):
            pygame.event.pump()

    def checkCollision(self):
        mousePosition = pygame.mouse.get_pos()

        selected = None
        for i in range(len(self.rectangles)):
            if self.rectangles[i].collidepoint(mousePosition):
                selected = i

        return selected


class Text:

    def __init__(self, text, screen, font=Font().get(), colour=(0, 0, 0)):
        self.text = text
        self.screen = screen
        self.font = font
        self.colour = colour

    def write(self, position=(0, 0)):
        target = self.font.render(self.text, 1, self.colour)
        targetPosition = target.get_rect()
        targetPosition.centerx = position[0]
        targetPosition.centery = position[1]
        self.screen.blit(target, targetPosition)

        return target, targetPosition

    def wrapWrite(self, rect, lineSpace=1):
        """
        """
        space = self.font.render(" ", 1, self.colour)
        spaceSize = space.get_size()

        leftTop = [rect.left, rect.top]

        for sentence in self.text.split("\n"):
            for word in sentence.split(" "):
                word += " "

                target = self.font.render(word, 1, self.colour)
                targetSize = target.get_size()

                if (leftTop[0] + targetSize[0] > rect.right):
                    # new line
                    leftTop[0] = rect.left
                    leftTop[1] += spaceSize[1] * lineSpace

                self.screen.blit(target, leftTop)

                leftTop[0] += targetSize[0]

            leftTop[0] = rect.left
            leftTop[1] += spaceSize[1] * lineSpace
