# server.py is responsible for sending all information about the game back to the clients

# Imports
import socket
import _thread
import pickle
from entity import Player
from entity import Boss

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Constants
SERVER = "26.76.124.87"
PORT = 5050
BYTES_TO_RECEIVE = 4096*2
RIGHT_BORDER, BOTTOM_BORDER = 500, 750
BOSS_HEALTH = 25
BOSS_SIZE = (RIGHT_BORDER / 5, BOTTOM_BORDER / 5)
SPACE_FOR_LIVES = BOTTOM_BORDER / 10
BLOCK_HEIGHT = BOTTOM_BORDER / 30
GRAVITY = BOTTOM_BORDER / 1000

try:
    server.bind((SERVER, PORT))
except socket.error as e:
    print(e)

server.listen(2)
print("Listening for connections")

entities = {"Player 0": Player(start_pos=(0,  BOTTOM_BORDER - SPACE_FOR_LIVES - BLOCK_HEIGHT), size=(RIGHT_BORDER / 15, BOTTOM_BORDER / 15), health=BOSS_HEALTH * .08, vel_vector=(RIGHT_BORDER / 100, GRAVITY*3), num=0),
           "Player 1": Player(start_pos=(RIGHT_BORDER, BOTTOM_BORDER - SPACE_FOR_LIVES - BLOCK_HEIGHT), size=(RIGHT_BORDER / 15, BOTTOM_BORDER / 15), health=BOSS_HEALTH * .08, vel_vector=(RIGHT_BORDER / 100, GRAVITY*3), num=1),
           "Boss": Boss(start_pos=(RIGHT_BORDER / 2 - BOSS_SIZE[0] / 2, 0), size=BOSS_SIZE, health=BOSS_HEALTH, vel_vector=(RIGHT_BORDER / 400, 0))}
entities["Player 1"].x -= entities["Player 1"].width
entities["Player 0"].y -= entities["Player 0"].height
entities["Player 1"].y -= entities["Player 1"].height

# Function handles each new client. EACH CLIENT MUST BE HANDLED IN A NEW THREAD
def threaded_client(conn, crnt_player):
    if crnt_player == 0:
        entities["Player 0"].connected = True
        conn.send(pickle.dumps({"Player 1": entities["Player 0"], "Player 2": entities["Player 1"], "Boss": entities["Boss"]}))
    elif crnt_player == 1:
        entities["Player 1"].connected = True
        conn.send(pickle.dumps({"Player 1": entities["Player 1"], "Player 2": entities["Player 0"], "Boss": entities["Boss"]}))
    reply = ""
    while True:
        try:
            # Handle boss movement and weapons
            if (not entities["Player 0"].game_over and entities["Player 0"].connected and
             entities["Player 1"].connected): # game_over refers to the entire game being over
                entities["Boss"].handle_movement()
                entities["Boss"].handle_weapons()

            data = pickle.loads(conn.recv(BYTES_TO_RECEIVE))
            entities[f"Player {crnt_player}"] = data["Player 1"]

            # Delete the boss' weapon when a player collides with it and decrease that player's health bar
            if entities[f"Player {crnt_player}"].still_alive:
                for weapon in entities["Boss"].active_weapons:
                    if entities[f"Player {crnt_player}"].is_colliding_with(weapon):
                        entities["Player 0"].explosion = True
                        entities["Player 1"].explosion = True
                        del entities["Boss"].active_weapons[entities["Boss"].active_weapons.index(weapon)]
                        entities[f"Player {crnt_player}"].handle_health(weapon.damage)

                # Delete the player's weapon the boss collides with and decrease the boss's health bar
                for missile in entities[f"Player {crnt_player}"].active_missiles:
                    if entities["Boss"].is_colliding_with(missile):
                        entities["Boss"].handle_health(missile.damage)
                        del entities[f"Player {crnt_player}"].active_missiles[entities[f"Player {crnt_player}"].active_missiles.index(missile)]

            if not data:
                print("disconected")
            else:
                if crnt_player == 1:
                    reply = {"Player 1": entities["Player 1"], "Player 2": entities["Player 0"], "Boss": entities["Boss"]}
                else:
                    reply = {"Player 1": entities["Player 0"], "Player 2": entities["Player 1"], "Boss": entities["Boss"]}

                print("Received", data)
                print("Sending", reply)

            conn.sendall(pickle.dumps(reply))
        except:
            print('error')
            break


player = 0
while True:
    conn, addr = server.accept()
    print("Connected to", addr)
    _thread.start_new_thread(threaded_client, (conn, player))
    player += 1









