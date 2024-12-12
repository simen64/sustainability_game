import pygame
import sys
import button
import csv

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, acceleration, gravity, sprite):
        super().__init__()
        self.vec = pygame.math.Vector2

        self.pos = self.vec(x, y)
        self.vel = self.vec(0, 0)
        self.acc = self.vec(0, 0)

        self.acceleration = acceleration
        self.gravity = gravity
        self.friction = -0.12

        self.grounded = False
        self.is_jumping = False

        self.image = pygame.image.load(sprite).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def handle_input(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.acc.x = -self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.acc.x = self.acceleration
        else:
            self.acc.x = 0  # No horizontal input

        # Jumping
        if keys[pygame.K_SPACE] and self.grounded:
            self.vel.y = -10  # Jump velocity
            self.grounded = False


    def apply_physics(self):
        # Apply gravity
        self.acc.y = self.gravity

        # Apply friction
        self.acc.x += self.vel.x * self.friction

        # Update velocity and position
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc  # Update position using Verlet integration

        # Update rect position for collision detection
        self.rect.topleft = self.pos

        # Ground collision simulation (basic example)
        if self.rect.bottom >= 540:  # Assume ground level is at y=540
            self.rect.bottom = 540
            self.pos.y = self.rect.y
            self.vel.y = 0
            self.grounded = True



    def update(self, keys, world_data, TILE_SIZE):
        self.handle_input(keys)
        self.apply_physics()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game:
    def __init__(self):
        pygame.init()

        # Clock settings
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Screen settings
        self.GAME_WIDTH = 960
        self.GAME_HEIGHT = 540
        self.LOWER_MARGIN = 100
        self.SIDE_MARGIN = 300

        self.screen = pygame.display.set_mode((self.GAME_WIDTH + self.SIDE_MARGIN, self.GAME_HEIGHT + self.LOWER_MARGIN))
        pygame.display.set_caption('Level Editor')

        # Game variables
        self.level = 0

        # Tiling settings
        self.TILE_SIZE = 32
        self.ROWS = self.GAME_HEIGHT // self.TILE_SIZE + 1
        self.COLS = self.GAME_WIDTH // self.TILE_SIZE
        print(self.ROWS, self.COLS)

        self.TILE_TYPES = 1

        self.current_tile = 0


        # Load images
        self.tile_list = []

        for i in range(self.TILE_TYPES):
            img = pygame.image.load(f"./assets/images/tiles/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (self.TILE_SIZE, self.TILE_SIZE))
            self.tile_list.append(img)

        self.save_img = pygame.image.load("./assets/images/UI/save_btn.png").convert_alpha()
        self.load_img = pygame.image.load("./assets/images/UI/load_btn.png").convert_alpha()

        self.cave_background = pygame.image.load("./assets/images/backgrounds/factory.png").convert_alpha()


        # Define colours
        self.GREEN = (144, 201, 120)
        self.WHITE = (255, 255, 255)
        self.RED = (200, 25, 25)
        self.GREY = (189, 189, 189)

        # Define font
        self.font = pygame.font.SysFont('Futura', 30)


        # World building
        self.world_data = []
        for row in range(self.ROWS):
            r = [-1] * self.COLS
            self.world_data.append(r)


        # create buttons
        self.save_button = button.Button(self.GAME_WIDTH // 2, self.GAME_HEIGHT + self.LOWER_MARGIN - 50, self.save_img, 1)
        self.load_button = button.Button(self.GAME_WIDTH // 2 + 200, self.GAME_HEIGHT + self.LOWER_MARGIN - 50, self.load_img, 1)

        # make a tile button list
        self.button_list = []
        self.button_col = 0
        self.button_row = 0
        for i in range(len(self.tile_list)):
            self.tile_button = button.Button(self.GAME_WIDTH + (75 * self.button_col) + 50, 75 * self.button_row + 50, self.tile_list[i], 1)
            self.button_list.append(self.tile_button)
            self.button_col += 1
            if self.button_col == 3:
                self.button_row += 1
                self.button_col = 0


        # Create player
        self.player = Player(100, 100, 0.5, 0.5, "./assets/images/player/idle/tile000.png")

        # create sprite group
        self.all_sprites = pygame.sprite.Group()  # Create a sprite group
        self.all_sprites.add(self.player) 


    def draw_background(self):
        self.screen.fill(self.GREEN)
        width = self.cave_background.get_width()
        for x in range(0, self.GAME_WIDTH, width):
            self.screen.blit(self.cave_background, (x * 0.5, 0))


    def draw_grid(self):
        # vertical lines
        for c in range(self.COLS + 1):
            pygame.draw.line(self.screen, self.WHITE, (c * self.TILE_SIZE, 0), (c * self.TILE_SIZE, self.GAME_HEIGHT))
            
        # horizontal lines
        for c in range(self.ROWS + 1):
            pygame.draw.line(self.screen, self.WHITE, (0, c * self.TILE_SIZE), (self.GAME_WIDTH, c * self.TILE_SIZE))


    def draw_world(self):
        for y, row in enumerate(self.world_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    self.screen.blit(self.tile_list[tile], (x * self.TILE_SIZE, y * self.TILE_SIZE))

    
    def draw_text(self, text, font, text_col, x, y):
        img = self.font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def load_level(self):
        print("loading")
        try:
            with open(f'./levels/level{self.level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter = ',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        self.world_data[x][y] = int(tile)

        except FileNotFoundError:
            print("file not found")
            self.world_data = [[-1 for _ in row] for row in self.world_data]


    def run_editor(self):
        while True:
            self.draw_background()
            self.draw_grid()
            self.draw_world()

            pygame.draw.rect(self.screen, self.GREY, (self.GAME_WIDTH, 0, self.SIDE_MARGIN, self.GAME_WIDTH))
            pygame.draw.rect(self.screen, self.GREY, (0, self.GAME_HEIGHT, self.GAME_WIDTH, self.GAME_HEIGHT + self.LOWER_MARGIN))

            self.draw_text(f'Level: {self.level}', self.font, self.WHITE, 10, self.GAME_HEIGHT + self.LOWER_MARGIN - 90)
            self.draw_text('Press UP or DOWN to change level', self.font, self.WHITE, 10, self.GAME_HEIGHT + self.LOWER_MARGIN - 60)

            if self.save_button.draw(self.screen):
                with open(f'./levels/level{self.level}_data.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter = ',')
                    for row in self.world_data:
                        writer.writerow(row)

            if self.load_button.draw(self.screen):
                self.load_level()

            self.button_count = 0
            for self.button_count, i in enumerate(self.button_list):
                if i.draw(self.screen):
                    self.current_tile = self.button_count

            #highlight the selected tile
            pygame.draw.rect(self.screen, self.RED, self.button_list[self.current_tile].rect, 3)

            pos = pygame.mouse.get_pos()
            x = (pos[0]) // self.TILE_SIZE
            y = pos[1] // self.TILE_SIZE
 
            if pos[0] < self.GAME_WIDTH and pos[1] < self.GAME_HEIGHT:
                #update tile value
                if pygame.mouse.get_pressed()[0] == 1:
                    if self.world_data[y][x] != self.current_tile:
                        self.world_data[y][x] = self.current_tile
                if pygame.mouse.get_pressed()[2] == 1:
                    self.world_data[y][x] = -1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.level += 1
                        self.load_level()
                    if event.key == pygame.K_DOWN and self.level > 0:
                        self.level -= 1
                        self.load_level()

            pygame.display.update()
            self.clock.tick(self.FPS)

    def run_game(self):
        self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.load_level()
        while True:
            self.draw_background()
            self.draw_world()

            # get keys pressed

            keys = pygame.key.get_pressed()

            # update and draw player
            self.player.update(keys, self.world_data, self.TILE_SIZE)
            self.player.draw(self.screen)

            self.all_sprites.draw(self.screen)

            # quit loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(self.FPS)


Game().run_game()