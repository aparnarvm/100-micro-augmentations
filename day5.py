# -*- coding: utf-8 -*-
"""
PROJECT: SIGNAL HUNTER (Day 5)
TYPE: Visual Search / Oddball Paradigm
TARGET: Visual Cortex (V4) & Parietal Lobe
"""

import pygame
import random
import time

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (5, 5, 10)
UI_COLOR = (0, 255, 255)     # Cyan (Interface)
ACCENT_COLOR = (255, 215, 0) # Gold (Level)
ERROR_COLOR = (255, 50, 50)  # Red (Fail)
SUCCESS_COLOR = (0, 255, 128) # Bright Green (Win)

# GAME SETTINGS
GRID_PADDING = 100
BASE_TIME = 5.0 
MAX_LEVELS = 15  # <--- GAME ENDS HERE

class Shape:
    def __init__(self, x, y, size, shape_type, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.shape_type = shape_type 
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.is_target = False

    def draw(self, surface):
        center = (self.rect.centerx, self.rect.centery)
        radius = self.size // 2
        
        if self.shape_type == 'square':
            pygame.draw.rect(surface, self.color, self.rect)
        elif self.shape_type == 'circle':
            pygame.draw.circle(surface, self.color, center, radius)
        elif self.shape_type == 'triangle':
            p1 = (self.x + self.size//2, self.y)
            p2 = (self.x, self.y + self.size)
            p3 = (self.x + self.size, self.y + self.size)
            pygame.draw.polygon(surface, self.color, [p1, p2, p3])
            
    def is_clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)

class GameState:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.grid_size = 2 
        self.shapes = []
        self.target = None
        self.start_time = 0
        self.time_limit = BASE_TIME
        self.game_over = False
        self.won = False  # <--- New Win Flag
        self.feedback = ""
        self.feedback_color = UI_COLOR

    def generate_level(self):
        self.shapes = []
        # Increase difficulty
        self.grid_size = 3 + (self.level // 2) 
        self.time_limit = max(1.5, BASE_TIME - (self.level * 0.2)) 
        
        available_w = WIDTH - (GRID_PADDING * 2)
        available_h = HEIGHT - (GRID_PADDING * 2)
        cell_size = min(available_w // self.grid_size, available_h // self.grid_size)
        padding = 10
        actual_size = cell_size - padding
        
        # Difficulty Logic
        c1 = (0, 255, 128) # Green
        c2 = (255, 50, 80) # Red
        
        distractor_props = {'type': 'square', 'color': c1}
        target_props = {'type': 'circle', 'color': c1}
        
        if self.level > 3: target_props = {'type': 'square', 'color': c2}
        if self.level > 6:
            distractor_props = {'type': 'random', 'color': 'random'}
            target_props = {'type': 'triangle', 'color': (50, 100, 255)} 
        
        total_cells = self.grid_size * self.grid_size
        target_idx = random.randint(0, total_cells - 1)
        
        for i in range(total_cells):
            row = i // self.grid_size
            col = i % self.grid_size
            x = GRID_PADDING + (col * cell_size) + padding//2
            y = GRID_PADDING + (row * cell_size) + padding//2
            
            if i == target_idx:
                s = Shape(x, y, actual_size, target_props['type'], target_props['color'])
                s.is_target = True
                self.target = s
                self.shapes.append(s)
            else:
                st = distractor_props['type']
                sc = distractor_props['color']
                if st == 'random': st = random.choice(['square', 'circle'])
                if sc == 'random': sc = random.choice([c1, c2])
                s = Shape(x, y, actual_size, st, sc)
                self.shapes.append(s)
                
        self.start_time = time.time()

# --- MAIN SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PROTOCOL: VISUAL SEARCH // Day 5")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 24, bold=True)
font_big = pygame.font.SysFont("monospace", 60, bold=True)
font_huge = pygame.font.SysFont("monospace", 80, bold=True)

game = GameState()
game.generate_level()

running = True
while running:
    screen.fill(BG_COLOR)
    
    # Check Time (Only if game is active)
    if not game.game_over:
        elapsed = time.time() - game.start_time
        remaining = game.time_limit - elapsed
        if remaining <= 0:
            game.game_over = True
            game.feedback = "TIME BREACH // SIGNAL LOST"
            game.feedback_color = ERROR_COLOR

    # --- EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
            mx, my = pygame.mouse.get_pos()
            
            for s in game.shapes:
                if s.is_clicked(mx, my):
                    if s.is_target:
                        # SUCCESS Logic
                        game.score += 100 + int(remaining * 100)
                        
                        # Check for WIN CONDITION
                        if game.level >= MAX_LEVELS:
                            game.game_over = True
                            game.won = True
                        else:
                            game.level += 1
                            game.generate_level()
                    else:
                        # FAIL Logic
                        game.game_over = True
                        game.feedback = "WRONG TARGET SELECTED"
                        game.feedback_color = ERROR_COLOR
                    break

    # --- DRAWING ---
    if not game.game_over:
        # 1. Gameplay Mode
        for s in game.shapes:
            s.draw(screen)
            
        timer_width = (remaining / game.time_limit) * WIDTH
        pygame.draw.rect(screen, game.feedback_color, (0, 0, timer_width, 10))
        
        level_txt = font.render(f"LEVEL: {game.level}/{MAX_LEVELS}", True, ACCENT_COLOR)
        score_txt = font.render(f"SCORE: {game.score}", True, UI_COLOR)
        screen.blit(level_txt, (20, 20))
        screen.blit(score_txt, (WIDTH - 200, 20))
        
    else:
        # 2. End Screen Mode
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        if game.won:
            # WIN SCREEN
            t1 = font_huge.render("SEARCH SUCCESSFUL", True, SUCCESS_COLOR)
            t2 = font.render(f"ALL {MAX_LEVELS} TARGETS ACQUIRED", True, UI_COLOR)
            t3 = font.render(f"FINAL SCORE: {game.score}", True, ACCENT_COLOR)
            t4 = font_big.render("OPTICAL FILTERS: OPTIMIZED", True, (255, 255, 255))
            
            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))
            screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 60))
            screen.blit(t4, (WIDTH//2 - t4.get_width()//2, HEIGHT//2 + 150))
            
        else:
            # LOSE SCREEN
            t1 = font_huge.render("SEARCH FAILED", True, ERROR_COLOR)
            t2 = font.render(f"ELIMINATED AT LEVEL {game.level}", True, UI_COLOR)
            t3 = font.render(game.feedback, True, ACCENT_COLOR)
            
            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 50))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))
            screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
