import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class player:
    def __init__(self, start_grid_x, start_grid_z, tile_size):
        self.player_x = start_grid_x * tile_size + (tile_size / 2)
        self.player_y = 1.0 
        self.player_z = start_grid_z * tile_size + (tile_size / 2)
        
        self.yaw = 0.0
        self.pitch = 0.0
        self.speed = 3.0
        self.radius = 0.35 
        
        self.bob_phase = 0.0
        
        self.walking_sound = pygame.mixer.Sound("audio/walking.mp3")
        self.is_walking = False
        
    def mouse(self, sensitivity=0.15):
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        pygame.mouse.set_pos((1100 // 2, 800 // 2))
        pygame.mouse.get_rel() 

        self.yaw += mouse_dx * sensitivity
        self.pitch -= mouse_dy * sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch)) 
        self.yaw %= 360.0

    def collisions(self, dx, dz, maze_obj, tile_size):
        margin = self.radius 
        
        grid_x = int(self.player_x // tile_size)
        grid_z = int(self.player_z // tile_size)
        
        if 0 <= grid_x < maze_obj.cols and 0 <= grid_z < maze_obj.rows:
            current_cell = maze_obj.grid_cells[grid_x + grid_z * maze_obj.cols]
            
            new_x = self.player_x + dx
            new_z = self.player_z + dz
            
            min_x = grid_x * tile_size + margin
            max_x = (grid_x + 1) * tile_size - margin
            min_z = grid_z * tile_size + margin
            max_z = (grid_z + 1) * tile_size - margin
            
            if current_cell.walls['left'] and new_x < min_x: new_x = min_x
            if current_cell.walls['right'] and new_x > max_x: new_x = max_x
            if current_cell.walls['top'] and new_z < min_z: new_z = min_z
            if current_cell.walls['bottom'] and new_z > max_z: new_z = max_z
                
            self.player_x = new_x
            self.player_z = new_z
        else:
            self.player_x += dx
            self.player_z += dz

    def movement(self, keys, dt, maze_obj, tile_size=2.0): 
        rad_yaw = math.radians(self.yaw)
        
        dx, dz = 0.0, 0.0 
        
        fx = math.sin(rad_yaw)
        fz = -math.cos(rad_yaw)
        
        rx = math.cos(rad_yaw)
        rz = math.sin(rad_yaw)
        
        if keys[K_w]: dx += fx; dz += fz
        if keys[K_s]: dx -= fx; dz -= fz
        if keys[K_a]: dx -= rx; dz -= rz
        if keys[K_d]: dx += rx; dz += rz
            
        length = math.hypot(dx, dz)
            
        if length > 0:
            dx /= length
            dz /= length
            self.bob_phase += dt * 10.0 # cross bobbing while moving
            if not self.is_walking:
                self.walking_sound.play(-1)
                self.is_walking = True
        else:
            self.bob_phase *= 0.85 
            if self.bob_phase < 0.05:
                self.bob_phase = 0.0
            if self.is_walking:
                self.walking_sound.stop()
                self.is_walking = False
        
        dx *= self.speed * dt
        dz *= self.speed * dt
        
        self.collisions(dx, dz, maze_obj, tile_size)
        
    def is_reset(self, start_x, start_y, tile_size):
        self.player_x = start_x * tile_size + (tile_size / 2)
        self.player_z = start_y * tile_size + (tile_size / 2)
        self.yaw = 0.0
        self.pitch = 0.0
        self.bob_phase = 0.0
        if self.is_walking:
            self.walking_sound.stop()
            self.is_walking = False

    def draw_weapon(self, weapon_tex, display_size=(1100, 800)):
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
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBindTexture(GL_TEXTURE_2D, weapon_tex)
        glColor3f(1.0, 1.0, 1.0)
        
        w, h = 300, 475
        bob_x = math.sin(self.bob_phase) * 30
        bob_y = abs(math.cos(self.bob_phase)) * 25
        
        x = display_size[0] - w + bob_x - 50 
        y = display_size[1] - h + bob_y + 40 
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()