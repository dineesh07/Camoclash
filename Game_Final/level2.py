import pygame
import random
import os

# ----- CONFIG -----
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 80
GRAVITY = 0.5
JUMP_STRENGTH = 5  # Lowered for gentler jetpack ascent

# ----- INIT -----
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level 2 - Mario Style")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

gameover_img = pygame.image.load("wegotyou.png").convert_alpha()
gameover_img = pygame.transform.scale(gameover_img, (400, 300))

# ----- IMAGES -----
player_img = pygame.image.load("jetpack-.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (80, 80))

if os.path.exists("question_box.png"):
    question_box_img = pygame.image.load("question_box.png").convert_alpha()
else:
    question_box_img = None

# ----- PARALLAX BACKGROUND CLASS -----
class ParallaxBackground:
    def __init__(self, image1, image2):
        self.image1 = pygame.image.load(image1).convert()
        self.image2 = pygame.image.load(image2).convert()
        self.image1 = pygame.transform.scale(self.image1, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image2 = pygame.transform.scale(self.image2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.x1 = 0
        self.x2 = SCREEN_WIDTH
        self.speed = 2

    def update(self, player_movement):
        self.x1 -= player_movement
        self.x2 -= player_movement
        if self.x1 <= -SCREEN_WIDTH:
            self.x1 = self.x2 + SCREEN_WIDTH
        if self.x2 <= -SCREEN_WIDTH:
            self.x2 = self.x1 + SCREEN_WIDTH
        if self.x1 >= SCREEN_WIDTH:
            self.x1 = self.x2 - SCREEN_WIDTH
        if self.x2 >= SCREEN_WIDTH:
            self.x2 = self.x1 - SCREEN_WIDTH

    def draw(self, surface):
        surface.blit(self.image1, (self.x1, 0))
        surface.blit(self.image2, (self.x2, 0))

# Initialize parallax background
parallax_bg = ParallaxBackground("bgrun.jpg", "bgrun.jpg")

# ----- PLAYER -----
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.velocity_y = 0
        self.on_ground = True

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.x += 3  # Reduced speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= 3  # Reduced speed
        if keys[pygame.K_SPACE]:
            self.velocity_y -= 0.3  # Smoothly accelerate upward while space is pressed
            if self.velocity_y < -JUMP_STRENGTH:
                self.velocity_y = -JUMP_STRENGTH
        else:
            self.velocity_y += GRAVITY  # Descend when space is not pressed


        # Ensure player stays within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        self.rect.y += self.velocity_y

        if self.rect.top < 0:
            self.rect.top = 0
            if self.velocity_y < 0:
                self.velocity_y = 0

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if self.velocity_y > 0:
                self.velocity_y = 0


# ----- OBSTACLE CLASS -----
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, top=False):
        super().__init__()
        if top and os.path.exists("obstacle top.png"):
            self.image = pygame.image.load("obstacle top.png").convert_alpha()
        else:
            self.image = pygame.image.load("obstacle.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        if top:
            self.rect = self.image.get_rect(midtop=(x, 0))
        else:
            self.rect = self.image.get_rect(midbottom=(x, SCREEN_HEIGHT))

    def update(self):
        self.rect.x -= 3
        if self.rect.right < 0:
            self.kill()

# ----- ANSWER COIN CLASS -----
class AnswerCoin(pygame.sprite.Sprite):
    def __init__(self, x, y, answer, is_correct):
        super().__init__()
        if os.path.exists("chamion.png"):
            self.image = pygame.image.load("chamion.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 80))
        else:
            self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (40, 40), 40)
        self.rect = self.image.get_rect(center=(x, y))
        self.answer = answer
        self.is_correct = is_correct

    def update(self):
        self.rect.x -= 3
        if self.rect.right < 0:
            self.kill()

    def draw_with_text(self, surface, font):
        surface.blit(self.image, self.rect)
        text = font.render(str(self.answer), True, (255, 255, 255))  # White color
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

# ----- QUESTION GENERATORS -----
def generate_math_question():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    correct = num1 + num2
    question_text = f"{num1} + {num2} = ?"
    answers = [correct]
    while len(answers) < 3:
        wrong = correct + random.choice([-3, -2, -1, 1, 2, 3])
        if wrong not in answers and wrong > 0:
            answers.append(wrong)
    random.shuffle(answers)
    return question_text, answers, correct

def generate_unemployed_addition_question():
    num = random.randint(5, 15)
    unknown = random.randint(1, num - 1)
    correct = num - unknown
    question_text = f"X + {unknown} = {num} (Find X)"
    answers = [correct]
    while len(answers) < 3:
        wrong = correct + random.choice([-3, -2, -1, 1, 2, 3])
        if wrong not in answers and wrong > 0:
            answers.append(wrong)
    random.shuffle(answers)
    return question_text, answers, correct

def generate_chemical_equation():
    equations = [
        ("H2 + O2 → ?", "H2O"),
        ("CO2 + H2O → ? + O2", "C6H12O6"),
        ("Na + Cl2 → ?", "NaCl"),
        ("CaO + H2O → ?", "Ca(OH)2")
    ]
    eq, correct = random.choice(equations)
    question_text = f"What is the product of this reaction: {eq}?"
    wrongs = [e[1] for e in equations if e[1] != correct]
    random.shuffle(wrongs)
    answers = [correct] + wrongs[:2]
    random.shuffle(answers)
    return question_text, answers, correct

def new_question():
    question_type = random.choice(["math", "chemical", "unemployed_addition"])
    if question_type == "math":
        return generate_math_question()
    elif question_type == "chemical":
        return generate_chemical_equation()
    else:
        return generate_unemployed_addition_question()

# ----- GAME SETUP -----
import os
player = Player()
player_group = pygame.sprite.GroupSingle(player)

obstacles = pygame.sprite.Group()
top_obstacles = pygame.sprite.Group()  # Group for top obstacles
coins = pygame.sprite.Group()

score = 0
high_score = 60
health = 100  # Health ranges from 0 to 100
MAX_HEALTH = 100

# Initialize first question
question, answers, correct = new_question()

# Add initial ground obstacles
for i in range(3):
    obstacle = Obstacle(SCREEN_WIDTH + i * 350)
    obstacles.add(obstacle)
# Add initial top obstacle
for i in range(1):
    top_obstacle = Obstacle(SCREEN_WIDTH + 600, top=True)
    top_obstacles.add(top_obstacle)

# Add answer coins (in the air)
coin_y_positions = [200, 300, 400]
for i, ans in enumerate(answers):
    coin = AnswerCoin(SCREEN_WIDTH + 200 + i * 220, coin_y_positions[i % len(coin_y_positions)], ans, ans == correct)
    coins.add(coin)

# ----- MAIN LOOP -----
def main_loop():
    global score, high_score, question, answers, correct, health
    running = True
    obstacle_timer = 0
    coin_timer = 0
    top_obstacle_timer = 0
    OBSTACLE_INTERVAL = 80  # frames
    TOP_OBSTACLE_INTERVAL = 300  # ~5 seconds at 60 FPS
    COIN_INTERVAL = 90      # frames
    coin_y_positions = [200, 300, 400]
    show_gameover = False
    gameover_timer = 0
    while running:
        player_movement = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player_movement = 3
        if keys[pygame.K_LEFT]:
            player_movement = -3

        parallax_bg.update(player_movement)
        screen.fill((0, 0, 0))
        parallax_bg.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_group.update()
        player_group.draw(screen)

        # Spawn obstacles at intervals
        obstacle_timer += 1
        if obstacle_timer >= OBSTACLE_INTERVAL:
            obstacles.add(Obstacle(SCREEN_WIDTH + 10))
            obstacle_timer = 0

        # Spawn top obstacles at intervals
        top_obstacle_timer += 1
        if top_obstacle_timer >= TOP_OBSTACLE_INTERVAL:
            top_obs = Obstacle(SCREEN_WIDTH + 10, top=True)
            top_obstacles.add(top_obs)
            top_obstacle_timer = 0
        # Spawn answer coins at intervals (for current question)
        coin_timer += 1
        if coin_timer >= COIN_INTERVAL:
            # Cycle through answers, spawn one at a time
            if not hasattr(main_loop, 'coin_answer_idx'):
                main_loop.coin_answer_idx = 0
            ans = answers[main_loop.coin_answer_idx % len(answers)]
            y = coin_y_positions[main_loop.coin_answer_idx % len(coin_y_positions)]
            coins.add(AnswerCoin(SCREEN_WIDTH + 100, y, ans, ans == correct))
            main_loop.coin_answer_idx += 1
            coin_timer = 0

        # Draw and update ground obstacles
        for obstacle in obstacles:
            obstacle.update()
            screen.blit(obstacle.image, obstacle.rect)

        # Draw and update top obstacles
        for top_obs in top_obstacles:
            top_obs.update()
            screen.blit(top_obs.image, top_obs.rect)

        # Draw and update answer coins
        for coin in coins:
            coin.update()
            coin.draw_with_text(screen, font)

        # Check for collisions with coins (answers)
        coin_collided = pygame.sprite.spritecollide(player, coins, False)
        if coin_collided:
            for coin in coin_collided:
                if coin.is_correct:
                    score += 10
                    health = min(health + 10, MAX_HEALTH)  # Increase health by 10, max 100
                    if score > high_score:
                        high_score = score
                    # Generate new question and reset timers
                    question, answers, correct = new_question()
                    coins.empty()
                    obstacle_timer = 0
                    coin_timer = 0
                    main_loop.coin_answer_idx = 0
                else:
                    health -= 20  # Decrease health by 20 on wrong coin
                    if health < 0:
                        health = 0
                coin.kill()  # Remove collected coin (even if wrong)
                break

        # End game if health is zero
        if health <= 0:
            running = False

        # Check for collisions with obstacles or health reaches 0 (ends game)
        if not show_gameover and (pygame.sprite.spritecollide(player, obstacles, False) or pygame.sprite.spritecollide(player, top_obstacles, False) or health <= 0):
            # Show game over image and exit immediately
            img_rect = gameover_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(gameover_img, img_rect)
            pygame.display.update()
            pygame.time.wait(2000)
            pygame.quit()
            exit()

        # Draw HUD
        score_text = font.render(f"Score: {score}   High Score: {high_score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Draw question box image behind question, dynamically sized to fit text
        question_text = font.render(f"Question: {question}", True, (0, 0, 0))
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        padding_x = 32
        padding_y = 16
        box_width = question_rect.width + padding_x * 2
        box_height = question_rect.height + padding_y * 2
        box_x = question_rect.centerx - box_width // 2
        box_y = question_rect.centery - box_height // 2
        # Draw question box image behind question, no shadow, fully transparent background
        if question_box_img:
            scaled_box_img = pygame.transform.smoothscale(question_box_img, (box_width, box_height))
            box_rect = scaled_box_img.get_rect(center=question_rect.center)
            screen.blit(scaled_box_img, box_rect)
        else:
            # Draw a semi-transparent light box with border
            s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            s.fill((255, 255, 230, 200))  # Light color, 200 alpha for transparency
            screen.blit(s, (box_x, box_y))
            pygame.draw.rect(screen, (180, 180, 140), (box_x, box_y, box_width, box_height), 4, border_radius=18)
        # Draw question text on top
        screen.blit(question_text, question_rect)

        # Draw Health Bar further down
        health_bar_width = 200
        health_bar_height = 25
        health_bar_x = 10
        health_bar_y = 85  # Moved further down to avoid overlap
        pygame.draw.rect(screen, (180, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))  # Background
        pygame.draw.rect(screen, (0, 220, 0), (health_bar_x, health_bar_y, int(health_bar_width * health / MAX_HEALTH), health_bar_height))  # Current health
        pygame.draw.rect(screen, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)  # Border
        health_text = font.render(f"Health: {health}", True, (0, 0, 0))
        screen.blit(health_text, (health_bar_x + 60, health_bar_y + 1))

        # Show Game Over image if needed
        if show_gameover:
            img_rect = gameover_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(gameover_img, img_rect)
            pygame.display.update()
            # Wait 2 seconds, then exit loop
            if pygame.time.get_ticks() - gameover_timer > 2000:
                pygame.quit()
                exit()
            continue

        pygame.display.update()
        clock.tick(60)

main_loop()
pygame.quit()
