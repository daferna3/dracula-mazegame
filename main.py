#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

import enemy
import maze_gen
import player
import popups
import lighting
import pickups

def main():
    pygame.init()
    pygame.mixer.init()
    display = (1100, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    clock = pygame.time.Clock()
    
    # textures

    wall_texture = maze_gen.loadTexture('sprites/wall_texture.png')
    floor_texture = maze_gen.loadTexture('sprites/floor_texture.png')
    holy_water_tex = maze_gen.loadTexture('sprites/holy_water.png')
    lantern_tex = maze_gen.loadTexture('sprites/lantern.png')
    mirror_tex = maze_gen.loadTexture('sprites/mirror.png')
    
    dracula_tex = maze_gen.loadTexture('sprites/dracula.png') 
    
    wolf_tex = maze_gen.loadTexture('sprites/wolf.png')
    vamp_tex = maze_gen.loadTexture('sprites/vamp.png')
    drac_head_tex = maze_gen.loadTexture('sprites/drac_head.png')
    player_head_tex = maze_gen.loadTexture('sprites/player_head.png')
    weapon_tex = maze_gen.loadTexture('sprites/weapon.png')
    
    battle_bg_tex = maze_gen.loadTexture('backgrounds/battle_bg.png')
    drac_bg_tex = maze_gen.loadTexture('backgrounds/dracula_bg.png')
    
    popup_system = popups.popups()
    popup_system.start_screen()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75, (display[0]/display[1]), 0.1, 100)
    
    glMatrixMode(GL_MODELVIEW) 
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST) 
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.2, 0.2, 0.2, 1))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    m = maze_gen.maze(cols=16, rows=16, cell_size=2.0)
    m.items_list = pickups.spawn_items(m.cols, m.rows, m.cell_size, holy_water_tex, lantern_tex, mirror_tex)
    m.enemies_list = m.spawn_enemies(dracula_tex, wolf_tex, vamp_tex) 
    
    p = player.player(1, 1, 2.0)
    l = lighting.lighting()
    player_inventory = pickups.pick_ups([], 0)
    
    #player_inventory.id = [1, 2] # UNCOMMENT HERE FOR A FREE HALFER AND INSTAKILL
    
    sensitivity = 0.15 
    show_minimap = False

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_m:
                    show_minimap = not show_minimap
                    if show_minimap and p.is_walking:
                        p.walking_sound.stop()
                        p.is_walking = False
                elif event.key == K_n:
                    if p.is_walking:
                        p.walking_sound.stop()
                        p.is_walking = False
                    popup_system.start_screen() 
                    m = maze_gen.maze(cols=16, rows=16, cell_size=2.0)
                    m.items_list = pickups.spawn_items(m.cols, m.rows, m.cell_size, holy_water_tex, lantern_tex, mirror_tex)
                    m.enemies_list = m.spawn_enemies(dracula_tex, wolf_tex, vamp_tex)
                    p = player.player(1, 1, 2.0)
                    l = lighting.lighting()
                    player_inventory = pickups.pick_ups([], 0)
                elif event.key == K_r:
                    p.is_reset(1, 1, 2.0) 

        if not show_minimap:
            m.elapsed_time += dt
            
            p.mouse(sensitivity)
            keys = pygame.key.get_pressed()
            p.movement(keys, dt, m, tile_size=2.0)

            pickups.check_collisions(p, m.items_list, player_inventory, l, popup_system)

            l.flashlight(p.player_x, p.player_y, p.player_z, p.yaw, p.pitch)

            for e in m.enemies_list:
                if not e.defeated:
                    dist_to_enemy = math.hypot(p.player_x - e.x, p.player_z - e.z)
                    if dist_to_enemy < 1.8:
                        if p.is_walking:
                            p.walking_sound.stop()
                            p.is_walking = False
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                        
                        bg_to_use = drac_bg_tex if e.name == "Dracula" else battle_bg_tex
                        
                        result = enemy.battle(p, e, player_inventory, bg_to_use)
                        
                        if result == "win" and e.name == "Dracula":
                            if popup_system.win_screen():
                                m = maze_gen.maze(cols=16, rows=16, cell_size=2.0)
                                m.items_list = pickups.spawn_items(m.cols, m.rows, m.cell_size, holy_water_tex, lantern_tex, mirror_tex)
                                m.enemies_list = m.spawn_enemies(dracula_tex, wolf_tex, vamp_tex)
                                p = player.player(1, 1, 2.0)
                                l = lighting.lighting()
                                player_inventory = pickups.pick_ups([], 0)
                        elif result == "reset":
                            m = maze_gen.maze(cols=16, rows=16, cell_size=2.0)
                            m.items_list = pickups.spawn_items(m.cols, m.rows, m.cell_size, holy_water_tex, lantern_tex, mirror_tex)
                            m.enemies_list = m.spawn_enemies(dracula_tex, wolf_tex, vamp_tex)
                            p = player.player(1, 1, 2.0)
                            l = lighting.lighting()
                            player_inventory = pickups.pick_ups([], 0)
                        elif result == "quit":
                            pygame.quit()
                            sys.exit(0)
                        
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        rad_yaw = math.radians(p.yaw)
        rad_pitch = math.radians(p.pitch)
        
        look_x = p.player_x + math.sin(rad_yaw) * math.cos(rad_pitch)
        look_y = p.player_y + math.sin(rad_pitch)
        look_z = p.player_z - math.cos(rad_yaw) * math.cos(rad_pitch)
        
        gluLookAt(p.player_x, p.player_y, p.player_z, look_x, look_y, look_z, 0, 1, 0)

        m.draw(wall_texture, floor_texture, p.player_x, p.player_z, tile_size=2.0, height=2.0)
        
        if not show_minimap:
            p.draw_weapon(weapon_tex, display)
        
        if show_minimap:
            m.minimap(p, drac_head_tex, player_head_tex, player_inventory, holy_water_tex, lantern_tex, mirror_tex, display_size=display)
            
        m.draw_hud()
        pygame.display.flip()

if __name__ == '__main__':
    main()