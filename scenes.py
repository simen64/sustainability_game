import pygame
import os
from completed_levels import completed_levels

class Standard:
    """standard scenes"""
    def __init__(self, screen):
        self.font = pygame.font.Font(None, 74)
        self.background_color = (0, 0, 0)
        self.waiting = False
        self.screen = screen

    def text_and_continue(self, text, color):
        """shows a short info screen in desired color with an option to move onwards by pressing any key"""
        self.screen.fill(self.background_color)

        # Render text
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)
    
        # Render "Press any key to continue" text
        subtext_surface = self.font.render("Press any key to continue", True, color)
        subtext_rect = subtext_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(subtext_surface, subtext_rect)
    
        # Update the display
        pygame.display.flip()
    
        # Wait for any key press
        self.waiting = True
        while self.waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                    return True


class LevelMenu:
    """menu for selecting levels"""
    def __init__(self, screen):
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.background_color = (0, 0, 0)

        self.completed_color = (0, 255, 0)
        self.not_done_color = (0, 0, 0)
        self.not_allowed_color = (255, 0, 0)

        self.screen = screen
        self.levels = self.load_levels()
        self.selected_index = 0


    def load_levels(self):
        """load levels from path into list"""
        level_files = len(os.listdir("./levels/"))
        levels = []
        for i in range(level_files):
            levels.append(str(i))
        levels = sorted(levels)
        return levels

    def handle_event(self, event):
        """handle changing of levels with arrowkeys"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index + 1) % len(self.levels)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index - 1) % len(self.levels)
            elif event.key == pygame.K_RETURN:
                # If previous level hasnt been completed dont allow selecting it
                if self.selected_index -1 in completed_levels or self.selected_index == 0:
                    self.active = False
                    return self.selected_index
        return None

    def render(self):
        """render the menu to the screen"""
        self.screen.fill(self.background_color)

        # Correct color and text based on completion of level
        if self.selected_index in completed_levels:
            selected_text = self.completed_color
            completed_text = "Completed"
        elif self.selected_index -1 not in completed_levels and self.selected_index != 0:
            selected_text = self.not_allowed_color
            completed_text = "Not unlocked"
        else:
            selected_text = (255, 255, 255)
            completed_text = "Not completed"

        # Render completed text
        text_surface = self.font.render(completed_text, True, selected_text)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 120))
        self.screen.blit(text_surface, text_rect)
        
        # Render level number
        text_surface = self.font.render(str(self.selected_index), True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)
    
        # Render "Press any key to continue" text
        subtext_surface = self.small_font.render("Change with arrow keys\nSelect with return", True, self.text_color)
        subtext_rect = subtext_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 200))
        self.screen.blit(subtext_surface, subtext_rect)

        pygame.display.flip()

class Intro:
    """intro text for the game"""
    def __init__(self, screen):
            self.font = pygame.font.Font(None, 32)
            self.background_color = (0, 0, 0)
            self.text_color = (255, 255, 255)
            self.waiting = False
            self.screen = screen

            self.slides = [
                """
                Greetings agent, you have come a long way, and we are pleased to have you.

                As you know there are still 256 coal powerplants in Europe, releasing around
                755 million tons of Co2.

                We need to transition from coal to nuclear power to change these statistics.
                Nuclear energy is far cleaner, producing zero emissions during operation,
                and far more efficient,
                requiring less fuel for greater energy output. It's a sustainable path
                to a greener future.
                And against popular belief, its totally safe.
                """,
                """
                Thats why you have been sent into these coal powerplants
                to turn them off for good.

                You will face deadly challenges, but keep through it
                for our future.

                Your goal is to reach the red button,
                which stops the machine.
                """,
                """
                Good luck agent

                Kohlekraft, nein danke!
                """
            ]
            self.current_slide = 0

    def render_slide(self):
        """Renders the current slide."""
        self.screen.fill(self.background_color)
        slide_text = self.slides[self.current_slide]

        text_surface = self.font.render(slide_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2 - 43, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)

        # Render press any key to continue text
        subtext_surface = self.font.render("Press any key to continue", True, self.text_color)
        subtext_rect = subtext_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 200))
        self.screen.blit(subtext_surface, subtext_rect)

        pygame.display.flip()

    def handle_event(self, event):
        """handles events for switchins slides"""
        if event.type == pygame.KEYDOWN:
            self.current_slide += 1
            if self.current_slide >= len(self.slides):
                return True  # Intro is complete
        return False