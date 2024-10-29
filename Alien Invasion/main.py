import pygame
import sys
from ship import Ship
from settings import Settings
from bullet import Bullet
from time import sleep
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to mange game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, 
                                               self.settings.screen_hight)) 
        self.clock = pygame.time.Clock() # clock to control the framerate
        self.ship = Ship(self) 
        self.bullets = pygame.sprite.Group()  
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.game_active = False
        self.scoreboard = Scoreboard(self)  

        self.button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self.check_event()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self.update_screen()
            self.clock.tick(60) # maximum framerate  

    def check_event(self):
        """Respond to key presses and mouse events."""
        # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)

            elif event.type == pygame.QUIT:
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_mouse_on_button(mouse_pos)

    def check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        elif event.key == pygame.K_q:
            sys.exit()

        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
    
    def check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color) 

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)

        self.scoreboard.show_score()

        if self.game_active == False:
            self.button.draw_button()

        pygame.display.flip() # make the most recent drawn screen visible
    
    def fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.max_bullets:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def delete_bullet(self):
        """Delete a bullet if it reaches the top of the screen."""
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
    
    def _update_bullets(self):
        """Update the position of the bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        self.delete_bullet()

        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, 
                                                True, True)
        if collisions:
            for aliens in collisions.values():
                # each aliens is a list of aliens being hit by the same bullet
                self.stats.score += self.settings.alien_points * len(aliens)
            self.scoreboard.prep_score()
            self.scoreboard.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()

            # Increase level
            self.settings.increase_speed()
            self.stats.level += 1
            self.scoreboard.prep_level()

    def _check_alien_ship_collisions(self):
        """Respond to alien-ship collisions."""
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

    def _check_aliens_bottom(self):
        """Respond to aliens reaching the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_hight:
                self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height= alien.rect.size

        current_x, current_y = alien_width, alien_height

        while current_y < (self.settings.screen_hight - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.y = y_position
        new_alien.rect.y = new_alien.y
        new_alien.rect.x = new_alien.x
        self.aliens.add(new_alien)
    
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """Update the position of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        self._check_alien_ship_collisions()
        self._check_aliens_bottom()
    
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.scoreboard.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)

        else:    
            self.game_active = False
            pygame.mouse.set_visible(True)
            self.settings.initialize_dynamic_settings()
    
    def _check_mouse_on_button(self, mouse_pos):
        """Check if the mouse is on the button."""
        if self.button.rect.collidepoint(mouse_pos) and self.game_active == False:
            # reset the game status
            self.stats.reset_stats()
            self.game_active = True

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            self.scoreboard.prep_score()
            self.scoreboard.prep_level()
            self.scoreboard.prep_ships()

            # hide the mouse cursor
            pygame.mouse.set_visible(False)

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
