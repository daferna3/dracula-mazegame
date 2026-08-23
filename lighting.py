from OpenGL.GL import *
import math

class lighting:
    def __init__(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        
        self.diffuse_color = [1.0, 0.95, 0.88, 1.0]  
        self.specular_color = [0.5, 0.5, 0.5, 1.0]
        
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse_color)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular_color)
        
        self.lantern = False

    def flashlight(self, player_x, player_y, player_z, yaw, pitch):
        glLightfv(GL_LIGHT0, GL_POSITION, (player_x, player_y, player_z, 1.0))
        
        rad_yaw = math.radians(yaw)
        rad_pitch = math.radians(pitch)
        dir_x = math.sin(rad_yaw) * math.cos(rad_pitch)
        dir_y = math.sin(rad_pitch)
        dir_z = -math.cos(rad_yaw) * math.cos(rad_pitch)
        
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, (dir_x, dir_y, dir_z))
        
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 8.0)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        
        if self.lantern: 
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.28, 0.35, 1.0])
            glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 60.0)
            glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.01)     
            glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.001)
        else: 
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
            glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 25.0)
            glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.3)     
            glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.05)