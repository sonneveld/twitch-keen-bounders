import sys, pygame
import random
import websocket
import _thread
import time
import json
import traceback


STREAMERBOT_WS_URL = "ws://127.0.0.1:8080/"

STILL_STARE = 0
STILL_STARE_DOWN = 1

SCREEN_WIDTH=1280
SCREEN_HEIGHT=720

BOUNDERS_MAX_ALIVE = 50

SOUND_MAX_CHANELS = 8
SOUND_VOLUME = 1.0/2/2/2

SOUND_ENABLED = True


bounder_still_anim = [
(0, 0, 495),
(0, -6 ,495),
(0, -5 ,495),
(0, -5 ,495),
(0, -5 ,495),
(0, -4 ,495),
(0, -3 ,495),
(0, -3 ,495),
(0, -3 ,495),
(0, -2 ,495),
(0, -1 ,496),
(0, -1 ,496),
(0, -1 ,496),
(0, 0,496),
(0, 0,496),
(0, 1,496),
(0, 1,496),
(0, 2,496),
(0, 2,496),
(0, 3,496),
(0, 3,495),
(0, 4,495),
(0, 4,495),
(0, 5,495),
(0, 5,495),
(0, 6,495),
(0, 3,495),

]

bounder_right_anim = [
(0, 0, 493),
(3, -6, 493),
(3, -5, 493),
(3, -5, 493),
(3, -5, 493),
(3, -4, 493),
(3, -3, 493),
(3, -3, 493),
(3, -3, 493),
(3, -2, 493),
(3, -1, 494),
(3, -1, 494),
(3, -1, 494),
(3, 0, 494),
(3, 0, 494),
(3, 1, 494),
(3, 1, 494),
(3, 2, 494),
(3, 2, 494),
(3, 3, 494),
(3, 3, 493),
(3, 4, 493),
(3, 4, 493),
(3, 5, 493),
(3, 5, 493),
(3, 6, 493),
(3, 3, 493),
]

boulder_left_anim = [

(0, 0, 491),
(-3, -6, 491),
(-3, -5, 491),
(-3, -5, 491),
(-3, -5, 491),
(-3, -4, 491),
(-3, -3, 491),
(-3, -3, 491),
(-3, -3, 491),
(-3, -2, 491),
(-3, -1, 492),
(-3, -1, 492),
(-3, -1, 492),
(-3, 0, 492),
(-3, 0, 492),
(-3, 1, 492),
(-3, 1, 492),
(-3, 2, 492),
(-3, 2, 492),
(-3, 3, 492),
(-3, 3, 491),
(-3, 4, 491),
(-3, 4, 491),
(-3, 5, 491),
(-3, 5, 491),
(-3, 6, 491),
(-3, 3, 491),

]


anim_frames = [bounder_right_anim, bounder_right_anim, bounder_right_anim, bounder_right_anim, bounder_right_anim, boulder_left_anim, bounder_still_anim]



class Bounder:
    def __init__(self, img_lookup, bounce_snd):

        self.img_lookup = img_lookup
        self.bounce_snd = bounce_snd 

        self.x = random.randrange(-100,-25)
        self.y = SCREEN_HEIGHT-23
        self.z = random.randrange(0, 25)
        self.anim = None
        self.anim_index = None
        self.spr_index = None

        self.active = True

    def update(self):


        if not self.active:
            return

        if self.x > SCREEN_WIDTH:
            self.active = False
            return

        if self.anim is None:
            self.anim = random.choice(anim_frames)
            self.anim_index = 0
            if SOUND_ENABLED:
                self.bounce_snd.play()
        
        self.x += self.anim[self.anim_index][0]
        self.y += self.anim[self.anim_index][1]
        self.spr_index = self.anim[self.anim_index][2]

        self.anim_index += 1

        if self.anim_index >= len(self.anim):
            self.anim = None
            self.anim_index = None



    def render(self, screen):
        if not self.active:
            return

        spr = self.img_lookup[self.spr_index]
        r = spr.get_rect()
        r.x = self.x
        r.y = self.y - self.z
        

        screen.blit(spr, r)



bounders_to_deploy = 0

def run_bounders():
    global bounders_to_deploy
    global SOUND_ENABLED
        
    pygame.init()

    pygame.mixer.init()
    pygame.mixer.set_num_channels(SOUND_MAX_CHANELS)


    size = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
    speed = [2, 2]
    FILL_COLOUR = 0, 255, 0

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('BOUNDERS')

    bounder_up_straight = pygame.image.load("res/still-stare.png")
    bounder_up_look_down = pygame.image.load("res/still-stare-down.png")

    bounder_right = pygame.image.load("res/bounder_right.png")
    bounder_right_look_down = pygame.image.load("res/bounder_right_look_down.png")

    bounder_left = pygame.image.load("res/bounder_left.png")
    bounder_left_look_down = pygame.image.load("res/bounder_left_look_down.png")

    img_lookup = {
        495: bounder_up_straight,
        496: bounder_up_look_down,

        493: bounder_right,
        494: bounder_right_look_down,

        491: bounder_left,
        492: bounder_left_look_down,
    }


    bounce_snd = pygame.mixer.Sound("res/bounder_bounce.wav")
    bounce_snd.set_volume(SOUND_VOLUME)

    bounders = []




    update_count = 0

    clock = pygame.time.Clock()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bounders_to_deploy += 1
            elif event.type == pygame.KEYDOWN:
                SOUND_ENABLED = not SOUND_ENABLED
                    



        bounders = [b for b in bounders if b.active]


        update_count += 1
        if update_count > 50*5:
            print('alive', len(bounders), 'todeploy', bounders_to_deploy)
            update_count = 0


        if bounders_to_deploy > 0 and len(bounders) < BOUNDERS_MAX_ALIVE:
            if random.choice([True, False,False,False,False,False,False,False,False,False]):
                bounders.append(Bounder(img_lookup, bounce_snd))
                bounders_to_deploy -= 1


        for b in bounders:
            b.update()


        bounders.sort(key=lambda b: b.z)

        screen.fill(FILL_COLOUR)
        for b in bounders:
            b.render(screen)

        pygame.display.flip()

        clock.tick(50)



def run_websocket_client():
    def ws_message(ws, message):
        global bounders_to_deploy
        print("WebSocket msg: %s" % message)
        try:
            msgj = json.loads(message)
            if msgj['event']['type'] == "Raid":
                num_bounders = msgj['data']['viewerCount']
                if num_bounders <= 10:
                    num_bounders = 10
                bounders_to_deploy += num_bounders
            elif msgj['event']['type'] == "Cheer":
                num_bounders = msgj['data']['message']['bits'] // 10
                if num_bounders <= 0:
                    num_bounders = 1
                bounders_to_deploy += num_bounders
            elif msgj['event']['type'] in ("Sub", "ReSub", "GiftSub"):
                num_bounders = msgj['data']['subTier']
                if num_bounders <= 0:
                    num_bounders = 1
                num_bounders *= 5
                bounders_to_deploy += num_bounders
        except Exception as e:
            print(f"Websocket message exception: {traceback.format_exception(type(e), e, e.__traceback__)}")



    def ws_open(ws):
        print("Websocket Opened")

        ws.send('''{
                    "request": "Subscribe",
                    "id": "bounders-subscribe-events-id",
                    "events": {
                        "Twitch": [
                            "Raid",
                            "Cheer",

                            "Sub",
                            "ReSub",
                            "GiftSub",
                            ]
                        },
                    }''')

    def on_error(ws, error):
        print(f"Websocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"Websocket close: ({close_status_code}) {close_msg}")

    def ws_thread(*args):
        ws = websocket.WebSocketApp(STREAMERBOT_WS_URL, on_open=ws_open, on_message=ws_message, on_error=on_error, on_close=on_close)

        while True:
            print("Connecting to websocket")
            try:
                ws.run_forever(reconnect=5)
            except Exception as e:
                print(f"Websocket thread exception: {traceback.format_exception(type(e), e, e.__traceback__)}")
            time.sleep(5)
            
        print("end of thread")

    # Start a new thread for the WebSocket interface
    _thread.start_new_thread(ws_thread, ())


def main():

    run_websocket_client()

    run_bounders()


if __name__ == "__main__":
    main()