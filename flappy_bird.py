import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BIRD_SIZE = 30
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_SPEED = 3
GRAVITY = 0.5
JUMP_STRENGTH = -8
BIRD_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity_y = 0
        self.size = BIRD_SIZE
        
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Keep bird on screen
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity_y = 0
    
    def jump(self):
        self.velocity_y = JUMP_STRENGTH
    
    def move_up(self):
        self.y -= BIRD_SPEED
        if self.y < 0:
            self.y = 0
    
    def move_down(self):
        self.y += BIRD_SPEED
        if self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size//2), int(self.y + self.size//2)), self.size//2)
        # Draw eye
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size//2 + 5), int(self.y + self.size//2 - 5)), 3)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.width = PIPE_WIDTH
        self.passed = False
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP)
        return top_rect, bottom_rect
    
    def draw(self, screen):
        top_rect, bottom_rect = self.get_rects()
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, GREEN, bottom_rect)
        # Draw pipe borders
        pygame.draw.rect(screen, BLACK, top_rect, 2)
        pygame.draw.rect(screen, BLACK, bottom_rect, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.reset_game()
        
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.pipe_timer = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    if self.game_state == "menu" or self.game_state == "game_over":
                        self.reset_game()
                        self.game_state = "playing"
                elif event.key == pygame.K_BACKSPACE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "playing":
                        self.bird.jump()
        
        # Handle continuous key presses for arrow keys
        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.bird.move_up()
            if keys[pygame.K_DOWN]:
                self.bird.move_down()
        
        return True
    
    def update(self):
        if self.game_state != "playing":
            return
            
        # Update bird
        self.bird.update()
        
        # Generate pipes
        self.pipe_timer += 1
        if self.pipe_timer > 120:  # New pipe every 2 seconds at 60 FPS
            self.pipes.append(Pipe(SCREEN_WIDTH))
            self.pipe_timer = 0
        
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
            
            # Check for scoring
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
        
        # Check collisions
        bird_rect = self.bird.get_rect()
        
        # Check pipe collisions
        for pipe in self.pipes:
            top_rect, bottom_rect = pipe.get_rects()
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                self.game_state = "game_over"
        
        # Check ground/ceiling collision
        if self.bird.y <= 0 or self.bird.y >= SCREEN_HEIGHT - self.bird.size:
            self.game_state = "game_over"
    
    def draw(self):
        self.screen.fill(BLUE)
        
        if self.game_state == "menu":
            title_text = self.big_font.render("FLAPPY BIRD", True, WHITE)
            start_text = self.font.render("Press ENTER to Start", True, WHITE)
            controls_text = [
                "Controls:",
                "SPACE - Jump",
                "UP/DOWN Arrows - Move",
                "BACKSPACE - Pause",
                "ESCAPE - Exit"
            ]
            
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 150))
            self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 250))
            
            for i, control in enumerate(controls_text):
                text = self.font.render(control, True, WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 320 + i * 30))
        
        elif self.game_state == "playing" or self.game_state == "paused":
            # Draw pipes
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            # Draw bird
            self.bird.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw pause overlay
            if self.game_state == "paused":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.big_font.render("PAUSED", True, WHITE)
                resume_text = self.font.render("Press BACKSPACE to Resume", True, WHITE)
                self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        elif self.game_state == "game_over":
            # Draw final game state
            for pipe in self.pipes:
                pipe.draw(self.screen)
            self.bird.draw(self.screen)
            
            # Draw game over overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press ENTER to Play Again", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
