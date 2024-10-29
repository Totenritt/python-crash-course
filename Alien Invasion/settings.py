class Settings:
    def __init__(self):
        """Initialize the game's settings."""
        # Ship settings
        self.screen_width = 1200
        self.screen_hight = 800
        self.bg_color = (230, 230, 230) 

        # Bullet settings
        self.bullet_width = 10
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)    
        self.max_bullets = 99

        # Alien settings
        self.fleet_drop_speed = 10
    
        # Game settings
        self.ship_limit = 3
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 2.5
        self.alien_speed = 1.0

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = round(self.alien_points * self.score_scale, -1)
        print("alien_points: ", self.alien_points)