# Importar los módulos necesarios
from random import randint
from math import hypot
from pygame import *

init()
# durante el juego creamos etiquetas en tamaño 72
title_font = font.Font(None, 72)
small_font = font.Font(None, 28)


# Variables globales (ajustes)
win_width = 800
win_height = 600
left_bound = 20            # límites que el jugador no supera (el fondo empieza a moverse)
right_bound = win_width - 8 * left_bound
shift = 0
gravedad = .25
state = "world"
# Variables heroe
salto = -9 #debe ser negativo pues es una reducción de 'y' (arriba)
x_start, y_start = 20, 10
h_width = 65
h_heigth = 90

img_file_back = 'hielo.png'
img_file_hero = 'frisk.png'
img_file_enemy = 'loox.png'

img_file_princess = 'asriel.png'
FPS = 60

# colores:
C_WHITE = (255, 255, 255)
C_DARK = (48, 48, 0)
C_YELLOW = (255, 255, 87)
C_GREEN = (32, 128, 32)
C_RED = (255, 0, 0)
C_BLACK = (0, 0, 0)


# Clases
# Clase para el objetivo (está parado y no hace nada)
class FinalSprite(sprite.Sprite):
 # constructor de clase
 def __init__(self, player_image, player_x, player_y, player_speed):
     # Llamando al constructor de la clase (Sprite):
     sprite.Sprite.__init__(self)
     # cada objeto debe almacenar la propiedad image
     self.image = transform.scale(image.load(player_image), (60, 120))
     self.speed = player_speed


     # cada objeto debe almacenar la propiedad Rect en la cual está inscrito
     self.rect = self.image.get_rect()
     self.rect.x = player_x
     self.rect.y = player_y
    
class Hero(sprite.Sprite):
   def __init__(self, filename, x, y, width, height):
       sprite.Sprite.__init__(self)
       # La imagen es subida de un archivo y encaja en un rectángulo del tamaño correcto:
       self.image = transform.scale(image.load(filename), (width, height)).convert_alpha()
                   # Utilizamos convert_alpha, lo necesitamos para la transparencia
       # creamos las propiedades y registramos los valores transferidos:
       self.x=x
       self.y=y
       self.width=width
       self.heigth=height
       self.x_speed = 0
       self.y_speed = 0
       # cada objeto debe almacenar una propiedad rect. Esta propiedad es necesaria para detectar el contacto del objeto.
       self.rect = self.image.get_rect()
       # Colocamos al personaje en un punto específico (x, y):
       self.rect.x = x
       self.rect.y = y

       # añadimos la propiedad stands_on – es la plataforma en la cual está parado el personaje
       self.stands_on = False # Si no está en una, entonces el valor es falso


   def gravitate(self,gravedad):
       self.y_speed += gravedad

 
   def jump(self, y):
       if self.stands_on:
           self.y_speed = y


   def update(self):
       ''' Mueve al personaje usando la velocidad actual horizontal y vertical'''
       # primer movimiento horizontal
       self.rect.x += self.x_speed
       # si vamos detrás de la pared, estaremos contra la pared
       platforms_touched = sprite.spritecollide(self, barriers, False)
       if self.x_speed > 0: # si vamos a la derecha, el borde derecho del personaje está en contra del borde izquierdo de la pared
           for p in platforms_touched:
               self.rect.right = min(self.rect.right, p.rect.left) # Si tocamos varios al mismo tiempo, el borde derecho es el mínimo
       elif self.x_speed < 0: # yendo a la izquierda, colocamos el borde izquierdo del personaje contra el borde derecho de la pared
           for p in platforms_touched:
               self.rect.left = max(self.rect.left, p.rect.right) # si varias paredes son tocadas, el borde izquierdo es el máximo

    
       self.stands_on = False
       # ahora el movimiento vertical       
       self.gravitate(gravedad)
       self.rect.y += self.y_speed
       # si vamos más allá de la pared, estaremos parados contra la pared
       platforms_touched = sprite.spritecollide(self, barriers, False)
       if self.y_speed > 0: # bajando
           for p in platforms_touched:
               self.y_speed = 0
               # Comprobamos cuál de las plataformas está más alto desde la parte inferior, la alineamos y la registramos como nuestro soporte:
               if p.rect.top < self.rect.bottom:
                   self.rect.bottom = p.rect.top
                   self.stands_on = p
       elif self.y_speed < 0: # subiendo
           self.stands_on = False # subimos, ¡lo que significa que ya no estamos parados en nada!
           for p in platforms_touched:
               self.y_speed = 0  # al colisionar con una pared, la velocidad vertical se disipa
               self.rect.top = max(self.rect.top, p.rect.bottom) # alineamos el borde superior con los bordes inferiores de las paredes con las cuales colisionamos




class Wall(sprite.Sprite):
   def __init__(self, x, y, width, height):
       sprite.Sprite.__init__(self)
       # imagen – un nuevo rectángulo del tamaño correcto:
       # Plataforma azul hielo con borde luminoso y sombra inferior.
       self.image = Surface((width, height), SRCALPHA)
       platform_rect = self.image.get_rect()
       draw.rect(self.image, (92, 151, 190), platform_rect, border_radius=6)
       draw.rect(self.image, (190, 232, 250), platform_rect, 2, border_radius=6)
       # La luz superior y la sombra dan volumen a las barras.
       if width > 8 and height > 8:
           draw.line(self.image, (230, 249, 255),
                     (4, 3), (width - 5, 3), 2)
           draw.line(self.image, (57, 104, 145),
                     (4, height - 4), (width - 5, height - 4), 2)
       
       

       # creamos una propiedad rect
       self.rect = self.image.get_rect()
       self.rect.x = x
       self.rect.y = y


class Enemy(sprite.Sprite): # enemigo
   def __init__(self, x=20, y=0, filename=img_file_enemy, width=100, height=100):
       sprite.Sprite.__init__(self)


       self.image = transform.scale(image.load(filename), (width, height)).convert_alpha()
       self.rect = self.image.get_rect()
       self.rect.x = x
       self.rect.y = y
       self.side = "left"

   def update(self):
        ''' mueve el personaje usando las flechas'''

        #self.rect.x += randint(-5, 5)
        #self.rect.y += randint(-5, 5)
        if self.rect.x <= 0:
            self.side = "right"  # Cambia dirección a derecha
        if self.rect.x >= 400:
            self.side = "left"  # Cambia dirección a izquierda
        if self.side == "left":
            self.rect.x -= 3  # Se mueve a la izquierda
        else:
            self.rect.x += 3 # Se mueve a la derecha


# Empieza el juego
display.set_caption("undertale")
window = display.set_mode([win_width, win_height])


back = transform.scale(image.load(img_file_back).convert(), (win_width, win_height))


# lista de todos los personajes en el juego:
all_sprites = sprite.Group()
# lista de obstáculos:
barriers = sprite.Group()
# lista de enemigos:
enemies = sprite.Group()
# lista de minas:
bombs = sprite.Group()


# creamos un personaje y lo añadimos a la lista de objetos:
robin = Hero(img_file_hero,x_start,y_start,h_width,h_heigth)
all_sprites.add(robin)
# creamos paredes y las añadimos:
w = Wall(50, 150, 480, 20)
barriers.add(w)
all_sprites.add(w)
w = Wall(700, 50, 50, 360)
barriers.add(w)
all_sprites.add(w)
w = Wall(350, 380, 640, 20)
barriers.add(w)
all_sprites.add(w)
w = Wall(-200, 590, 1600, 20)
barriers.add(w)
all_sprites.add(w)
w = Wall(1000, -100, 20, 350)
barriers.add(w)
all_sprites.add(w)

# Barrera invisible en el extremo izquierdo del mapa.
# Está en barriers para detener al héroe, pero no en all_sprites para no dibujarla.
left_wall = Wall(-200, -2000, 20, 3000)
barriers.add(left_wall)

# creamos enemigos y los añadimos:
en = Enemy(50, 480)
all_sprites.add(en)
enemies.add(en)


en = Enemy(400, 480)
all_sprites.add(en)
enemies.add(en)


# creamos minas y las añadimos:
 # no añadimos bombas a la lista de objetos, las dibujaremos con un comando separado
               # Podemos detonar bombas fácilmente y también hacer que estén inmóviles, update() no es llamado


# Creamos el objeto final y lo añadimos:
pr = FinalSprite(img_file_princess, win_width + 500, win_height - 150, 0)
all_sprites.add(pr)


# La princesa (asriel.png) ahora es el jefe final.
# En el mundo: flechas izquierda/derecha y arriba para saltar.
# En combate: cuatro flechas para esquivar; Z para atacar en tu turno.
clock = time.Clock()
arena = Rect(200, 250, 400, 250)
run = True
enemy_fighting = None
is_boss = False
player_hp = 20
boss_hp = 60
battle_timer = 0
turn = "dodge"
turn_timer = 0
invulnerable = 0
projectiles = []
soul = Rect(390, 365, 16, 16)
boss_image = transform.scale(pr.image, (80, 140))


def start_battle(target, final=False):
    # Reiniciamos cada combate; el jefe tiene tres rondas de defensa.
    global state, enemy_fighting, is_boss, player_hp, boss_hp
    global battle_timer, turn, turn_timer, invulnerable
    state = "battle"
    enemy_fighting = target
    is_boss = final
    player_hp = 20
    boss_hp = 60
    battle_timer = 0
    turn = "dodge"
    turn_timer = 0
    invulnerable = 0
    projectiles.clear()
    soul.center = arena.center
    robin.x_speed = 0


def add_attack(x, y, vx, vy):
    # Coordenadas decimales para que los disparos diagonales sean fluidos.
    projectiles.append([float(x), float(y), vx, vy])


def centered_text(message, y, color=C_WHITE, large=False):
    lettering = (title_font if large else small_font).render(message, True, color)
    window.blit(lettering, lettering.get_rect(center=(win_width // 2, y)))


while run:
    for e in event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            run = False
        elif e.type == KEYDOWN:
            if state == "world" and e.key == K_UP:
                robin.jump(salto)
            elif state == "battle" and turn == "attack" and e.key == K_z:
                # Un ataque por turno. Tres golpes vencen a Asriel.
                boss_hp = max(0, boss_hp - 20)
                if boss_hp == 0:
                    enemy_fighting.kill()
                    state = "victory"
                else:
                    turn = "dodge"
                    turn_timer = 0
                    projectiles.clear()
                    soul.center = arena.center

    keys = key.get_pressed()
    if state == "world":
        robin.x_speed = 5 * (int(keys[K_RIGHT]) - int(keys[K_LEFT]))
        all_sprites.update()
        # La cámara desplaza también al jefe final porque está en all_sprites.
        if ((robin.rect.x > right_bound and robin.x_speed > 0)
                or (robin.rect.x < left_bound and robin.x_speed < 0)):
            shift -= robin.x_speed
            for obj in all_sprites:
                obj.rect.x -= robin.x_speed
            # La barrera invisible debe desplazarse junto con el mapa.
            left_wall.rect.x -= robin.x_speed
        local_shift = shift % win_width
        window.blit(back, (local_shift, 0))
        if local_shift:
            window.blit(back, (local_shift - win_width, 0))
        all_sprites.draw(window)
        # Tocar al jefe inicia el combate, en lugar de ganar inmediatamente.
        if robin.rect.top > win_height:
            state = "gameover"
        elif sprite.collide_rect(robin, pr):
            start_battle(pr, True)
        else:
            hits = sprite.spritecollide(robin, enemies, False)
            if hits:
                start_battle(hits[0])

    elif state == "battle":
        window.fill(C_BLACK)
        battle_timer += 1
        turn_timer += 1
        invulnerable = max(0, invulnerable - 1)
        phase = 1 if boss_hp > 40 else 2 if boss_hp > 20 else 3
        if is_boss:
            window.blit(boss_image, (360, 55))
            centered_text("ASRIEL DREMURR", 25)
            draw.rect(window, C_DARK, (300, 205, 200, 12))
            draw.rect(window, C_GREEN, (300, 205, int(200 * boss_hp / 60), 12))
        else:
            window.blit(enemy_fighting.image,
                        enemy_fighting.image.get_rect(center=(400, 125)))
            centered_text("LOOX", 25)

        if turn == "dodge":
            soul.x += 4 * (int(keys[K_RIGHT]) - int(keys[K_LEFT]))
            soul.y += 4 * (int(keys[K_DOWN]) - int(keys[K_UP]))
            soul.clamp_ip(arena.inflate(-12, -12))
            if not is_boss:
                if turn_timer % 45 == 0:
                    add_attack(arena.right - 15, randint(265, 475), -4, 0)
            elif phase == 1:
                # Primera fase: lluvia de estrellas desde arriba.
                if turn_timer % 20 == 0:
                    add_attack(randint(215, 575), arena.top + 10, 0, 3)
            elif phase == 2:
                # Segunda fase: disparos desde ambos lados.
                if turn_timer % 25 == 0:
                    y = randint(265, 475)
                    add_attack(arena.left + 10, y, 3.5, 0)
                    add_attack(arena.right - 20, randint(265, 475), -3.5, 0)
            else:
                # Tercera fase: proyectiles dirigidos a tu posición al disparar.
                if turn_timer % 30 == 0:
                    x = randint(215, 575)
                    y = arena.top + 10
                    dx, dy = soul.centerx - x, soul.centery - y
                    distance = max(1, hypot(dx, dy))
                    add_attack(x, y, dx / distance * 3.8, dy / distance * 3.8)
                    add_attack(randint(215, 575), arena.top + 10, 0, 2.8)

            for shot in projectiles[:]:
                shot[0] += shot[2]
                shot[1] += shot[3]
                hitbox = Rect(int(shot[0]), int(shot[1]), 12, 12)
                if not arena.colliderect(hitbox):
                    projectiles.remove(shot)
                    continue
                draw.rect(window, C_WHITE, hitbox)
                if soul.colliderect(hitbox) and invulnerable == 0:
                    player_hp = max(0, player_hp - 4)
                    invulnerable = 60  # Un segundo para recuperarte de un golpe.
                    projectiles.remove(shot)
            # Comprobamos primero la derrota para evitar ganar al morir.
            if player_hp == 0:
                state = "gameover"
            elif turn_timer >= (420 if is_boss else 300):
                if is_boss:
                    turn = "attack"
                    turn_timer = 0
                    projectiles.clear()
                else:
                    enemy_fighting.kill()
                    enemy_fighting = None
                    state = "world"
            centered_text("Esquiva con las flechas" +
                          (" - Fase " + str(phase) if is_boss else ""), 535)
        else:
            centered_text("Pulsa Z para CONTRAATACAR", 535, C_RED)

        draw.rect(window, C_WHITE, arena, 4)
        # Corazón rojo dibujado con formas: no necesita otra imagen.
        if invulnerable == 0 or invulnerable % 10 < 5:
            x, y = soul.topleft
            draw.circle(window, C_RED, (x + 4, y + 5), 5)
            draw.circle(window, C_RED, (x + 11, y + 5), 5)
            draw.polygon(window, C_RED,
                         [(x, y + 6), (x + 15, y + 6), (x + 8, y + 15)])
        centered_text("VIDA: " + str(player_hp) + "/20", 575, C_YELLOW)

    elif state == "victory":
        window.fill(C_BLACK)
        centered_text("¡GANASTE!", 250, C_YELLOW, True)
        centered_text("Derrotaste a Asriel, el jefe final.", 325)
        centered_text("Pulsa ESC para salir", 380)
    elif state == "gameover":
        window.fill(C_BLACK)
        centered_text("GAME OVER", 250, C_RED, True)
        centered_text("Pulsa ESC para salir", 340)

    display.update()
    clock.tick(FPS)

quit()
