import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *

import audio
import backgrounds
import sprites

# this file handles ALL pop ups that appear since I heavily relied on images

def load_texture(filename):
    try:
        surface = pygame.image.load(filename)
        surface = pygame.transform.flip(surface, False, True) 
        data = pygame.image.tostring(surface, "RGBA", 0)
        w, h = surface.get_width(), surface.get_height()

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return tex
    except Exception as e:
        # print(f"Error loading texture '{filename}': {e}") # TESTING ONLY
        return 0

class popups:
    def __init__(self):
        self.tex_start = load_texture("backgrounds/start_screen.png")
        self.tex_instructions = load_texture("backgrounds/instructions.png")
        self.tex_win = load_texture("backgrounds/you_win.png")
        self.tex_game_over = load_texture("backgrounds/game_over.png")
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Times New Roman', 24, bold=True)

    def render_text(self, text, color, x, y, display_size):
        text_surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tw, th = text_surface.get_size()
        
        tex_text = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_text)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_text)
        glColor3f(1.0, 1.0, 1.0)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + tw, y)
        glTexCoord2f(1, 0); glVertex2f(x + tw, y + th)
        glTexCoord2f(0, 0); glVertex2f(x, y + th)
        glEnd()
        
        glDeleteTextures(1, [tex_text])

    def draw_image_overlay(self, tex_id, display_size=(1100, 800)):
        if not tex_id:
            return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, display_size[0], display_size[1], 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(display_size[0], 0)
        glTexCoord2f(1, 0); glVertex2f(display_size[0], display_size[1])
        glTexCoord2f(0, 0); glVertex2f(0, display_size[1])
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        pygame.display.flip()

    def start_screen(self):
            pygame.mixer.music.load("audio/start_screen.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            show_instructions = False
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            pygame.mixer.music.load("audio/started_game.mp3")
                            pygame.mixer.music.play(0)
                            pygame.time.wait(4000)
                            
                            pygame.mixer.music.load("audio/in_game.mp3")
                            pygame.mixer.music.set_volume(1.0) # louder volume for in-game
                            pygame.mixer.music.play(-1)
                            return
                        if event.key == pygame.K_i:
                            show_instructions = True
                        if event.key == pygame.K_b:
                            show_instructions = False
                
                current_tex = self.tex_instructions if show_instructions else self.tex_start
                self.draw_image_overlay(current_tex)

    def win_screen(self):
        pygame.mixer.music.load("audio/you_win.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(0)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_n, pygame.K_r): 
                        pygame.mixer.music.load("audio/in_game.mp3")
                        pygame.mixer.music.set_volume(1.0)
                        pygame.mixer.music.play(-1)
                        return True
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit(0)
            self.draw_image_overlay(self.tex_win)

    def game_over(self):
        pygame.mixer.music.load("audio/game_over.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(0)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_n, pygame.K_r): 
                        pygame.mixer.music.load("audio/in_game.mp3")
                        pygame.mixer.music.set_volume(1.0)
                        pygame.mixer.music.play(-1)
                        return True
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit(0)
            self.draw_image_overlay(self.tex_game_over)

    def item_pickup(self, item_name, texture_id, display_size=(1100, 800)): # pop up window with sprite
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, display_size[0], display_size[1], 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.6)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(display_size[0], 0)
        glVertex2f(display_size[0], display_size[1]); glVertex2f(0, display_size[1])
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        
        sprite_size = 250
        cx = (display_size[0] - sprite_size) // 2
        cy = (display_size[1] - sprite_size) // 2 - 50
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(cx, cy)
        glTexCoord2f(1, 1); glVertex2f(cx + sprite_size, cy)
        glTexCoord2f(1, 0); glVertex2f(cx + sprite_size, cy + sprite_size)
        glTexCoord2f(0, 0); glVertex2f(cx, cy + sprite_size)
        glEnd()

        green_color = (100, 255, 100)
        white_color = (255, 255, 255)
        
        self.render_text(f"You picked up a {item_name}!", white_color, cx - 20, cy + sprite_size + 40, display_size)
        self.render_text("Press 'SPACE' to continue", white_color, cx - 20, cy + sprite_size + 80, display_size)

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True