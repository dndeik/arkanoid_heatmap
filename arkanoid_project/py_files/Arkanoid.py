import pygame as pg
import socket
from random import randrange as rnd

WIDTH, HEIGHT = 1200, 800
fps = 60
# paddle settings
paddle_w = 330
paddle_h = 35
paddle_speed = 15
paddle = pg.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10, paddle_w, paddle_h)
# ball settings
ball_radius = 20
ball_speed = 6
ball_rect = int(ball_radius * 2 ** 0.5)
ball = pg.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect, ball_rect)
dx, dy = 1, -1
# blocks settings
block_list = [pg.Rect(10 + 120 * i, 2 + 72 * j, 110, 70) for i in range(10) for j in range(4)]
color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10) for j in range(4)]

pg.init()
sc = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
# background color
bg = pg.Surface((WIDTH, HEIGHT))
bg.fill((21, 21, 21))

def detect_collision(dx, dy, ball, rect):
    if dx > 0:
        delta_x = ball.right - rect.left
    else:
        delta_x = rect.right - ball.left
    if dy > 0:
        delta_y = ball.bottom - rect.top
    else:
        delta_y = rect.bottom - ball.top

    if abs(delta_x - delta_y) < 10:
        dx, dy = -dx, -dy
    elif delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx
    return dx, dy


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
    sc.blit(bg, (0, 0))
    # drawing world
    [pg.draw.rect(sc, color_list[color], block) for color, block in enumerate(block_list)]
#    [pg.draw.rect(sc, pg.Color(0,0,0), block) for color, block in enumerate(block_list)]
    pg.draw.rect(sc, pg.Color(49,160,49), paddle)
    pg.draw.circle(sc, pg.Color('white'), ball.center, ball_radius)
    # ball movement
    ball.x += ball_speed * dx
    ball.y += ball_speed * dy
    # collision left right
    if ball.centerx < ball_radius or ball.centerx > WIDTH - ball_radius:
        dx = -dx
    # collision top
    if ball.centery < ball_radius:
        dy = -dy
    # collision paddle
    if ball.colliderect(paddle) and dy > 0:
        dx, dy = detect_collision(dx, dy, ball, paddle)
        # if dx > 0:
        #     dx, dy = (-dx, -dy) if ball.centerx < paddle.centerx else (dx, -dy)
        # else:
        #     dx, dy = (-dx, -dy) if ball.centerx >= paddle.centerx else (dx, -dy)
    # collision blocks
    hit_index = ball.collidelist(block_list)
    if hit_index != -1:
        hit_rect = block_list.pop(hit_index)
        hit_color = color_list.pop(hit_index)
        dx, dy = detect_collision(dx, dy, ball, hit_rect)
        # special effect
        hit_rect.inflate_ip(ball.width * 3, ball.height * 3)
        pg.draw.rect(sc, hit_color, hit_rect)
        fps += 2
    # win, game over
    if ball.bottom > HEIGHT:
        print('GAME OVER!')
        exit()
    elif not len(block_list):
        print('WIN!!!')
        exit()
    # control
    key = pg.key.get_pressed()
    if key[pg.K_LEFT] and paddle.left > 0:
        paddle.left -= paddle_speed
    if key[pg.K_RIGHT] and paddle.right < WIDTH:
        paddle.right += paddle_speed
    # update screen
    print ("Paddle coordinates = " + str(paddle.centerx) + ',' + str(paddle.centery))

    #POSTING COORDINATES TO UDP PORT FOR TELEGRAF
    UDP_IP = "127.0.0.1"
    UDP_PORT = 8094
    paddle_x = paddle.centerx//10*10
    paddle_y = paddle.centery//10*10

    ball_x = ball.centerx//10*10
    ball_y = ball.centery//10*10

    MESSAGE_PADDLE = b"coord,obj=paddle x_coord=%d,y_coord=%d " % (paddle_x, paddle_y)
    MESSAGE_BALL = b"coord,obj=ball x_coord=%d,y_coord=%d " % (ball_x, ball_y)

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE_PADDLE)
    print("message: %s" % MESSAGE_BALL)


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE_PADDLE, (UDP_IP, UDP_PORT))
    sock.sendto(MESSAGE_BALL, (UDP_IP, UDP_PORT))

    #RENEW DISPLAY
    pg.display.flip()
    clock.tick(fps)