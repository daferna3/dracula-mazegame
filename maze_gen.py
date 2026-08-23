import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import time
import enemy

def loadTexture(texture_name, rotate_deg=0):
    try:
        textureSurface = pygame.image.load(texture_name)
        
        if rotate_deg != 0:
            textureSurface = pygame.transform.rotate(textureSurface, rotate_deg) 
        
        textureData = pygame.image.tostring(textureSurface, "RGBA", True)
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        return texid
    except Exception as e:
        # print(f"MISSING!!!! '{texture_name}': {e}.") # TESTING ONLY
        return 0

class cell: 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        
    def check_cell(self, x, y, cols, rows, grid_cells):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self, cols, rows, grid_cells):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, cols, rows, grid_cells)
        right = self.check_cell(self.x + 1, self.y, cols, rows, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, cols, rows, grid_cells)
        left = self.check_cell(self.x - 1, self.y, cols, rows, grid_cells)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return random.choice(neighbors) if neighbors else False

class maze_item:
    def __init__(self, item_id, grid_x, grid_z, tile_size, tex_id):
        self.id = item_id 
        self.x = grid_x * tile_size + (tile_size / 2)
        self.z = grid_z * tile_size + (tile_size / 2)
        self.tex_id = tex_id
        self.collected = False

class maze: 
    def __init__(self, cols=16, rows=16, cell_size=2.0):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.grid_cells = [cell(x, y) for y in range(self.rows) for x in range(self.cols)]
        
        self.elapsed_time = 0.0 
        pygame.font.init()
        self.font = pygame.font.SysFont('Times New Roman', 18, bold=True)
        self.text_texture = None
        
        self.generate()
        self.carve_center_room()
        self.items_list = [] 
        
    def remove_walls(self, current, next_cell):
        dx = current.x - next_cell.x
        if dx == 1:
            current.walls['left'] = False
            next_cell.walls['right'] = False
        elif dx == -1:
            current.walls['right'] = False
            next_cell.walls['left'] = False
        dy = current.y - next_cell.y
        if dy == 1:
            current.walls['top'] = False
            next_cell.walls['bottom'] = False
        elif dy == -1:
            current.walls['bottom'] = False
            next_cell.walls['top'] = False    

    def generate(self):
        current_cell = self.grid_cells[0]
        array = []
        break_count = 1
        while break_count != len(self.grid_cells):
            current_cell.visited = True
            next_cell = current_cell.check_neighbors(self.cols, self.rows, self.grid_cells)
            if next_cell:
                next_cell.visited = True
                break_count += 1
                array.append(current_cell)
                self.remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif array:
                current_cell = array.pop()
        return self.grid_cells

    def carve_center_room(self):
        mid_x = self.cols // 2
        mid_y = self.rows // 2
        
        for y in range(mid_y - 1, mid_y + 2):
            for x in range(mid_x - 1, mid_x + 2):
                idx = x + y * self.cols
                c = self.grid_cells[idx]
                if x > mid_x - 1: c.walls['left'] = False
                if x < mid_x + 1: c.walls['right'] = False
                if y > mid_y - 1: c.walls['top'] = False
                if y < mid_y + 1: c.walls['bottom'] = False

    def spawn_enemies(self, drac_tex, wolf_tex, vamp_tex):
        enemies = []
        mid_x = self.cols // 2
        mid_y = self.rows // 2
        
        dracula = enemy.enemy('Dracula', 2, 25, 200, drac_tex)
        dracula.x = mid_x * self.cell_size + (self.cell_size / 2)
        dracula.z = mid_y * self.cell_size + (self.cell_size / 2)
        enemies.append(dracula)
        
        player_spawn_x, player_spawn_z = 1, 1
        spawned_positions = [(mid_x, mid_y)]
        
        while len(enemies) < 8:
            rx = random.randint(1, self.cols - 2)
            rz = random.randint(1, self.rows - 2)
            
            if math.hypot(rx - player_spawn_x, rz - player_spawn_z) < 5.0:
                continue
                
            too_close = any(math.hypot(rx - ex, rz - ez) < 3.0 for (ex, ez) in spawned_positions)
            if too_close:
                continue
                
            spawned_positions.append((rx, rz))
            rand_enemy = enemy.gen_enemy(wolf_tex, vamp_tex) 
            rand_enemy.x = rx * self.cell_size + (self.cell_size / 2)
            rand_enemy.z = rz * self.cell_size + (self.cell_size / 2)
            enemies.append(rand_enemy)
            
        return enemies

    def spawn_items(self, holy_water_tex, lantern_tex, mirror_tex):
        items = []
        def get_pos():
            return random.randint(2, self.cols - 2), random.randint(2, self.rows - 2)
            
        rx1, rz1 = get_pos()
        rx2, rz2 = get_pos()
        rx3, rz3 = get_pos()
        
        items.append(maze_item(1, rx1, rz1, self.cell_size, holy_water_tex)) # ID 1
        items.append(maze_item(0, rx2, rz2, self.cell_size, lantern_tex))    # ID 0
        items.append(maze_item(2, rx3, rz3, self.cell_size, mirror_tex))     # ID 2
        return items

    def draw_block(self, x0, x1, y0, y1, z0, z1):
        glNormal3f(0.0, 0.0, 1.0)
        glTexCoord2f(0, 0); glVertex3f(x0, y0, z1)
        glTexCoord2f(1, 0); glVertex3f(x1, y0, z1)
        glTexCoord2f(1, 1); glVertex3f(x1, y1, z1)
        glTexCoord2f(0, 1); glVertex3f(x0, y1, z1)

        glNormal3f(0.0, 0.0, -1.0)
        glTexCoord2f(1, 0); glVertex3f(x1, y0, z0)
        glTexCoord2f(0, 0); glVertex3f(x0, y0, z0)
        glTexCoord2f(0, 1); glVertex3f(x0, y1, z0)
        glTexCoord2f(1, 1); glVertex3f(x1, y1, z0)

        glNormal3f(-1.0, 0.0, 0.0)
        glTexCoord2f(0, 0); glVertex3f(x0, y0, z0)
        glTexCoord2f(1, 0); glVertex3f(x0, y0, z1)
        glTexCoord2f(1, 1); glVertex3f(x0, y1, z1)
        glTexCoord2f(0, 1); glVertex3f(x0, y1, z0)

        glNormal3f(1.0, 0.0, 0.0)
        glTexCoord2f(0, 0); glVertex3f(x1, y0, z1)
        glTexCoord2f(1, 0); glVertex3f(x1, y0, z0)
        glTexCoord2f(1, 1); glVertex3f(x1, y1, z0)
        glTexCoord2f(0, 1); glVertex3f(x1, y1, z1)

    def draw_sprite(self, x, y, z, player_x, player_z, tex_id, scale=0.5):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE) 

        glPushMatrix()
        glTranslatef(x, y, z)
        dx = player_x - x
        dz = player_z - z
        angle = math.degrees(math.atan2(dx, dz))
        glRotatef(angle, 0.0, 1.0, 0.0)
        
        glScalef(scale, scale, scale)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-1.3,  1.0, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 1.3,  1.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 1.3, -1.0, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-1.3, -1.0, 0.0)
        glEnd()
        glPopMatrix()
        
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
            
    def draw(self, wall_tex_id, floor_tex_id, player_x, player_z, tile_size=2.0, height=2.0, thickness=0.15):
        glColor3f(0.85, 0.85, 0.85) 
        t = thickness 
        
        if floor_tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, floor_tex_id)
        else:
            glDisable(GL_TEXTURE_2D)
            
        glBegin(GL_QUADS)
        for cell in self.grid_cells:
            x0 = cell.x * tile_size
            z0 = cell.y * tile_size
            x1 = x0 + tile_size
            z1 = z0 + tile_size
            y0 = 0.0     

            glNormal3f(0.0, 1.0, 0.0) 
            glTexCoord2f(0.0, 1.0); glVertex3f(x0, y0, z0)
            glTexCoord2f(0.0, 0.0); glVertex3f(x0, y0, z1)
            glTexCoord2f(1.0, 0.0); glVertex3f(x1, y0, z1)
            glTexCoord2f(1.0, 1.0); glVertex3f(x1, y0, z0)
        glEnd()

        if wall_tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, wall_tex_id)
        else:
            glDisable(GL_TEXTURE_2D)
            
        glBegin(GL_QUADS)
        for cell in self.grid_cells:
            x0 = cell.x * tile_size
            z0 = cell.y * tile_size
            x1 = x0 + tile_size
            z1 = z0 + tile_size
            y0 = 0.0     
            y1 = height  

            glNormal3f(0.0, -1.0, 0.0)
            glTexCoord2f(0.0, 1.0); glVertex3f(x0, y1, z0)
            glTexCoord2f(1.0, 1.0); glVertex3f(x1, y1, z0)
            glTexCoord2f(1.0, 0.0); glVertex3f(x1, y1, z1)
            glTexCoord2f(0.0, 0.0); glVertex3f(x0, y1, z1)

            if cell.walls['top']: self.draw_block(x0, x1, y0, y1, z0 - t, z0 + t)
            if cell.walls['bottom']: self.draw_block(x0, x1, y0, y1, z1 - t, z1 + t)
            if cell.walls['left']: self.draw_block(x0 - t, x0 + t, y0, y1, z0, z1)
            if cell.walls['right']: self.draw_block(x1 - t, x1 + t, y0, y1, z0, z1)
        glEnd()

        current_time = time.time()
        for item in self.items_list:
            if not item.collected:
                bobbing_offset = math.sin(current_time * 3.0) * 0.15
                base_y = 0.5 
                draw_y = base_y + bobbing_offset
                self.draw_sprite(item.x, draw_y, item.z, player_x, player_z, item.tex_id, scale=0.3)

        for enemy_obj in self.enemies_list:
            if not enemy_obj.defeated:
                self.draw_sprite(enemy_obj.x, 0.6, enemy_obj.z, player_x, player_z, enemy_obj.tex_id, scale=0.6)

    def minimap(self, player, drac_head_tex, player_head_tex, player_inventory, holy_water_tex, lantern_tex, mirror_tex, display_size=(1100, 800)):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, display_size[0], display_size[1], 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        glColor4f(0.05, 0.05, 0.08, 0.92)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(display_size[0], 0)
        glVertex2f(display_size[0], display_size[1]); glVertex2f(0, display_size[1])
        glEnd()

        map_box_size = 500.0
        map_x0 = (display_size[0] - map_box_size) / 2 - 100 
        map_y0 = (display_size[1] - map_box_size) / 2
        cell_size = map_box_size / self.cols

        glColor3f(0.5, 0.0, 0.12)  # bg color
        glBegin(GL_QUADS)
        for cell in self.grid_cells:
            cx0 = map_x0 + cell.x * cell_size
            cy0 = map_y0 + cell.y * cell_size
            glVertex2f(cx0, cy0); glVertex2f(cx0 + cell_size, cy0)
            glVertex2f(cx0 + cell_size, cy0 + cell_size); glVertex2f(cx0, cy0 + cell_size)
        glEnd()

        glColor3f(1.0, 1.0, 1.0)   # lines
        glLineWidth(4.0)
        glBegin(GL_LINES)
        for cell in self.grid_cells:
            cx0 = map_x0 + cell.x * cell_size
            cy0 = map_y0 + cell.y * cell_size
            cx1 = cx0 + cell_size
            cy1 = cy0 + cell_size
            if cell.walls['top']: glVertex2f(cx0, cy0); glVertex2f(cx1, cy0)
            if cell.walls['bottom']: glVertex2f(cx0, cy1); glVertex2f(cx1, cy1)
            if cell.walls['left']: glVertex2f(cx0, cy0); glVertex2f(cx0, cy1)
            if cell.walls['right']: glVertex2f(cx1, cy0); glVertex2f(cx1, cy1)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1.0, 1.0, 1.0)

        if self.enemies_list and not self.enemies_list[0].defeated:
            drac = self.enemies_list[0]
            dx = map_x0 + (drac.x / self.cell_size) * cell_size
            dy = map_y0 + (drac.z / self.cell_size) * cell_size
            r = 18.0 

            glBindTexture(GL_TEXTURE_2D, drac_head_tex)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(dx - r, dy - r)
            glTexCoord2f(1, 1); glVertex2f(dx + r, dy - r)
            glTexCoord2f(1, 0); glVertex2f(dx + r, dy + r)
            glTexCoord2f(0, 0); glVertex2f(dx - r, dy + r)
            glEnd()

        px = map_x0 + (player.player_x / self.cell_size) * cell_size
        py = map_y0 + (player.player_z / self.cell_size) * cell_size
        pr = 18.0 
        
        glBindTexture(GL_TEXTURE_2D, player_head_tex)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(px - pr, py - pr)
        glTexCoord2f(1, 1); glVertex2f(px + pr, py - pr)
        glTexCoord2f(1, 0); glVertex2f(px + pr, py + pr)
        glTexCoord2f(0, 0); glVertex2f(px - pr, py + pr)
        glEnd()
        
        inv_items = [("-- INVENTORY --", None)]
        if player_inventory and 0 in player_inventory.id:
            inv_items.append(("Lantern", lantern_tex))
        if player_inventory and 1 in player_inventory.id:
            inv_items.append(("[X] Holy Water [X]", holy_water_tex))
        if player_inventory and 2 in player_inventory.id:
            inv_items.append(("[H] Mirror [H]", mirror_tex))
        if len(inv_items) == 1:
            inv_items.append(("Empty", None))
            
        inv_y = map_y0 + 50
        inv_x = map_x0 + map_box_size + 40 
        
        for text, tex in inv_items:
            if tex is not None:
                glBindTexture(GL_TEXTURE_2D, tex)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex2f(inv_x, inv_y - 5)
                glTexCoord2f(1, 1); glVertex2f(inv_x + 35, inv_y - 5)
                glTexCoord2f(1, 0); glVertex2f(inv_x + 35, inv_y + 30)
                glTexCoord2f(0, 0); glVertex2f(inv_x, inv_y + 30)
                glEnd()
                text_offset_x = 45 
            else:
                text_offset_x = 0
                
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            tw, th = text_surface.get_size()
            
            tex_text = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_text)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            tx = inv_x + text_offset_x
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(tx, inv_y)
            glTexCoord2f(1, 1); glVertex2f(tx + tw, inv_y)
            glTexCoord2f(1, 0); glVertex2f(tx + tw, inv_y + th)
            glTexCoord2f(0, 0); glVertex2f(tx, inv_y + th)
            glEnd()
            
            glDeleteTextures(1, [tex_text])
            inv_y += 45
            
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_hud(self, display_size=(1100, 800)):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, display_size[0], display_size[1], 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        bar_height = 40
        glColor3f(0.0, 0.0, 0.0) 
        glBegin(GL_QUADS)
        glVertex2f(0, display_size[1] - bar_height)
        glVertex2f(display_size[0], display_size[1] - bar_height)
        glVertex2f(display_size[0], display_size[1])
        glVertex2f(0, display_size[1])
        glEnd()

        mins, secs = divmod(self.elapsed_time, 60) # timer and bottom bar
        time_str = f"Time: {int(mins):02d}:{secs:05.2f}    |    Press 'N' to Get a New Map    |    Press 'R' to Restart    |    Press 'M' for Map"
        
        text_surface = self.font.render(time_str, True, (255, 255, 255), (0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tw, th = text_surface.get_size()
        
        if self.text_texture is None:
            self.text_texture = glGenTextures(1)
            
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.text_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        tx = (display_size[0] - tw) // 2
        ty = display_size[1] - bar_height + (bar_height - th) // 2
        
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(tx, ty)
        glTexCoord2f(1, 1); glVertex2f(tx + tw, ty)
        glTexCoord2f(1, 0); glVertex2f(tx + tw, ty + th)
        glTexCoord2f(0, 0); glVertex2f(tx, ty + th)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()