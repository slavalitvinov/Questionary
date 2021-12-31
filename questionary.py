
import sys
import pygame
import string

from dataclasses import dataclass, field
from typing import Iterable, Optional, List, Sequence, Tuple
from enum import Enum
import re
import os

BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = ( 255, 0, 0)

@dataclass
class Question:
    """Class for storing a question and its details."""
    title: Optional[str] = None
    # The question text.
    question: str = ''
    # The list of available options.
    options: list[str] = field(default_factory=list)
    # The list of images to support the question or options.
    images: list[str] = field(default_factory=list)
    # The correct answer index from the given options, starting from 1.
    answer: int = 0
    # The final text to be displayed when an answer is given.
    final_text: Optional[str] =  None
    # The final image to support the answer.
    final_image: Optional[str] = None

Questions = Iterable[Question]

def read_questions(filename: str) -> Questions:
    """Yields  questions out of a given text file.
    
    A text file contains:

    title: <optional title text>
    question: <question text>
    option: <option text>
    option: <option text>
    image: <optional image file path relative to the given filename>
    image: <...>
    answer: <index>
    final_text: <optional text>
    final_image: <optional image file path>
    """
    base_path = os.path.dirname(filename)
    with open(filename, 'rt') as input_file:
        line_number = 1
        quest = Question()
        for line in input_file:
            line = line.rstrip()
            print(line)
            if len(line) == 0:
                if len(quest.question):
                    yield quest
                quest = Question()
            elif line.startswith('#'):
                pass
            else:
                try:
                    name, value = re.split(r'\s*:\s*', line, maxsplit=2)
                except Exception as e:
                    raise Exception(f'Failed to parse {filename}:{line_number}: {line!r}.') from e
                if name == 'option':
                    quest.options.append(value)
                elif name == 'image':
                    quest.images.append(os.path.join(base_path, value))
                elif name == 'final_image':
                    quest.final_image = os.path.join(base_path, value)
                elif name in vars(Question):
                    setattr(quest, name, value)
                else:
                    raise Exception(
                        f'Invalid question field {name!r} at {filename}:{line_number}:\n  {line}')
            line_number += 1
        if len(quest.question):
            yield quest

class Screen:

    def __init__(self, surface: pygame.Surface, font):
        self._surface = surface
        self._font = font

    def draw_text_center(self, text, color=(0,0,0), x=None, y=None, align_x=None, align_y=None):
        text_surface, rect = self._font.render(text, color)
        if x is None:
            if align_x is None:
                x = 0
        self._surface.blit(text_surface, (40, 250))

class Questionary:    

    def __init__(self, questions: Questions):
        self._questions = iter(questions)
        self._current = None
        self._show_final = False

        pygame.init()
        self._screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        # TODO: support custom fonts.
        # print(pygame.font.get_fonts())
        self._font = pygame.freetype.Font(None, 24)

    @property
    def current(self) -> Question:
        """Returns the current question."""
        if self._current is None:
            self._current = next(self._questions, None)
        return self._current

    def next(self) -> Question:
        """Moves current pointer to the next question."""
        self._current = None
        return self.current

    def scale_image(self, image, size, center_image=True) -> Tuple[pygame.Surface, Tuple[int, int]]:
        """Scales the image to the size respecting the current size ratio.
        
        Returns the scaled image and a tuple of (x, y) offset.
        """
        screen_w, screen_h = size
        image_w, image_h = image.get_size()

        screen_aspect_ratio = screen_w / screen_h
        photo_aspect_ratio = image_w / image_h

        if screen_aspect_ratio < photo_aspect_ratio:  # Width is binding
            new_image_w = screen_w
            new_image_h = int(new_image_w / photo_aspect_ratio)
            image = pygame.transform.smoothscale(image, (new_image_w, new_image_h))
            image_x = 0
            image_y = (screen_h - new_image_h) // 2 if center_image else 0

        elif screen_aspect_ratio > photo_aspect_ratio:  # Height is binding
            new_image_h = screen_h
            new_image_w = int(new_image_h * photo_aspect_ratio)
            image = pygame.transform.smoothscale(image, (new_image_w, new_image_h))
            image_x = (screen_w - new_image_w) // 2 if center_image else 0
            image_y = 0

        else:  # Images have the same aspect ratio
            image = pygame.transform.smoothscale(image, (screen_w, screen_h))
            image_x = 0
            image_y = 0

        return (image, (image_x, image_y))

    def render_question(self, screen, font):
        """Renders the current question with respect of _show_final value."""
        quest = self.current
        size = screen.get_size()

        screen.fill((255,255,255))

        if quest is None:
            text_surface, rect = font.render("No more questions are left. Press 'ESC' to quit.", (0, 0, 0))
            screen.blit(text_surface, (40, 250))
            return

        if quest.title:
            text_surface, rect = font.render(quest.title, (0, 0, 0))
            screen.blit(text_surface, (size[0]*0.01, size[1]*0.01))

        text = quest.final_text or quest.question if self._show_final else quest.question
        font.render_to(screen, (size[0]*0.05, size[1]*0.1), text, (100, 0, 0))

        for index, option in enumerate(quest.options):
            option = option.replace('\\n', '\n')
            prefix = string.ascii_letters[index] + '. '
            print(f"answer {quest.answer!r}")
            color = (225, 20, 30) if self._show_final and (index+1 == int(quest.answer)) else (0, 0, 0)
            font.render_to(
                screen,
                (screen.get_width()*0.07, screen.get_height()* 0.3 + index*40),
                prefix + option,
                color)

        if self._show_final and quest.final_image:
            image = pygame.image.load(quest.final_image)
            image, (image_x, image_y) = self.scale_image(image, (size[0]*0.90, size[1]*0.45))
            screen.blit(image, (size[0]*0.05 + image_x, size[1]*0.55+image_y))
        else:
            if quest.images:
                image_indent = size[0] * 0.1
                image_width = (size[0] - image_indent*2) / len(quest.images)
                image_height = size[1]*0.4
                for index, image_filename in enumerate(quest.images):
                    print(f'Loading {image_filename}...')
                    image = pygame.image.load(image_filename)
                    image, (image_x, image_y) = self.scale_image(image, (image_width, image_height))
                    screen.blit(image, (image_indent + index*image_width + image_x, size[1]*0.55 + image_y))
                
    def act(self):
        """Implements a user action depending on the context."""
        current = self.current
        if not current:
            return

        if self._show_final:
            self._show_final = False
            self.next()
            return

        self._show_final = True

    def render(self):
        """Renders a question."""
        self.render_question(self._screen, self._font)
        pygame.display.flip()

    def run(self):
        """The main events loop."""
        running = True
        self.render()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)
                    self.render()
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        self.act()
                    self.render()

        pygame.quit()


def main():
    if len(sys.argv) != 2:
        raise Exception(
            f'Failed to retrieve a questionary filename. Use: {sys.argv[0]} <filename>')
    filename = sys.argv[1]
    questionary = Questionary(read_questions(filename))
    questionary.run()

main()