import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Team Smileys")

# Colors
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize font
pygame.font.init()
SCORE_FONT = pygame.font.Font(None, 74)
WIN_FONT = pygame.font.Font(None, 100)

class Obstacle:
    def __init__(self, x, y, size, is_circle):
        self.x = x
        self.y = y
        self.size = size
        self.is_circle = is_circle
        self.created_time = time.time()
        self.lifetime = random.uniform(2, 4)  # Obstacles last 2-4 seconds
        
    def draw(self, screen):
        if self.is_circle:
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size)
        else:
            rect = pygame.Rect(self.x - self.size, self.y - self.size, 
                             self.size * 2, self.size * 2)
            pygame.draw.rect(screen, RED, rect)
            
    def check_collision(self, ball):
        if self.is_circle:
            # Circle collision
            dx = ball.x - self.x
            dy = ball.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            return distance < (ball.radius + self.size)
        else:
            # Square collision
            return (abs(ball.x - self.x) < (ball.radius + self.size) and 
                   abs(ball.y - self.y) < (ball.radius + self.size))

class Ball:
    def __init__(self):
        self.radius = 15
        self.speed = 12  # Reduced speed from 18 to 12
        self.reset_position()
        
    def reset_position(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        # Generate random direction but maintain constant speed
        angle = random.uniform(0, 2 * math.pi)
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)
        
    def move(self, smileys, obstacles):
        # Update position
        self.x += self.dx
        self.y += self.dy
        
        # Check wall collisions
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.dx *= -1
        if self.y - self.radius < 0:
            self.y = self.radius
            self.dy *= -1
            return True  # Hit top wall
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.dy *= -1
            return False  # Hit bottom wall
            
        # Check collision with smileys
        for smiley in smileys:
            # Calculate distance between ball and smiley
            dx = self.x - smiley.x
            dy = self.y - smiley.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If collision occurs
            if distance < self.radius + smiley.radius:
                # Calculate collision normal
                nx = dx / distance
                ny = dy / distance
                
                # Reflect velocity
                dot_product = self.dx * nx + self.dy * ny
                self.dx = self.dx - 2 * dot_product * nx
                self.dy = self.dy - 2 * dot_product * ny
                
                # Move ball out of collision
                overlap = (self.radius + smiley.radius - distance) / 2
                self.x += nx * overlap
                self.y += ny * overlap
                
        # Check collision with obstacles
        for obstacle in obstacles:
            if obstacle.check_collision(self):
                if obstacle.is_circle:
                    # Circle collision
                    dx = self.x - obstacle.x
                    dy = self.y - obstacle.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    nx = dx / distance
                    ny = dy / distance
                else:
                    # Square collision
                    if abs(self.x - obstacle.x) > abs(self.y - obstacle.y):
                        nx = 1 if self.x > obstacle.x else -1
                        ny = 0
                    else:
                        nx = 0
                        ny = 1 if self.y > obstacle.y else -1
                
                # Reflect velocity
                dot_product = self.dx * nx + self.dy * ny
                self.dx = self.dx - 2 * dot_product * nx
                self.dy = self.dy - 2 * dot_product * ny
                
                # Move ball out of collision
                overlap = (self.radius + obstacle.size - abs(self.x - obstacle.x)) / 2
                self.x += nx * overlap
                self.y += ny * overlap
        return None  # No wall hit
            
    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius)

class Smiley:
    def __init__(self, x, y, color, is_top_team):
        self.base_radius = 30  # Store the original radius
        self.radius = self.base_radius  # Current radius
        self.x = x
        self.y = y
        self.color = color
        self.speed = 5
        self.dx = 0
        self.is_top_team = is_top_team
        self.target_x = x
        
    def set_size_multiplier(self, multiplier):
        self.radius = int(self.base_radius * multiplier)  # Ensure radius is an integer
        
    def move(self, ball):
        # Calculate predicted ball position
        if ball.dy != 0:  # Avoid division by zero
            time_to_wall = (self.y - ball.y) / ball.dy
            predicted_x = ball.x + ball.dx * time_to_wall
            
            # Keep the smiley within screen bounds
            predicted_x = max(self.radius, min(WIDTH - self.radius, predicted_x))
            
            # Move towards predicted position
            if abs(self.x - predicted_x) > self.speed:
                self.dx = self.speed if predicted_x > self.x else -self.speed
            else:
                self.dx = 0
        else:
            # If ball is moving horizontally, just follow it
            if abs(self.x - ball.x) > self.speed:
                self.dx = self.speed if ball.x > self.x else -self.speed
            else:
                self.dx = 0
        
        # Update position
        self.x += self.dx
        
        # Keep smiley within screen bounds
        if self.x - self.radius < 0:
            self.x = self.radius
            self.dx = 0
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.dx = 0
            
    def draw(self, screen):
        # Draw face circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw eyes
        eye_radius = 5
        left_eye_x = self.x - 10
        right_eye_x = self.x + 10
        eye_y = self.y - 5
        pygame.draw.circle(screen, BLACK, (int(left_eye_x), int(eye_y)), eye_radius)
        pygame.draw.circle(screen, BLACK, (int(right_eye_x), int(eye_y)), eye_radius)
        
        # Draw smile
        smile_radius = 15
        smile_start = math.pi
        smile_end = 2 * math.pi
        pygame.draw.arc(screen, BLACK, (self.x - smile_radius, self.y - smile_radius,
                                      smile_radius * 2, smile_radius * 2),
                       smile_start, smile_end, 3)

class Game:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        # Create teams of smileys
        self.top_team = [
            Smiley(WIDTH // 2, 50, YELLOW, True)  # Single smiley at top
        ]
        
        self.bottom_team = [
            Smiley(WIDTH // 2, HEIGHT - 50, YELLOW, False)  # Single smiley at bottom
        ]
        
        # Create the orange ball
        self.ball = Ball()
        
        # List to store obstacles
        self.obstacles = []
        self.last_obstacle_time = time.time()
        
        # Initialize scores
        self.top_score = 0
        self.bottom_score = 0
        
        # Game state
        self.winner = None  # None = playing, "top" = top won, "bottom" = bottom won
        self.win_time = 0  # When the game was won
        
    def check_win_condition(self):
        if self.top_score >= 10:
            self.winner = "top"
            self.win_time = time.time()
        elif self.bottom_score >= 10:
            self.winner = "bottom"
            self.win_time = time.time()
                
    def update(self):
        # Update obstacles
        current_time = time.time()
        
        # Remove old obstacles
        self.obstacles = [obs for obs in self.obstacles if current_time - obs.created_time < obs.lifetime]
        
        # Add new obstacles randomly
        if current_time - self.last_obstacle_time > 0.5:  # Add new obstacle every 0.5 seconds
            if random.random() < 0.3:  # 30% chance to add an obstacle
                size = random.randint(10, 30)
                x = random.randint(size, WIDTH - size)
                y = random.randint(size, HEIGHT - size)
                is_circle = random.random() < 0.5
                self.obstacles.append(Obstacle(x, y, size, is_circle))
                self.last_obstacle_time = current_time
                
        # Only update game elements if there's no winner
        if not self.winner:
            # Update
            for smiley in self.top_team + self.bottom_team:
                smiley.move(self.ball)
            
            # Update ball position and check collisions
            wall_hit = self.ball.move(self.top_team + self.bottom_team, self.obstacles)
            if wall_hit is True:  # Hit top wall
                self.bottom_score += 1
                self.ball.reset_position()
            elif wall_hit is False:  # Hit bottom wall
                self.top_score += 1
                self.ball.reset_position()
                
            # Check win condition
            self.check_win_condition()
        else:
            # Reset game after 5 seconds of win
            if current_time - self.win_time > 5:
                self.reset_game()
            
    def draw(self, screen):
        screen.fill((255, 255, 255))  # White background
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Draw all smileys
        for smiley in self.top_team + self.bottom_team:
            smiley.draw(screen)
        
        # Draw the ball
        self.ball.draw(screen)
        
        # Draw scores
        top_text = SCORE_FONT.render(str(self.top_score), True, BLACK)
        bottom_text = SCORE_FONT.render(str(self.bottom_score), True, BLACK)
        
        screen.blit(top_text, (WIDTH//2 - top_text.get_width()//2, 20))
        screen.blit(bottom_text, (WIDTH//2 - bottom_text.get_width()//2, HEIGHT - 60))
        
        # Draw winner text
        if self.winner:
            if self.winner == "top":
                win_text = WIN_FONT.render("TOP WINS!", True, BLACK)
            else:
                win_text = WIN_FONT.render("BOTTOM WINS!", True, BLACK)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))

# Create game instance
game = Game()

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Update game state
    game.update()
    
    # Draw everything
    game.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 