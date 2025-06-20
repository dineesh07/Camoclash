import pygame
import random
import math

# ----- CONFIG -----
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BRANCH_Y_POSITION = 100
SWING_RADIUS = 100
SWING_SPEED = 0.00
PLAYER_SIZE = 100
GRAVITY = 0.02
MAX_DESCEND_SPEED = 0.5
ANIMAL_SIZE = 60
GROUND_Y_POSITION = SCREEN_HEIGHT - 40

# ----- INIT -----
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Swinging Branches with Insects")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
bold_font = pygame.font.SysFont("arial", 24, bold=True)
question_font = pygame.font.SysFont("arial", 18)

# ----- IMAGES -----
background_img = pygame.image.load("bg.png").convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

congrats_img = pygame.image.load("congrats.jpeg").convert_alpha()
congrats_img = pygame.transform.scale(congrats_img, (400, 300))

gameover_img = pygame.image.load("wegotyou.png").convert_alpha()
gameover_img = pygame.transform.scale(gameover_img, (400, 300))

import os
if os.path.exists("question_box.png"):
    question_box_img = pygame.image.load("question_box.png").convert_alpha()
else:
    question_box_img = None

# ----- PLAYER -----
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.angle = math.pi / 2
        self.swing_speed = SWING_SPEED
        self.descend_speed = 0

        self.swing_img = pygame.image.load("normal.png").convert_alpha()
        self.descend_img = pygame.image.load("open.png").convert_alpha()

        self.swing_img = pygame.transform.scale(self.swing_img, (PLAYER_SIZE, PLAYER_SIZE))
        self.descend_img = pygame.transform.scale(self.descend_img, (PLAYER_SIZE, PLAYER_SIZE))

        self.image = self.swing_img
        self.rect = self.image.get_rect(center=(400, BRANCH_Y_POSITION))

    def update_position(self):
        cx = 400
        cy = BRANCH_Y_POSITION if self.descend_speed == 0 else self.rect.centery
        self.rect.centerx = cx + SWING_RADIUS * math.cos(self.angle)
        self.rect.centery = cy + SWING_RADIUS * math.sin(self.angle)

    def update(self):
        if self.descend_speed == 0:
            self.angle += self.swing_speed
            if self.angle > 1.5 or self.angle < 0.5:
                self.swing_speed = -self.swing_speed
        else:
            self.rect.centery += self.descend_speed
            if self.rect.centery >= GROUND_Y_POSITION:
                self.rect.centery = GROUND_Y_POSITION
                self.descend_speed = 0

        self.image = self.swing_img if self.descend_speed == 0 else self.descend_img
        self.update_position()

    def descend(self):
        if self.rect.centery < GROUND_Y_POSITION:
            if self.descend_speed < MAX_DESCEND_SPEED:
                self.descend_speed += GRAVITY

    def stop_descending(self):
        self.descend_speed = 0

# ----- ANIMAL -----
ANIMAL_SPEED = 3  # All animals move at this speed

class Animal(pygame.sprite.Sprite):
    def __init__(self, equation, is_correct):
        super().__init__()
        self.equation = equation
        self.is_correct = is_correct

        self.image = pygame.image.load("insect.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ANIMAL_SIZE, ANIMAL_SIZE))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.speed = ANIMAL_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove animal when it leaves the screen

    def draw_with_text(self, surface):
        surface.blit(self.image, self.rect)
        text = bold_font.render(str(self.equation), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

# ----- HUD -----
def draw_hud(screen, score, lives, question, high_score):
    text = font.render(f"Score: {score}   Lives: {lives}   High Score: {high_score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    # Draw question box image or semi-transparent box behind question
    question_text = question_font.render(question, True, (0, 0, 0))
    question_text_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    padding_x = 32
    padding_y = 16
    box_width = question_text_rect.width + padding_x * 2
    box_height = question_text_rect.height + padding_y * 2
    box_x = question_text_rect.centerx - box_width // 2
    box_y = question_text_rect.centery - box_height // 2
    if 'question_box_img' in globals() and question_box_img:
        scaled_box_img = pygame.transform.smoothscale(question_box_img, (box_width, box_height))
        box_rect = scaled_box_img.get_rect(center=question_text_rect.center)
        screen.blit(scaled_box_img, box_rect)
    else:
        s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        s.fill((255, 255, 230, 200))  # Light color, 200 alpha for transparency
        screen.blit(s, (box_x, box_y))
        pygame.draw.rect(screen, (180, 180, 140), (box_x, box_y, box_width, box_height), 4, border_radius=18)
    # Draw question text on top
    screen.blit(question_text, question_text_rect)


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
    animals = [Animal(ans, ans == correct) for ans in answers]
    return question_text, animals, answers, correct

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
    animals = [Animal(ans, ans == correct) for ans in answers]
    return question_text, animals, answers, correct

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
    animals = [Animal(ans, ans == correct) for ans in answers]
    return question_text, animals, answers, correct

# ----- GAME SETUP -----
player = Player()
player_group = pygame.sprite.GroupSingle(player)
animals_group = pygame.sprite.Group()

score = 0
high_score = 60
lives = 3
show_congrats = False
show_gameover = False
congrats_timer = 0

def new_question():
    question_type = random.choice(["math", "chemical", "unemployed_addition"])
    if question_type == "math":
        return generate_math_question()
    elif question_type == "chemical":
        return generate_chemical_equation()
    else:
        return generate_unemployed_addition_question()

question, animal_queue, answers, correct = new_question()
ANIMAL_SPACING = 250  # constant distance between animals (pixels)

# Store the current answers/correct for refilling the animal queue
current_answers = answers
current_correct = correct

# Spawn the first animal
if animal_queue:
    first_animal = animal_queue.pop(0)
    first_animal.rect.left = SCREEN_WIDTH
    animals_group.add(first_animal)

# ----- MAIN LOOP -----
running = True
while running:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            player.descend()
        elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            player.stop_descending()

    if not show_gameover:
        player_group.update()
        animals_group.update()

        # Maintain constant distance between animals
        if len(animals_group) > 0:
            # If animal_queue is empty, refill it with new animals for the current question
            if not animal_queue:
                animal_queue = [Animal(ans, ans == current_correct) for ans in current_answers]
            rightmost = max(a.rect.left for a in animals_group)
            if rightmost <= SCREEN_WIDTH - ANIMAL_SPACING and animal_queue:
                next_animal = animal_queue.pop(0)
                next_animal.rect.left = SCREEN_WIDTH
                animals_group.add(next_animal)

        for animal in animals_group:
            if player.rect.colliderect(animal.rect):
                if animal.is_correct:
                    score += 10
                    if score > high_score and not show_congrats:
                        show_congrats = True
                        congrats_timer = pygame.time.get_ticks()
                        high_score = score
                    # Generate new question and update current_answers/correct
                    question, animal_queue, answers, correct = new_question()
                    current_answers = answers
                    current_correct = correct
                else:
                    lives -= 1
                    if lives <= 0:
                        show_gameover = True
                        gameover_timer = pygame.time.get_ticks()
                    else:
                        question, animal_queue, answers, correct = new_question()
                        current_answers = answers
                        current_correct = correct
                animals_group.empty()
                # Spawn the first animal for the new question
                if animal_queue:
                    first_animal = animal_queue.pop(0)
                    first_animal.rect.left = SCREEN_WIDTH
                    animals_group.add(first_animal)
                break

    pygame.draw.line(screen, (139, 69, 19), (0, BRANCH_Y_POSITION), (SCREEN_WIDTH, BRANCH_Y_POSITION), 4)
    for a in animals_group:
        a.draw_with_text(screen)
    player_group.draw(screen)

    draw_hud(screen, score, lives, question, high_score)

    # Show Congrats Image
    if show_congrats:
        if pygame.time.get_ticks() - congrats_timer < 3000:
            img_rect = congrats_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(congrats_img, img_rect)
        else:
            show_congrats = False

    # Show Game Over
    if show_gameover:
        img_rect = gameover_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(gameover_img, img_rect)
        if pygame.time.get_ticks() - gameover_timer > 3000:
            running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
