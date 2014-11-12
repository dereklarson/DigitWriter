"""Simple display class so we can see what we are writing"""

import sys, os, pygame, time


class TextDisplay(object):

    def __init__(self, size, font, font_size):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.bg_color = [10, 10, 10]
        self.size = size
        self.screen = pygame.display.set_mode(size)
        self.font = pygame.font.SysFont(font, font_size)
        self.redraw()
        pygame.display.flip()

    # Refresh the setup
    def redraw(self):
        self.screen.fill(self.bg_color)
        pygame.draw.rect(self.screen, [140, 140, 140],
                [self.size[0]/4, self.size[1]/2 + 50,
                    self.size[0]/2, self.size[1]/2 - 60], 2)


    # Write centered text
    def write(self, text, color=(0, 0, 255), centered=True, pos=(0,0)):
        label = self.font.render(text, 4, color)
        if centered:
            pos = label.get_rect(centerx=self.size[0]/2, centery=self.size[1]/2)
        self.redraw()
        self.screen.blit(label, pos)
        pygame.display.flip()

    # This is used to show us what our writing looks like as we gesture
    def draw_circle(self, pos, color=[50, 50, 50], radius=5):
        pos = [self.size[0]/2 - 100 + pos[0], self.size[1] - 10 - pos[1]]
        pygame.draw.circle(self.screen, color, pos, radius)
        pygame.display.flip()

