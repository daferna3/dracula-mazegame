import math
import random
import pygame

class item:
    def __init__(self, item_id, grid_x, grid_z, tile_size, tex_id):
        self.id = item_id 
        self.x = grid_x * tile_size + (tile_size / 2)
        self.z = grid_z * tile_size + (tile_size / 2)
        self.tex_id = tex_id
        self.collected = False

class pick_ups:
    def __init__(self, item_ids, count):
        self.id = item_ids
        self.count = count

def spawn_items(cols, rows, tile_size, holy_water_tex, lantern_tex, mirror_tex):
    items = []
    
    def get_pos():
        return random.randint(2, cols - 2), random.randint(2, rows - 2)
        
    rx1, rz1 = get_pos()
    rx2, rz2 = get_pos()
    rx3, rz3 = get_pos()
    
    items.append(item(0, rx1, rz1, tile_size, holy_water_tex))
    items.append(item(1, rx2, rz2, tile_size, lantern_tex))
    items.append(item(2, rx3, rz3, tile_size, mirror_tex))
    return items

def check_collisions(p, items_list, player_inventory, l, popup_system): # checks "collisions" with items for picking up
    for i in items_list:
        if not i.collected:
            dist = math.hypot(p.player_x - i.x, p.player_z - i.z)
            if dist < 1.0:
                if p.is_walking:
                    p.walking_sound.stop()
                    p.is_walking = False
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                
                if i.id == 0: item_name = "Holy Water"
                elif i.id == 1: item_name = "Lantern"
                elif i.id == 2: item_name = "Mirror"
                
                take_it = popup_system.item_pickup(item_name, i.tex_id)
                
                if take_it:
                    pygame.mixer.Sound('audio/pickup.mp3').play()
                    
                    i.collected = True
                    if i.id == 0:
                        player_inventory.id.append(1) 
                    elif i.id == 1:
                        l.lantern = True 
                    elif i.id == 2:
                        player_inventory.id.append(2) 
                        
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)