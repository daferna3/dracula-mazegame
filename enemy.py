import pygame
import random
import time
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
import maze_gen

class enemy: 
    def __init__(self, name, num, limit, press, tex_id):
        self.name = name 
        self.sprite_num = num 
        self.time_limit = limit 
        self.presses = press 
        self.defeated = False 
        self.tex_id = tex_id 
        
def gen_enemy(wolf_tex, vamp_tex): 
    random_num = random.randint(0, 1)
    
    if random_num == 0:
        return enemy('Wolf', 0, 15, 100, wolf_tex)
    else:
        # return enemy('Vampire', 1, 20, 150, vamp_tex) = hard mode
        return enemy('Vampire', 1, 25, 150, vamp_tex)
    
def instakill(player_inventory): # player pickerd up water, can press x to instakill
    if player_inventory and 1 in player_inventory.id:
        return True
    return False
    
def battle(player_obj, enemy_obj, player_inventory, bg_texture):
    # print(f"{enemy_obj.name}, {enemy_obj.presses} times") # TESTING ONLY
    # if player_inventory and 2 in player_inventory.id:
       # print("player has the mirror") # TESTING ONLY
       
    clock = pygame.time.Clock()
       
    pygame.mixer.music.load('audio/encounter.mp3')
    pygame.mixer.music.play(0)
    
    # wipe
    encounter_start = time.time()
    while time.time() - encounter_start < 3.0:
        clock.tick(30)
        elapsed_enc = time.time() - encounter_start
        progress = elapsed_enc / 3.0 # 0.0 to 1.0 over 6 seconds
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
                
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1100, 800, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # under
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1.0, 1.0, 1.0)
        
        glBindTexture(GL_TEXTURE_2D, bg_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(1100, 0)
        glTexCoord2f(1, 0); glVertex2f(1100, 800)
        glTexCoord2f(0, 0); glVertex2f(0, 800)
        glEnd()
        
        glBindTexture(GL_TEXTURE_2D, enemy_obj.tex_id)
        sprite_w, sprite_h = 300, 300
        cx, cy = 800, 230
        ex1, ex2 = cx - (sprite_w / 2), cx + (sprite_w / 2)
        ey1, ey2 = cy - (sprite_h / 2), cy + (sprite_h / 2)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(ex1, ey1)
        glTexCoord2f(1, 1); glVertex2f(ex2, ey1)
        glTexCoord2f(1, 0); glVertex2f(ex2, ey2)
        glTexCoord2f(0, 0); glVertex2f(ex1, ey2)
        glEnd()
        
        # fade
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.0, 0.0, 0.0) 
        
        wipe_y = 700 * (1.0 - progress) # bottom to top
        
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1100, 0)
        glVertex2f(1100, wipe_y)
        glVertex2f(0, wipe_y)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        pygame.display.flip()
    
    if enemy_obj.name == 'Wolf':
        pygame.mixer.music.load('audio/battle_wolf.mp3')
        pygame.mixer.music.set_volume(0.1)
    elif enemy_obj.name == 'Vampire':
        pygame.mixer.music.load('audio/battle_vampire.mp3')
        pygame.mixer.music.set_volume(0.1)
    elif enemy_obj.name == 'Dracula':
        pygame.mixer.music.load('audio/battle_dracula.mp3')
        pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    
    button_presses = 0 
    time_limit = enemy_obj.time_limit 
    enemy_texture = enemy_obj.tex_id 
    
    shake_frames = 0 
    mirror_used = False 
    
    start_time = time.time()
    
    battle_active = True
    while battle_active:
        dt = clock.tick(60) / 1000.0
        elapsed = time.time() - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    button_presses += 1 
                    shake_frames = 10   
                    
                    if button_presses >= enemy_obj.presses: 
                        enemy_obj.defeated = True 
                        
                if event.key == pygame.K_x:
                    if instakill(player_inventory):
                        # print("used water") # TESTING ONLY
                        player_inventory.id.remove(1) # item used
                        shake_frames = 30 
                        enemy_obj.defeated = True
                        
                if event.key == pygame.K_h:
                    if player_inventory and 2 in player_inventory.id and not mirror_used:
                        enemy_obj.presses = max(1, enemy_obj.presses // 2)
                        mirror_used = True
                        player_inventory.id.remove(2) # used
                        shake_frames = 15
                        # print(f"player used the mirror") # TESTING ONLY - comment out before submit
                
        if elapsed > time_limit and not enemy_obj.defeated:
            # print("time up, game over") # TESTING ONLY
            battle_active = False
            from popups import popups
            reset_choice = popups().game_over()
            
            if reset_choice:
                return "reset" 
            else:
                return "quit"
            
        if shake_frames > 0:
            shake_x = random.randint(-15, 15)
            shake_y = random.randint(-15, 15)
            shake_frames -= 1
        else:
            shake_x, shake_y = 0, 0
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1100, 800, 0) 
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1.0, 1.0, 1.0) 
        
        glBindTexture(GL_TEXTURE_2D, bg_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)            
        glTexCoord2f(1, 1); glVertex2f(1100, 0)         
        glTexCoord2f(1, 0); glVertex2f(1100, 800)       
        glTexCoord2f(0, 0); glVertex2f(0, 800)          
        glEnd()
        
        if not enemy_obj.defeated:
            glBindTexture(GL_TEXTURE_2D, enemy_texture) # vanish after beat
            
            sprite_w, sprite_h = 300, 300 
            cx, cy = 800 + shake_x, 230 + shake_y # position x and y in battle
            
            ex1, ex2 = cx - (sprite_w / 2), cx + (sprite_w / 2)
            ey1, ey2 = cy - (sprite_h / 2), cy + (sprite_h / 2)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(ex1, ey1)        
            glTexCoord2f(1, 1); glVertex2f(ex2, ey1)        
            glTexCoord2f(1, 0); glVertex2f(ex2, ey2)        
            glTexCoord2f(0, 0); glVertex2f(ex1, ey2)        
            glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        pygame.display.flip()

        if enemy_obj.defeated:
            pygame.mixer.music.load('audio/battle_win.mp3')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(0)
            
            # wipe
            # print("player win, wait") # TESTING ONLY
            if enemy_obj.name == 'Dracula':
                wait_time = 6.0 # wait 8 seconds for dracula
            else:
                wait_time = 5.0 # wait 3 seconds for others
                
            defeat_start = time.time()
            
            while time.time() - defeat_start < wait_time:
                clock.tick(60)
                elapsed_def = time.time() - defeat_start
                # wipe
                progress = min(1.0, elapsed_def / 1.5) 
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                        
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                glMatrixMode(GL_PROJECTION)
                glPushMatrix()
                glLoadIdentity()
                gluOrtho2D(0, 1100, 800, 0)
                
                glMatrixMode(GL_MODELVIEW)
                glPushMatrix()
                glLoadIdentity()
                
                glDisable(GL_DEPTH_TEST)
                glDisable(GL_LIGHTING)
                
                glEnable(GL_TEXTURE_2D)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glColor3f(1.0, 1.0, 1.0)
                
                
                glBindTexture(GL_TEXTURE_2D, bg_texture)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex2f(0, 0)
                glTexCoord2f(1, 1); glVertex2f(1100, 0)
                glTexCoord2f(1, 0); glVertex2f(1100, 800)
                glTexCoord2f(0, 0); glVertex2f(0, 800)
                glEnd()
                
                # defeat
                if progress < 1.0:
                    glBindTexture(GL_TEXTURE_2D, enemy_texture)
                    
                    sprite_w, sprite_h = 300, 300 
                    cx, cy = 800, 230 
                    
                    ex1, ex2 = cx - (sprite_w / 2), cx + (sprite_w / 2)
                    ey1, ey2 = cy - (sprite_h / 2), cy + (sprite_h / 2)
                    
                    current_ey1 = ey1 + (ey2 - ey1) * progress
                    current_v1 = 1.0 - progress
                    
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, current_v1); glVertex2f(ex1, current_ey1)        
                    glTexCoord2f(1, current_v1); glVertex2f(ex2, current_ey1)        
                    glTexCoord2f(1, 0);          glVertex2f(ex2, ey2)        
                    glTexCoord2f(0, 0);          glVertex2f(ex1, ey2)        
                    glEnd()
                
                glDisable(GL_BLEND)
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)
                
                glMatrixMode(GL_PROJECTION)
                glPopMatrix()
                glMatrixMode(GL_MODELVIEW)
                glPopMatrix()
                
                pygame.display.flip()

            # resume music
            pygame.mixer.music.load('audio/in_game.mp3')
            pygame.mixer.music.set_volume(1.0) 
            pygame.mixer.music.play(-1)

            battle_active = False
            return "win"