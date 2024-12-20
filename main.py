import pygame
import sys
import button
import csv
import os
import argparse
from player import Player
import scenes
from completed_levels import completed_levels

class Game:
    """Definitive game class"""
    def __init__(self, scene):
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
        pygame.display.set_caption("Kohlekraft, nein danke!")

        # Game variables
        self.level = 0

        # Get current scene from argument
        self.scene = scene

        # Tiling settings
        self.TILE_SIZE = 32
        self.ROWS = self.GAME_HEIGHT // self.TILE_SIZE + 1
        self.COLS = self.GAME_WIDTH // self.TILE_SIZE

        self.TILE_TYPES = len(os.listdir("./assets/images/tiles/"))

        self.current_tile = 0


        # Load images
        self.tile_list = []

        # Load every tile from path to tile list
        for i in range(self.TILE_TYPES):
            img = pygame.image.load(f"./assets/images/tiles/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (self.TILE_SIZE, self.TILE_SIZE))
            self.tile_list.append(img)

        # Static images
        self.save_img = pygame.image.load("./assets/images/UI/save_btn.png").convert_alpha()
        self.load_img = pygame.image.load("./assets/images/UI/load_btn.png").convert_alpha()

        self.factory_background = pygame.image.load("./assets/images/backgrounds/factory.png").convert_alpha()


        # Define colours
        self.GREEN = (144, 201, 120)
        self.WHITE = (255, 255, 255)
        self.RED = (200, 25, 25)
        self.GREY = (189, 189, 189)

        # Define font
        self.font = pygame.font.Font(None, 30)

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
        self.player = Player(0, 0, 0.5, 0.5, "./assets/images/player/idle/tile000.png")

        # create sprite group
        self.all_sprites = pygame.sprite.Group()  # Create a sprite group
        self.all_sprites.add(self.player) 

        # load menu and intro
        self.menu = scenes.LevelMenu(self.screen)
        self.intro = scenes.Intro(self.screen)


    def draw_background(self):
        self.screen.fill(self.GREEN)
        width = self.factory_background.get_width()
        for x in range(0, self.GAME_WIDTH, width):
            self.screen.blit(self.factory_background, (x * 0.5, 0))


    def draw_grid(self):
        # vertical lines
        for c in range(self.COLS + 1):
            pygame.draw.line(self.screen, self.WHITE, (c * self.TILE_SIZE, 0), (c * self.TILE_SIZE, self.GAME_HEIGHT))
            
        # horizontal lines
        for c in range(self.ROWS + 1):
            pygame.draw.line(self.screen, self.WHITE, (0, c * self.TILE_SIZE), (self.GAME_WIDTH, c * self.TILE_SIZE))


    def draw_world(self):
        """render each tile from tilemap"""
        for y, row in enumerate(self.world_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    self.screen.blit(self.tile_list[tile], (x * self.TILE_SIZE, y * self.TILE_SIZE))

    
    def draw_text(self, text, font, text_col, x, y):
        """function to easily draw text"""
        img = self.font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def load_level(self):
        """open level file and add to world_data"""
        print("loading level")
        try:
            with open(f'./levels/level{self.level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter = ',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        self.world_data[x][y] = int(tile)

        except FileNotFoundError:
            print("file not found")
            self.world_data = [[-1 for _ in row] for row in self.world_data]

    def reset(self):
        """reset player to start with atrributes"""
        self.player.pos = self.player.vec(0, 0)
        self.player.vel = self.player.vec(0, 0)
        self.player.acc = self.player.vec(0, 0)
        self.player.rect.topleft = (0, 0)
        self.player.grounded = False
        self.player.is_jumping = False
        self.player.has_won = False
        self.player.dead = False
        self.player.dead_screen = False
        self.player.is_playing_jump_animation = False

    def update_completed_levels(self, input_list):
        """write completed levels to file"""
        with open("./completed_levels.py", 'w') as f:
            # Write the list to the file
            f.write(f'completed_levels = {input_list}\n')


    def run_editor(self):
        """game editor"""
        self.load_level()
        while True:
            self.draw_background()
            self.draw_grid()
            self.draw_world()

            # Margins for buttons
            pygame.draw.rect(self.screen, self.GREY, (self.GAME_WIDTH, 0, self.SIDE_MARGIN, self.GAME_WIDTH))
            pygame.draw.rect(self.screen, self.GREY, (0, self.GAME_HEIGHT, self.GAME_WIDTH, self.GAME_HEIGHT + self.LOWER_MARGIN))

            # Text
            self.draw_text(f'Level: {self.level}', self.font, self.WHITE, 10, self.GAME_HEIGHT + self.LOWER_MARGIN - 90)
            self.draw_text('Press UP or DOWN to change level', self.font, self.WHITE, 10, self.GAME_HEIGHT + self.LOWER_MARGIN - 60)

            # Save button
            if self.save_button.draw(self.screen):
                with open(f'./levels/level{self.level}_data.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter = ',')
                    for row in self.world_data:
                        writer.writerow(row)

            # Load button
            if self.load_button.draw(self.screen):
                self.load_level()

            # Tile buttons
            self.button_count = 0
            for self.button_count, i in enumerate(self.button_list):
                if i.draw(self.screen):
                    self.current_tile = self.button_count

            # Highlight the selected tile
            pygame.draw.rect(self.screen, self.RED, self.button_list[self.current_tile].rect, 3)

            # Place tile on map
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

            # Event loop
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

    def run_game(self, hitbox):
        """gameplay"""
        self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.load_level()

        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle scene-specific events
                if self.scene == "select":
                    selected_level = self.menu.handle_event(event)
                    if selected_level is not None:
                        print("SELECTED LEVEL: ", selected_level)
                        self.level = selected_level
                        self.load_level()
                        self.scene = "game"

                elif self.scene == "intro":
                    if self.intro.handle_event(event):
                        self.scene = "select"

            # Update logic based on the current scene
            if self.scene == "select":
                self.menu.render()

            elif self.scene == "intro":
                self.intro.render_slide()

            elif self.scene == "game":
                keys = pygame.key.get_pressed()

                # Update and render game world
                self.draw_background()
                self.draw_world()

                # Update and render player
                self.player.update(keys, self.world_data, self.TILE_SIZE)
                self.player.draw(self.screen)

                if hitbox:
                    self.player.draw_hitbox(self.screen)

                # Handle win or death conditions
                if self.player.has_won:
                    print("LEVEL COMPLETED")
                    self.scene = "won"
                    

                elif self.player.dead_screen:
                    self.scene = "death"

            elif self.scene == "death":
                # Render the death screen
                if scenes.Standard(self.screen).text_and_continue("You died", (255, 0, 0)):
                    self.scene = "select"  # Reset to level selection or another appropriate scene
                    self.reset()

            elif self.scene == "won":
                # Render the win screen
                if scenes.Standard(self.screen).text_and_continue("Level completed!", (0, 255, 0)):

                    if self.level not in completed_levels:
                        completed_levels.append(self.level)

                    self.update_completed_levels(completed_levels)
                    self.scene = "select"
                    self.menu.selected_index += 1
                    self.reset()

            # Update the display and maintain FPS
            pygame.display.update()
            self.clock.tick(self.FPS)

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--editor", "-e", action="store_true") # level editor
parser.add_argument("--hitbox", action="store_true") # show hitbox ingame
parser.add_argument("--skip-intro", "-i", action="store_true") # skip intro

args = parser.parse_args()

# Run game based on arguments
if args.editor:
    Game("intro").run_editor()
else:
    if args.skip_intro:
        scene = "select"
    else:
        scene = "intro"
        
    Game(scene).run_game(args.hitbox)