# -*- coding: utf-8 -*-

import pygame
import numpy as np
import time
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1000, 800
BG_COLOR = (10, 10, 15) # Deep Bio-Dark
FPS = 60

# Brainwave Colors (Scientific & Aesthetic)
COLORS = {
    'delta': (50, 50, 150),   # Deep Sleep (Blue)
    'theta': (100, 0, 150),   # Dreaming/Flow (Purple)
    'alpha': (0, 200, 255),   # Focus/Calm (Cyan)
    'beta':  (255, 200, 0),   # Active/Anxious (Gold)
    'gamma': (255, 50, 50)    # High Insight (Red)
}

class BrainwaveSimulator:
    """Simulates realistic EEG data using superimposed sine waves + noise"""
    def __init__(self):
        self.start_time = time.time()

    def get_power_spectrum(self):
        t = time.time() - self.start_time
        # Create organic fluctuating values using sine wave superposition
        # We simulate "Power" (amplitude) of each band

        delta = (math.sin(t * 0.5) + 1) * 20 + np.random.normal(0, 2)
        theta = (math.sin(t * 1.2) + 1) * 15 + np.random.normal(0, 2)
        alpha = (math.sin(t * 2.5) + 1) * 30 + (math.sin(t * 0.2)*10) # Alpha pulses slowly
        beta  = (math.sin(t * 5.0) + 1) * 10 + np.random.normal(0, 5) # Beta is jittery
        gamma = (math.sin(t * 8.0) + 1) * 5

        return {
            'delta': max(0.1, delta),
            'theta': max(0.1, theta),
            'alpha': max(0.1, alpha),
            'beta':  max(0.1, beta),
            'gamma': max(0.1, gamma)
        }

def draw_glow_circle(surface, color, center, radius, width=2):
    """Draws a circle with a glow effect"""
    # Main ring
    pygame.draw.circle(surface, color, center, int(radius), width)
    # Glow (simulated by transparent surfaces)
    if radius > 4:
        s = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        # Create a faded color
        glow_color = (*color, 30) # Low alpha
        pygame.draw.circle(s, glow_color, (radius+5, radius+5), int(radius), width+4)
        surface.blit(s, (center[0] - radius - 5, center[1] - radius - 5))

# --- MAIN LOOP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Day 1: The Cognitive Symphony")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18)

simulator = BrainwaveSimulator()

# History for trail effect
history = []

running = True
while running:
    screen.fill(BG_COLOR)
    center = (WIDTH // 2, HEIGHT // 2)

    # 1. Get Data
    bands = simulator.get_power_spectrum()

    # 2. Visualize - Concentric "Symphony" Rings
    # The radius represents the Frequency Band
    # The thickness/brightness represents the Power (Activity)

    # DELTA (Core)
    draw_glow_circle(screen, COLORS['delta'], center, 50 + bands['delta'], width=int(bands['delta']/5))

    # THETA
    draw_glow_circle(screen, COLORS['theta'], center, 120 + bands['theta'], width=int(bands['theta']/4))

    # ALPHA (The Main Focus Ring)
    # Alpha also rotates to show "Flow"
    alpha_rad = 200 + bands['alpha']
    draw_glow_circle(screen, COLORS['alpha'], center, alpha_rad, width=int(bands['alpha']/3))

    # BETA (Outer fast ring)
    beta_rad = 300 + bands['beta']
    draw_glow_circle(screen, COLORS['beta'], center, beta_rad, width=2)

    # GAMMA (The Insight Spikes)
    # Draw lines radiating out based on Gamma power
    if bands['gamma'] > 5:
        for i in range(0, 360, 10):
            rad = math.radians(i + time.time()*50) # Rotate
            start_x = center[0] + math.cos(rad) * 320
            start_y = center[1] + math.sin(rad) * 320
            end_x = center[0] + math.cos(rad) * (320 + bands['gamma']*3)
            end_y = center[1] + math.sin(rad) * (320 + bands['gamma']*3)
            pygame.draw.line(screen, COLORS['gamma'], (start_x, start_y), (end_x, end_y), 2)

    # 3. Dynamic Text Info
    y_offset = HEIGHT - 150
    for band, value in bands.items():
        # Draw bars
        bar_len = int(value * 3)
        pygame.draw.rect(screen, COLORS[band], (50, y_offset, bar_len, 10))
        text = font.render(f"{band.upper()}: {value:.1f} Hz", True, (200, 200, 200))
        screen.blit(text, (50, y_offset - 20))
        y_offset += 30

    # 4. Central "Mind" Particle
    # A single dot in the center that breathes with Alpha (Focus)
    pygame.draw.circle(screen, (255, 255, 255), center, int(bands['alpha'] / 5))

    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
