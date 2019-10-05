import sys, logging, arcade, random

#check to make sure we are running the right version of Python
version = (3,7)
assert sys.version_info >= version, "This script requires at least Python {0}.{1}".format(version[0],version[1])

#turn on logging, in case we have to leave ourselves debugging messages
logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
STARTING_LOCATION = (400,100)
PLAYER_VELOCITY = 5
SCREEN_TITLE = ""
LASER_DAMAGE = 50
ENEMY_HP = 100
PLAYER_HP = 200

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("assets/player.png", 0.5)
        self.hp = PLAYER_HP
        self.r = 0
        self.l = 0
        self.up = 0
        self.down = 0
        (self.center_x, self.center_y) = STARTING_LOCATION

    def update(self):
        self.center_x += (self.r + self.l)
        self.center_y += (self.up + self.down)

class Explosion(arcade.Sprite):
    def __init__(self, position):
        super().__init__("assets/laserRedShot.png", 0.5)
        (self.center_x, self.center_y) = position


class Laser(arcade.Sprite):
    def __init__(self, position, velocity, damage, enemy):
        
        self.enemy = enemy
        if(enemy):
            super().__init__("assets/laserRed.png", 0.5)
        else:
            super().__init__("assets/laserGreen.png", 0.5)
            

        (self.center_x, self.center_y) = position
        (self.dx, self.dy) = velocity
        self.damage = damage

    def update(self):
        self.center_x += self.dx
        self.center_y += self.dy

class Enemy(arcade.Sprite):
    def __init__(self, position, type):
        self.dx = 0
        self.dy = -1
        self.laserTimer = 0
        self.type = type
        self.hp = ENEMY_HP
        if(self.type == "UFO"):
            self.dx = 1
            self.dy = 0
            self.hp = 400
            super().__init__("assets/enemyUFO.png", 0.5)
        else:
            super().__init__("assets/enemyShip.png", 0.5)
        
        (self.center_x, self.center_y) = position

    def update(self):
        if(self.center_x < 100):
            self.dx = 2
        if(self.center_x > 700):
            self.dx = -2
        self.center_x += self.dx
        self.center_y += self.dy
        laser = None
        if(self.laserTimer > 50):
            x = self.position[0]
            y = self.position[1] - 15
            laser = [Laser((x,y),(0,-5),LASER_DAMAGE, True), None, None]
            self.laserTimer = 0
            if(self.type == "UFO"):
                x = self.position[0] - 20
                y = self.position[1] - 10
                laser[1] = Laser((x,y),(0,-5),LASER_DAMAGE, True)
                x = self.position[0] + 20
                y = self.position[1] - 10
                laser[2] = Laser((x,y),(0,-5),LASER_DAMAGE, True)
        self.laserTimer += 1
        return laser



class Window(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(False)
        self.background = arcade.load_texture("assets/bgfinal.jpg")
        arcade.set_background_color(arcade.color.BLUE)
        self.laser_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.player = Player()
        self.score = 0
        self.enemyModifier = 100
        self.ufoModifier = 1000
        self.time = 0
        self.playing = True



    def setup(self):
        pass

    def update(self, delta_time):
        if(self.playing):
            enemySpot = random.randrange(160, 640)
            if self.time > self.enemyModifier:
                x = enemySpot
                y = 500
                enemy = Enemy((x,y), "Ship")
                self.enemy_list.append(enemy) 
                self.enemyModifier += 100
            if self.time > self.ufoModifier:
                x = 400
                y = 500
                enemy = Enemy((x,y), "UFO")
                self.enemy_list.append(enemy) 
                self.ufoModifier += 1000
            self.laser_list.update()
            for enemy in self.enemy_list:
                laser = enemy.update()
                if(laser != None):
                    for shot in laser:
                        if(shot != None):
                            self.laser_list.append(shot)
            self.player.update()
            for e in self.enemy_list:
                if(e.center_y < -20):
                    self.playing = False
                hits = arcade.check_for_collision_with_list(e, self.laser_list)
                for shot in hits:
                    if(not shot.enemy):
                        e.hp -= shot.damage
                        if(e.hp <= 0):
                            if(e.type == "UFO"):
                                self.score += 5000
                            else:
                                self.score += 250
                            e.kill()
                        shot.kill()
            playerHits = arcade.check_for_collision_with_list(self.player, self.laser_list)
            for shot in playerHits:
                if(shot.enemy):
                    self.player.hp -= shot.damage
                    if(self.player.hp <= 0):
                        self.playing = False
                    shot.kill()
            playerCrash = arcade.check_for_collision_with_list(self.player, self.enemy_list)
            for enemy in playerCrash:
                x = (enemy.center_x + self.player.center_x)/2
                y = (enemy.center_y + self.player.center_y)/2
                explosion = Explosion((x,y))
                self.explosion_list.append(explosion)
                self.playing = False
            self.time += 1

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        self.background.draw(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT)
        arcade.draw_text("SCORE:" + str(self.score), 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 16)
        arcade.draw_text("HEALTH:" + str(self.player.hp), 680, SCREEN_HEIGHT - 40, arcade.color.WHITE, 16)
        self.player.draw()
        self.laser_list.draw()
        self.enemy_list.draw()
        self.explosion_list.draw()
        if(not self.playing):
            arcade.draw_text("GAME OVER", 250, 300, arcade.color.RED, 40)



    def on_mouse_motion(self, x, y, dx, dy):
        """ Called to update our objects. Happens approximately 60 times per second."""
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.LEFT:
            self.player.l = -PLAYER_VELOCITY 
        elif key == arcade.key.RIGHT:
            self.player.r = PLAYER_VELOCITY
        elif key == arcade.key.UP:
            self.player.up = PLAYER_VELOCITY
        elif key == arcade.key.DOWN:
            self.player.down = -PLAYER_VELOCITY

        if key == arcade.key.SPACE:
            x = self.player.center_x
            y = self.player.center_y + 15
            laser = Laser((x,y),(0,10),LASER_DAMAGE, False)
            self.laser_list.append(laser)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.l = 0 
        elif key == arcade.key.RIGHT:
            self.player.r = 0
        elif key == arcade.key.UP:
            self.player.up = 0
        elif key == arcade.key.DOWN:
            self.player.down = 0


def main():
    window = Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()