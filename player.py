import pygame
import os

class Player(pygame.sprite.Sprite):
    """Class for player in game handling movement physics sprites etc"""
    def __init__(self, x, y, acceleration, gravity, sprite):
        super().__init__()
        self.vec = pygame.math.Vector2

        self.pos = self.vec(x, y)
        self.vel = self.vec(0, 0)
        self.acc = self.vec(0, 0)

        self.acceleration = acceleration
        self.gravity = gravity
        self.friction = -0.13

        # set default values
        self.grounded = False
        self.is_jumping = False
        self.has_won = False
        self.dead = False
        self.dead_screen = False
        self.is_playing_jump_animation = False

        # Tiles player dies from
        self.deadly_tiles = [4, 5, 6, 7, 8]


        # Load animations
        self.animations = {
                "idle": self.load_animation_frames("./assets/images//player/idle", scale_factor=2),
                "run": self.load_animation_frames("./assets/images/player/run", scale_factor=2),
                "jump": self.load_animation_frames("./assets/images/player/jump", scale_factor=2),
                "death": self.load_animation_frames("./assets/images/player/death", scale_factor=2)
            }

        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # Time in milliseconds per frame

        # Initial image and rect setup
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.rect = self.rect.inflate(-30, -20)

        # where to place character at start (gotten from argument)
        self.rect.topleft = (x, y)


    def load_animation_frames(self, path, scale_factor=1):
        """Loads animation frames from a directory and scales them."""
        frames = []
        for filename in sorted(os.listdir(path)):  # Ensure files are sorted
            if filename.endswith(".png"):  # Only load PNG files
                frame = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                # Scale to desired factored
                if scale_factor != 1:
                    frame = pygame.transform.scale(
                        frame, (frame.get_width() * scale_factor, frame.get_height() * scale_factor)
                    )
                frames.append(frame)
        return frames


    def limit_velocity(self, max_vel):
        """Make sure velocity doesnt spin out of control due to repeated math operations"""
        self.vel.x = max(-max_vel, min(self.vel.x, max_vel))
        if abs(self.vel.x) < .01: self.vel.x = 0

    def horizontal_movement(self, keys):
        """Detects movment keys and applies movement horisontally"""
        self.acc.x = 0
        if keys[pygame.K_LEFT]:
            self.acc.x = -self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.acc.x = self.acceleration
        else:
            self.acc.x = 0

        # Clean up after movement
        self.acc.x += self.vel.x * self.friction
        self.vel += self.acc
        self.limit_velocity(4)
        self.pos += self.vel + 0.5 * self.acc
        self.rect.topleft = self.pos

    def vertical_movement(self, keys):
        """Detects jumping and operates gravity logic"""
        self.acc.y = self.gravity

        if keys[pygame.K_SPACE] and self.grounded and not self.is_playing_jump_animation:
            self.vel.y = -12  # Jump velocity
            self.grounded = False
            self.is_playing_jump_animation = True  # Start jump animation
            self.current_animation = "jump"
            self.current_frame = 0  # Reset jump animation to the beginning
        self.rect.topleft = self.pos

    def get_tile_collisions(self, world_data, TILE_SIZE):
        """Convert world_data to rects and detect collision based on it"""
        collisions = []
        for y, row in enumerate(world_data):
            for x, tile in enumerate(row):
                if tile >= 0:  # Tile exists
                    if tile in self.deadly_tiles:
                        # Smaller hitbox for deadly tiles
                        shrink_factor = 0.2
                        offset = (1 - shrink_factor) * TILE_SIZE / 2
                        tile_rect = pygame.Rect(
                            x * TILE_SIZE + offset, 
                            y * TILE_SIZE + offset, 
                            TILE_SIZE * shrink_factor, 
                            TILE_SIZE * shrink_factor
                        )
                    else:
                        # Normal hitbox for other tiles
                        tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if self.rect.colliderect(tile_rect):
                        collisions.append((tile, tile_rect))
        return collisions


    def check_tile(self, tile):
        """checks if collision tile has specific attributes"""
        skip_correction = False

        if tile == 3:  # win button
            self.has_won = True  # Set a flag to indicate level completion
            skip_correction = True

        elif tile in self.deadly_tiles:
            self.dead = True # Set flag to indicate death globally

        return skip_correction

    def checkCollisionsx(self, world_data, TILE_SIZE):
        """corrects collisions on the x axis"""
        collisions = self.get_tile_collisions(world_data, TILE_SIZE)
        for tile, tile_rect in collisions:
            # Do tile based detections
            skip = self.check_tile(tile)
            if not skip:
                if self.vel.x > 0:  # Hit tile moving right
                    self.rect.right = tile_rect.left
                    self.pos.x = self.rect.x
                elif self.vel.x < 0:  # Hit tile moving left
                    self.rect.left = tile_rect.right
                    self.pos.x = self.rect.x

    def checkCollisionsy(self, world_data, TILE_SIZE):
        """Correct collisions on y axis"""
        self.grounded = False

        # Adjust hitbox for detection:
        # This is a fix i am not contempt with and is causing some bugs
        # I would like to fix this in a future update
        self.rect.bottom += 1

        collisions = self.get_tile_collisions(world_data, TILE_SIZE)
        for tile, tile_rect in collisions:
            # Do tile based detections
            skip = self.check_tile(tile)
            if not skip:
                if self.vel.y > 0:  # Hit tile from the top
                    self.grounded = True
                    self.is_jumping = False

                    self.rect.bottom = tile_rect.top
                    self.pos.y = self.rect.y
                    self.vel.y = 0
                elif self.vel.y < 0:  # Hit tile from the bottom
                    self.rect.top = tile_rect.bottom
                    self.pos.y = self.rect.y
                    self.vel.y = 0

        # Undo adjustment for next calculation
        self.rect.bottom -= 1

    def animate(self, current_time):
        """Handles frame updates for animations."""
        if current_time - self.animation_timer > self.animation_speed:
            self.animation_timer = current_time

            if self.current_animation == "jump" and self.is_playing_jump_animation:
                # Play jump animation once
                self.current_frame += 1
                if self.current_frame >= len(self.animations["jump"]):
                    self.current_frame = len(self.animations["jump"]) - 1  # Stay on the last frame
                    self.is_playing_jump_animation = False  # End jump animation

            elif self.current_animation == "death":
                # Play jump animation once
                self.current_frame += 1
                if self.current_frame >= len(self.animations["death"]):
                    self.current_frame = len(self.animations["death"]) - 1  # Stay on the last frame
                    self.dead_screen = True

            else:
                # Loop other animations
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])

            self.image = self.animations[self.current_animation][self.current_frame]

    def check_map_boundaries(self):
        """checks and corrects player if they go to far to left or right"""
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x
        elif self.rect.right > 960:
            self.rect.right = 960
            self.pos.x = self.rect.x

    def check_fall_death(self):
        """kills player if they fall out of map"""
        if self.rect.top > 540:  # If the player falls below the map
            self.dead = True  # Player dies from falling
            self.current_animation = "death"
            self.is_playing_jump_animation = False  # End jump animation if falling


    def update(self, keys, world_data, TILE_SIZE):
        """Definitive player update function when it comes to movement, animation and physics"""
        if not self.dead:
            self.horizontal_movement(keys)
            self.checkCollisionsx(world_data, TILE_SIZE)

            self.vertical_movement(keys)
            self.checkCollisionsy(world_data, TILE_SIZE)

            self.pos.x = self.rect.x
            self.pos.y = self.rect.y

            self.check_fall_death()
            self.check_map_boundaries()

        # Determine animation state
        if self.dead:
            self.current_animation = "death"
        elif self.is_playing_jump_animation:
            self.current_animation = "jump"
        elif self.vel.x != 0:
            self.current_animation = "run"
        else:
            self.current_animation = "idle"

        # Update animation frame
        self.animate(pygame.time.get_ticks())

    def draw(self, screen):
        """Draw player on screen"""
        #screen.blit(self.image, (self.rect.x + self.image_offset_x, self.rect.y + self.image_offset_y))
        screen.blit(self.image, (self.rect.x - 18, self.rect.y - 10))


    def draw_hitbox(self, screen):
        """Draw players hitbox for debugging"""
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
