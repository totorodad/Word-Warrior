#   _____          __  __ ______  _____ ______ _______      ________ _____  
#  / ____|   /\   |  \/  |  ____|/ ____|  ____|  __ \ \    / /  ____|  __ \ 
# | |  __   /  \  | \  / | |__  | (___ | |__  | |__) \ \  / /| |__  | |__) |
# | | |_ | / /\ \ | |\/| |  __|  \___ \|  __| |  _  / \ \/ / |  __| |  _  / 
# | |__| |/ ____ \| |  | | |____ ____) | |____| | \ \  \  /  | |____| | \ \ 
#  \_____/_/    \_\_|  |_|______|_____/|______|_|  \_\  \/   |______|_|  \_\
# Big text generator used: https://www.fancytextpro.com/BigTextGenerator/Big
#
#gameserver.py
#Game Server Rev 1.0
#Boulder Creek Video Games
#Jim Nolan
#8-Nov-2024
#
#How server operates (The default starting active player is 'Player 1'):
#1. Inactive Clients reqests game data at no more than once a second with the 'ww_reqsdata' command.  All the game data will be
#   sent to that client.  Each client must ask for the data individaully.
#2. If there is a available player (i.e. status on 1 of the 4 players == 'notplaying') then
#   the client can set that WW_player<n> 'status' to 'playing' and claim that as their player slot.
#3. When each player is done with their turn then set the active player to the next Player in the status who has status == 'playing'.
#   If at the end of the list start back at 'Player 1', if no players then set WW_active_player to 'none'
#4. Each client when they are the active player shall send 'ww_acptdata' at least once every second.  It's up to the client to not
#   overwrite their own player hand with the received data from the server (unless it's the first packet received then overwrite the hand.)
#5. If an active player does not send their data via 'ww_acptdata' within 3 seconds then that player is marked status = 'notplaying' and is
#   "kicked" from the game rotation.
#   and the active palyer is set to the next status == 'playing'.

import socket, time, sys, pickle, threading, random, datetime
import requests as req #pip install requests (used to get internet ip address from amazonaws)
from sys import platform
from platform import system

lock = threading.Lock()

#Needed to support reading the keyboard non-blocking
if system() == 'Windows':
  import msvcrt
else:
  import termios #pip install termios (on linux posix platforms only)
  import tty 
  import select

#To support non-blocking keyboard read on posix (linux platforms) use
#termios, on Windows use msvcrt
def linux_is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
def linux_getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

run = True

#   _____                          _       _        
#  / ____|                        | |     | |       
# | |  __  __ _ _ __ ___   ___  __| | __ _| |_ __ _ 
# | | |_ |/ _` | '_ ` _ \ / _ \/ _` |/ _` | __/ _` | #
# | |__| | (_| | | | | | |  __/ (_| | (_| | || (_| |
#  \_____|\__,_|_| |_| |_|\___|\__,_|\__,_|\__\__,_| #

# __          __           _  __          __             _            
# \ \        / /          | | \ \        / /            (_)           
#  \ \  /\  / /__  _ __ __| |  \ \  /\  / /_ _ _ __ _ __ _  ___  _ __ 
#   \ \/  \/ / _ \| '__/ _` |   \ \/  \/ / _` | '__| '__| |/ _ \| '__|
#    \  /\  / (_) | | | (_| |    \  /\  / (_| | |  | |  | | (_) | |   
#     \/  \/ \___/|_|  \__,_|     \/  \/ \__,_|_|  |_|  |_|\___/|_|   
#

WW_game_was_reset = False

# key:
# '#' = empty
                   # 0   1   2   3   4   5   6   7   8   9   0   1   2   3   4  
WW_GAMEBOARD_WORDS = [['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#']]

# key:
# '#' = empty
# '1' = Dirty (just placed)
# '0' = Fixed (old tile)
                   # 0   1   2   3   4   5   6   7   8   9   0   1   2   3   4  
WW_DIRTY_GAMEBOARD = [['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
                   ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#']]

# key:
# hand: '#' = empty, or uppercase character or blank
# status: 'playing', 'notplaying', 'out'
# Support up to 4 players
WW_player1 = {"player": "Player 1", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player2 = {"player": "Player 2", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player3 = {"player": "Player 3", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player4 = {"player": "Player 4", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}

# Total of 101 tiles in a normal set, # = BLANK
WW_letter_key = {'A':9, 'B':2,  'C':2, 'D':4, 'E':12, 
                 'F':2, 'G':3,  'H':2, 'I':9, 'J':1, 
                 'K':1, 'L':4,  'M':2, 'N':6, 'O':8, 
                 'P':2, 'Q':1,  'R':6, 'S':4, 'T':6, 
                 'U':4, 'V':2,  'W':2, 'X':1, 'Y':2, 
                 'Z':1, ' ':2} # ' ' = BLANK TILE, '#' = EMPTY

# word_warrior bag of tiles (normally 100 characters 'tiles)
WW_bag = []

# used to keep track of what the last score was
WW_player_last_score = 0

#Can be: 'Player 1', 'Player 2', 'Player 3', 'Player 4'
WW_active_player = "none"

#Test: Client_player
WW_Client_player = "none"

#WW_bag_join_limit = 50 #There has to be at least half a bag full of tiles to allow a new player to join
WW_bag_join_limit = 2 # for testing **##**

#Keep track of number of syncronization cycles to read game over state (see WW_Check_Game_Over())
check_gameover_count = 0

#Take all the letters in the word_warrior key and mix them up into the word_warrior bag
def WW_mix_bag():
  global WW_bag 

  WW_bag = [] #set bag to empty

  #Insert random tiles into the bag
  for key in WW_letter_key:
      for i in range (0,WW_letter_key[key]):
          WW_Insert_random_tiles_to_bag(WW_bag,key)

  # For test purposes only **##**
  #print("Empty bag to test endgame.  Comment out on line 155")
  #for i in range (0,70):
  #  WW_bag.pop()

def WW_Insert_random_tiles_to_bag(arr, char):
  index = random.randint(0, len(arr))
  arr.insert(index, char)
  return arr

  #If there are empty spots and tiles available in the bag then refill the identified players hand

def get_my_hand(player):
  if (player == "Player 1"):
    return (WW_player1["hand"])
  elif (player == "Player 2"):
    return (WW_player2["hand"])
  elif (player == "Player 3"):
    return (WW_player3["hand"])
  elif (player == "Player 4"):
    return (WW_player4["hand"])
  else:
    print("Error: WW_Client_player not set properly, it's set to:", WW_Client_player)
    exit()

def set_my_hand (player,hand):
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (player == "Player 1"):
    WW_player1["hand"] = hand
  elif (player == "Player 2"):
    WW_player2["hand"] = hand
  elif (player == "Player 3"):
    WW_player3["hand"] = hand
  elif (player == "Player 4"):
    WW_player4["hand"] = hand

def WW_refill_hand (player):
  global WW_bag 

  hand = get_my_hand(player) 

  #Check for return characters (red background characters)
  for i in range (0,7):
    if hand[i].islower():
      WW_Insert_random_tiles_to_bag(WW_bag,hand[i].upper())
      hand[i] = '#'

  print("WW_refill_hand before: ", hand)
  for i in range (0,7):
    if (hand[i] == '#' and len(WW_bag)>0):
      hand[i] = WW_bag.pop()
  print("WW_refill_hand after: ", hand)

  set_my_hand(player,hand)

def player_hand_empty(hand):
  for i in range(0,7):
    if hand[i] != '#':
      return (False)
  else:
    return(True)

def WW_Check_Game_Over():
  global check_gameover_count

  #Check for end of game and subtract off unused player 1 tiles if player 2 went out first

  for x in range (0,15):
    for y in range (0,15):
      if (WW_DIRTY_GAMEBOARD[x][y] == '1'):
        return (False)

  if (len(WW_bag) == 0): #is game bag empty?

    #Don't consider the active player so as to give them time to hit Go and finish their turn
    if (WW_active_player == "Player 1"):
      empty1 = False
    else:
      empty1  = player_hand_empty(WW_player1["hand"])

    if (WW_active_player == "Player 2"):
      empty2  = False
    else:
      empty2  = player_hand_empty(WW_player2["hand"])

    if (WW_active_player == "Player 3"):
      empty3 = False
    else:
      empty3  = player_hand_empty(WW_player3["hand"])

    if (WW_active_player == "Player 4"):
      empty4 = False
    else:
      empty4  = player_hand_empty(WW_player4["hand"])

    playing1 = WW_player1["status"] == "playing"    
    playing2 = WW_player2["status"] == "playing"    
    playing3 = WW_player3["status"] == "playing"    
    playing4 = WW_player4["status"] == "playing"    

    if ((empty1 and playing1) or (empty2 and playing2) or (empty3 and playing3) or (empty4 and playing4)):
      check_gameover_count += 1
      print("Checking game over: ", check_gameover_count)
    else:
      return(False)

    if (check_gameover_count >= 1):
      check_gameover_count = 0
      print("############# WW Server found gameover ############")
      return (True)

#  _   _ ______ _________          ______  _____  _  _______ _   _  _____ 
# | \ | |  ____|__   __\ \        / / __ \|  __ \| |/ /_   _| \ | |/ ____|
# |  \| | |__     | |   \ \  /\  / / |  | | |__) | ' /  | | |  \| | |  __ 
# | . ` |  __|    | |    \ \/  \/ /| |  | |  _  /|  <   | | | . ` | | |_ |
# | |\  | |____   | |     \  /\  / | |__| | | \ \| . \ _| |_| |\  | |__| |
# |_| \_|______|  |_|      \/  \/   \____/|_|  \_\_|\_\_____|_| \_|\_____|
# ------------------------------------------------------------------------------------------                                                                         

#   _____ _ _            _              _____ _____     
#  / ____| (_)          | |   t    /\   |  __ \_   _|    
# | |    | |_  ___ _ __ | |_  e   /  \  | |__) || |  ___ 
# | |    | | |/ _ \ '_ \| __| s  / /\ \ |  ___/ | | / __|
# | |____| | |  __/ | | | |_  t / ____ \| |    _| |_\__ \
#  \_____|_|_|\___|_| |_|\__|  /_/    \_\_|   |_____|___/

def WW_client_request_game_data_from_server():
  global addr, port

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
      server_socket.connect((addr,port))
      #Send the request pickled data from the server (player 1) client handler
      server_socket.sendall(b'ww_reqsdata')

      #Receive the game data from server
      WW_client_request_game_data_from_server_receive_data(server_socket)
      server_socket.close()  
def WW_client_request_game_data_from_server_receive_data(client_socket):
  global WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD,WW_player1,WW_player2,WW_player3,WW_player4,WW_bag,WW_player_last_score
  global WW_active_player
  
  # Receive the size of the pickled data
  data_size = int.from_bytes(client_socket.recv(4), 'big')

  # Receive the pickled data
  data = b''
  while len(data) < data_size:
      packet = client_socket.recv(4096)
      if not packet:
          break
      data += packet

  # Deserialize the data
  d1, d2, d3, d4, d5, d6, d7, d8, d9 = pickle.loads(data)

  WW_GAMEBOARD_WORDS = d1
  WW_DIRTY_GAMEBOARD = d2

  #************  TODO *****************
  #Add detection for being set to status == 'notplaying'

  #If I'm player 1 then don't update my hand from the server data.
  if (WW_Client_player != "Player 1"):
    WW_player1 = d3
  
  #If I'm player 2 then don't update my hand from the server data.
  if (WW_Client_player != "Player 2"):
    WW_player2 = d4
  
  #If I'm player 3 then don't update my hand from the server data.
  if (WW_Client_player != "Player 3"):
    WW_player3 = d5
  
  #If I'm player 4 then don't update my hand from the server data.
  if (WW_Client_player != "Player 4"):
    WW_player4 = d6
  
  WW_bag = d7
  WW_player_last_score = d8

  WW_active_player = d9
  
def WW_client_send_game_data_to_server():
  global addr, port
  global WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((addr,port))
    #Ask server to accept pickled game data
    client_socket.sendall(b'ww_acptdata')

    #Check to make sure WW_Client_player is set
    if (WW_Client_player != "Player 1" and WW_Client_player != "Player 2" and WW_Client_player != "Player 3" and WW_Client_player != "Player 4"):
      print ("Error: WW_client_send_game_data_to_server requires WW_Client_player to be set to a valid player")
      exit()

    #Receive the game data
    if (WW_Client_player == "Player 1"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player_last_score)
      print("WW: Sent Player 1 data to Server")
    elif (WW_Client_player == "Player 2"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player2, WW_player_last_score)
      print("WW: Sent Player 2 data to Server")
    elif (WW_Client_player == "Player 3"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player3, WW_player_last_score)
      print("WW: Sent Player 3 data to Server")
    elif (WW_Client_player == "Player 4"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player4, WW_player_last_score)
      print("WW: Sent Player 4 data to Server")

    client_socket.close()
def WW_client_send_game_data_to_server_send_data(client_socket,d1,d2,d3,d4):
  # Serialize the data
  data = pickle.dumps((d1,d2,d3,d4))

  # Send the length of the pickled data payload as a header
  size = len(data).to_bytes(4, 'big')
  client_socket.sendall(size)
  
  # Send the pickled data payload
  client_socket.sendall(data)

def WW_client_try_to_join_game():
  global addr, port
  
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
      server_socket.connect((addr,port))
      #Send the request pickled data from the server (player 1) client handler
      server_socket.sendall(b'ww_joingame')

      #Receive the game data from server
      WW_player = WW_client_try_to_join_receive_data(server_socket)
      server_socket.close() 
  return(WW_player)
def WW_client_try_to_join_receive_data(client_socket):
  # Receive the size of the pickled data
  data_size = int.from_bytes(client_socket.recv(4), 'big')

  # Receive the pickled data
  data = b''
  while len(data) < data_size:
      packet = client_socket.recv(4096)
      if not packet:
          break
      data += packet

  # Deserialize the data
  return (pickle.loads(data))

def WW_client_leave_game(WW_player_name):
  global addr, port

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
      client_socket.connect((addr,port))
      #Ask server to accept pickled game data
      client_socket.sendall(b'ww_leavgame')

      #Receive the game data
      WW_client_leave_game_send_data(client_socket,WW_player_name)
      print("WW: Send command for: ", WW_player_name," to leave the game")
      client_socket.close()
def WW_client_leave_game_send_data(client_socket,WW_player_name):

    # Serialize the data
    data = pickle.dumps(WW_player_name)

    # Send the length of the pickled data payload as a header
    size = len(data).to_bytes(4, 'big')
    client_socket.sendall(size)
    
    # Send the pickled data payload
    client_socket.sendall(data)

def WW_client_send_turn_over_command():
  global addr, port
  
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((addr,port))
    #Ask server to accept pickled game data
    client_socket.sendall(b'ww_turnover')

    client_socket.close()


#  _______        _      _____ _ _            _       
# |__   __|      | |    / ____| (_)          | |      
#    | | ___  ___| |_  | |    | |_  ___ _ __ | |_ ___ 
#    | |/ _ \/ __| __| | |    | | |/ _ \ '_ \| __/ __|
#    | |  __/\__ \ |_  | |____| | |  __/ | | | |_\__ \
#    |_|\___||___/\__|  \_____|_|_|\___|_| |_|\__|___/

def player1_test_client():
  global WW_player1 
  global WW_Client_player

  print("Starting Player 1 test client")
  WW_player1 = WW_client_try_to_join_game()
  WW_Client_player = WW_player1["player"]
  
  print("WW: player1_test_client joined as player: ", WW_Client_player)

  while True:
    #Get the game data that shows Player 1 is the active player
    WW_client_request_game_data_from_server()

    print("WW: test client player 1 WW_active_player: ", WW_active_player)
    if WW_active_player == "Player 1":
      my_turn = True 
    else:
      my_turn = False

    if my_turn == True:
      for i in range (0,5):
        print("WW: Client player 1 send data to server with ww_acptdata")
        WW_client_send_game_data_to_server()
        WW_player1["score"] += 1
        time.sleep(1)

      WW_client_send_turn_over_command()
      my_turn = False

    while not my_turn:
      print("WW: Client player 1 Requeting data from server with ww_reqsdata")
      WW_client_request_game_data_from_server()
      time.sleep(1)
      if (WW_active_player == "Player 1"):
        my_turn = True

def player2_test_client():
  global WW_player2 
  global WW_Client_player

  print("Starting Player 2 test client")
  WW_player2 = WW_client_try_to_join_game()
  WW_Client_player = WW_player2["player"]

  print("WW: player2_test_client joined as player: ", WW_Client_player)

  while True:
    #Get the game data that shows Player 2 is the active player
    WW_client_request_game_data_from_server()

    print("WW: test client player 2 WW_active_player: ", WW_active_player)
    if WW_active_player == "Player 2":
      my_turn = True 
    else:
      my_turn = False

    if my_turn == True:
      for i in range (0,5):
        print("WW: Client player 2 send data to server with ww_acptdata")
        WW_client_send_game_data_to_server()
        WW_player2["score"] += 1
        time.sleep(1)

      WW_client_send_turn_over_command()
      my_turn = False

    while not my_turn:
      print("WW: Client player 2 Requeting data from server with ww_reqsdata")
      WW_client_request_game_data_from_server()
      time.sleep(1)
      if (WW_active_player == "Player 2"):
        my_turn = True

def player3_test_client():
  global WW_player3 
  global WW_Client_player

  while True:
    print("Starting Player 3 test client")
    WW_player3 = WW_client_try_to_join_game()
    WW_Client_player = WW_player3["player"]

    print("WW: player3_test_client joined as player: ", WW_Client_player)

    count_loop = 0

    while count_loop < 2:
      count_loop += 1
    
      #Get the game data that shows Player 3 is the active player
      WW_client_request_game_data_from_server()

      print("WW: test client player 3 WW_active_player: ", WW_active_player)
      if WW_active_player == "Player 3":
        my_turn = True 
      else:
        my_turn = False

      if my_turn == True:
        for i in range (0,5):
          print("WW: Client player 3 send data to server with ww_acptdata")
          WW_client_send_game_data_to_server()
          WW_player3["score"] += 1
          time.sleep(1)

        WW_client_send_turn_over_command()
        my_turn = False

      while not my_turn:
        print("WW: Client player 3 Requeting data from server with ww_reqsdata")
        WW_client_request_game_data_from_server()
        time.sleep(1)
        if (WW_active_player == "Player 3"):
          my_turn = True

    WW_client_leave_game("Player 3")
    time.sleep (2)

def player4_test_client():
  global WW_player4 
  global WW_Client_player

  print("Starting Player 4 test client")
  WW_player4 = WW_client_try_to_join_game()
  WW_Client_player = WW_player4["player"]

  print("WW: player4_test_client joined as player: ", WW_Client_player)

  while True:
    #Get the game data that shows Player 4 is the active player
    WW_client_request_game_data_from_server()

    print("WW: test client player 4 WW_active_player: ", WW_active_player)
    if WW_active_player == "Player 4":
      my_turn = True 
    else:
      my_turn = False

    if my_turn == True:
      for i in range (0,5):
        print("WW: Client player 4 send data to server with ww_acptdata")
        WW_client_send_game_data_to_server()
        WW_player4["score"] += 1
        time.sleep(1)

      WW_client_send_turn_over_command()
      my_turn = False

    while not my_turn:
      print("WW: Client player 4 Requeting data from server with ww_reqsdata")
      WW_client_request_game_data_from_server()
      time.sleep(1)
      if (WW_active_player == "Player 4"):
        my_turn = True


#   _____                                     _____ _____     
#  / ____|                              /\   |  __ \_   _|    
# | (___   ___ _ ____   _____ _ __     /  \  | |__) || |  ___ 
#  \___ \ / _ \ '__\ \ / / _ \ '__|   / /\ \ |  ___/ | | / __|
#  ____) |  __/ |   \ V /  __/ |     / ____ \| |    _| |_\__ \
# |_____/ \___|_|    \_/ \___|_|    /_/    \_\_|   |_____|___/

# Receive data from client
def WW_receive_data(client_socket):
  global WW_GAMEBOARD_WORDS,WW_DIRTY_GAMEBOARD,WW_player1,WW_player2,WW_player3,WW_player4,WW_player_last_score
  global WW_active_player

  # Receive the size of the pickled data
  data_size = int.from_bytes(client_socket.recv(4), 'big')

  print("Data Size: ", data_size)

  # Receive the pickled data
  data = b''
  while len(data) < data_size:
      packet = client_socket.recv(4096)
      if not packet:
          break
      data += packet

  # Deserialize the data
  d1, d2, d3, d4 = pickle.loads(data)

  WW_GAMEBOARD_WORDS = d1
  WW_DIRTY_GAMEBOARD = d2
  
  # 13-Nov-2024: The client is sending only their data to be recorded at the server.  All other game data from the 
  # non active player should be ignored. 
  WW_temp_player = d3
  WW_client_player = WW_temp_player["player"]

  if (WW_client_player == "Player 1"):
    WW_player1 = d3
  elif (WW_client_player == "Player 2"):
    WW_player2 = d3
  elif (WW_client_player == "Player 3"):
    WW_player3 = d3
  elif (WW_client_player == "Player 4"):
    WW_player4 = d3
  else:
    print("Error client sent badly encoded client in game data (WW_receive_data)")
    exit(1)

  WW_player_last_score = d4

# Transmit data to client
def WW_send_data(client_socket,d1,d2,d3,d4,d5,d6,d7,d8,d9):

    # Serialize the data
    data = pickle.dumps((d1,d2,d3,d4,d5,d6,d7,d8,d9))

    # Send the length of the pickled data payload as a header
    size = len(data).to_bytes(4, 'big')
    client_socket.sendall(size)
    
    # Send the pickled data payload
    client_socket.sendall(data)

def WW_player_join_game(client_socket):
  # New Client would like to join the game
  # 1. Check to see if there are no active players and if so the requesting client gets assigned Player 1
  #    Also randomize the scrabble bag and give 7 random characters from the bag to their hand.
  #    Send the player dictionary for the player assigned.
  # Else:
  # 1. Find the next available 'notplaying' player.
  # 2. Assign the open player spot if it exists to the requesting client by setting 'status' to 'playing'
  # 3. If player gets a spot send them their new palyer name. ('Player 1'. 'Player 2', ect.)
  # 4. Fill their hand with tiles from the bag and send their dictionary back to the client (newly joined player)
  # Else: If there is not room left for a new player send Player game data with player == 'none' dictionary
  global WW_player1,WW_player2,WW_player3,WW_player4,WW_active_player
  global WW_game_was_reset

  WW_new_player = {"player": "none", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}

  print("WW: Client from socket: ",client_socket," trying to joing the game")

  print("current libraries of players as seen by the server:")
  print(WW_player1)
  print(WW_player2)
  print(WW_player3)
  print(WW_player4)

  #Check for new game if so create a new mixed up bag of tiles
  if(WW_player1["status"] == "notplaying" and WW_player2["status"] == "notplaying" and\
     WW_player3["status"] == "notplaying" and WW_player4["status"] == "notplaying"):
    #Adding the first player
    #Mix the word warrior bag and load the first 7 characters into Player 1's hand.
    WW_mix_bag()
    print("WW: New Game, mixed up bag")
    WW_active_player = "Player 1"
    WW_game_was_reset = False #Allow ww_gameover signal from client to reset the game now that there is a new player

  if (WW_player1["status"] == "notplaying" and len(WW_bag) >= WW_bag_join_limit):
    WW_player1["status"] = "playing"
    # Add tiles to new players hand.
    WW_player1["hand"] = ['#','#','#','#','#','#','#']
    WW_refill_hand ("Player 1")
    WW_new_player = WW_player1 
    print("WW: Player 1 joined the game from client: ", client_socket)

  elif (WW_player2["status"] == "notplaying" and len(WW_bag) >= WW_bag_join_limit):
    WW_player2["status"] = "playing"
    # Add tiles to new players hand.
    WW_player2["hand"] = ['#','#','#','#','#','#','#']
    WW_refill_hand ("Player 2")
    print("WW: Player 2 joined the game from client: ", client_socket)
    WW_new_player = WW_player2 

  elif (WW_player3["status"] == "notplaying" and len(WW_bag) >= WW_bag_join_limit):
    WW_player3["status"] = "playing"
    # Add tiles to new players hand.
    WW_player3["hand"] = ['#','#','#','#','#','#','#']
    WW_refill_hand ("Player 3")
    print("WW: Player 3 joined the game from client: ", client_socket)
    WW_new_player = WW_player3 

  elif (WW_player4["status"] == "notplaying" and len(WW_bag) >= WW_bag_join_limit):
    WW_player4["status"] = "playing"
    # Add tiles to new players hand.
    WW_player4["hand"] = ['#','#','#','#','#','#','#']
    WW_refill_hand ("Player 4")
    print("WW: Player 4 joined the game from client: ", client_socket)
    WW_new_player = WW_player4 

  else:
    print("WW: Sorry game is full. Set player dictionary name to 'none'")
    if (len(WW_bag) < WW_bag_join_limit):
      print("WW: Sorry not enough tiles to allow the new player to join")

  #Send back to client the player slot they were assigned or 'gamefull' if there are too many players
  # Serialize the data
  data = pickle.dumps((WW_new_player))

  # Send the length of the pickled data payload as a header
  size = len(data).to_bytes(4, 'big')
  client_socket.sendall(size)
  
  # Send the pickled data payload
  client_socket.sendall(data)

def WW_player_leave_game(client_socket):
  # Set the players 'status' to 'notplaying' and return their hand tiles to the bag
  global WW_bag,WW_player1,WW_player2,WW_player3,WW_player4

  print("WW: Player leaving game from socket: ", client_socket)
    
  # Receive the size of the pickled data
  data_size = int.from_bytes(client_socket.recv(4), 'big')

  # Receive the pickled data
  data = b''
  while len(data) < data_size:
      packet = client_socket.recv(4096)
      if not packet:
          break
      data += packet

  # D1 is the index of the WW_player dictionary
  player_name = pickle.loads(data)

  print ("WW: Player: ",player_name," has requested to leave the game")

  if (player_name == "Player 1"):
    WW_player1["status"] = "notplaying"
    WW_player1["score"] = 0
    WW_recover_tiles_from_player(player_name)
    #If the active player leaves the game then go to the next player
    if (WW_active_player == player_name):
      WW_player_turn_over()

  elif (player_name == "Player 2"):
    WW_player2["status"] = "notplaying"
    WW_player2["score"] = 0
    WW_recover_tiles_from_player(player_name)
    #If the active player leaves the game then go to the next player
    if (WW_active_player == player_name):
      WW_player_turn_over()

  elif (player_name == "Player 3"):
    WW_player3["status"] = "notplaying"
    WW_player3["score"] = 0
    WW_recover_tiles_from_player(player_name)
    #If the active player leaves the game then go to the next player
    if (WW_active_player == player_name):
      WW_player_turn_over()

  elif (player_name == "Player 4"):
    WW_player4["status"] = "notplaying"
    WW_player4["score"] = 0
    WW_recover_tiles_from_player(player_name)
    #If the active player leaves the game then go to the next player
    if (WW_active_player == player_name):
      WW_player_turn_over()

  #Recover the tile from the leaving players hand if there are any
  WW_recover_tiles_from_player(player_name)
      
def WW_player_turn_over():
  global WW_active_player

  print("WW: current WW_active_player: ", WW_active_player)
  #find the player and make them active player
  if (WW_active_player == "Player 1"):
    if (WW_player2["status"] == "playing"):
      WW_active_player = "Player 2"
    elif (WW_player3["status"] == "playing"):
      WW_active_player = "Player 3"
    elif (WW_player4["status"] == "playing"):
      WW_active_player = "Player 1"
    elif (WW_player1["status"] != "playing"):
      WW_active_player = "none" # all players are set to status 'notplaying'

  elif (WW_active_player == "Player 2"):
    if (WW_player3["status"] == "playing"):
      WW_active_player = "Player 3"
    elif (WW_player4["status"] == "playing"):
      WW_active_player = "Player 4"
    elif (WW_player1["status"] == "playing"):
      WW_active_player = "Player 1"
    elif (WW_player2["status"] != "playing"):
      WW_active_player = "none" # all players are set to status 'notplaying'

  elif (WW_active_player == "Player 3"):
    if (WW_player4["status"] == "playing"):
      WW_active_player = "Player 4"
    elif (WW_player1["status"] == "playing"):
      WW_active_player = "Player 1"
    elif (WW_player2["status"] == "playing"):
      WW_active_player = "Player 2"
    elif (WW_player3["status"] != "playing"):
      WW_active_player = "none" # all players are set to status 'notplaying'

  elif (WW_active_player == "Player 4"):
    if (WW_player1["status"] == "playing"):
      WW_active_player = "Player 1"
    elif (WW_player2["status"] == "playing"):
      WW_active_player = "Player 2"
    elif (WW_player3["status"] == "playing"):
      WW_active_player = "Player 3"
    elif (WW_player4["status"] != "playing"):
      WW_active_player = "none" # all players are set to status 'notplaying'

  print("WW: new WW_active_player: ", WW_active_player)

def WW_recover_tiles_from_player(Player_name):
  global WW_player1,WW_player2,WW_player3,WW_player4

  if (Player_name == "Player 1"):
    for i in range(0,7):
      if (WW_player1["hand"][i] != '#'):
        WW_bag.append(WW_player1["hand"][i])
        WW_player1["hand"][i] = '#'

  if (Player_name == "Player 2"):
    for i in range(0,7):
      if (WW_player2["hand"][i] != '#'):
        WW_bag.append(WW_player2["hand"][i])
        WW_player2["hand"][i] = '#'

  if (Player_name == "Player 3"):
    for i in range(0,7):
      if (WW_player3["hand"][i] != '#'):
        WW_bag.append(WW_player3["hand"][i])
        WW_player3["hand"][i] = '#'

  if (Player_name == "Player 4"):
    for i in range(0,7):
      if (WW_player4["hand"][i] != '#'):
        WW_bag.append(WW_player4["hand"][i])
        WW_player4["hand"][i] = '#'

def WW_check_no_active_players_reset():
  global WW_GAMEBOARD_WORDS
  global WW_DIRTY_GAMEBOARD
  global WW_Client_player_last_score
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (WW_player1["status"] == "notplaying" and WW_player2["status"] == "notplaying" and WW_player3["status"] == "notplaying" and WW_player4["status"] == "notplaying"):
    print("WW: No active players: Reseting game data")

    #Reset the gameboard trackers
    for x in range(0,15):
      for y in range (0,15):
        WW_GAMEBOARD_WORDS[y][x] = '#'
        WW_DIRTY_GAMEBOARD[y][x] = '#'

    WW_player1 = {"player": "Player 1", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player2 = {"player": "Player 2", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player3 = {"player": "Player 3", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player4 = {"player": "Player 4", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_Client_player_last_score = 0
    WW_mix_bag()

def WW_kick_timedout_player(player):
  global WW_player1,WW_player2,WW_player3,WW_player4

  if (player == "Player 1" and WW_player1["status"] == "playing"):
    WW_player1["status"] = "notplaying"
    print("Payer 1 ****kicked**** from timout")
    #pick the next playing character to be the WW_active_player
    WW_recover_tiles_from_player("Player 1")
    WW_player1["score"] = 0
    if (WW_active_player == "Player 1"):
      WW_player_turn_over()
    WW_check_no_active_players_reset()

  elif (player == "Player 2" and WW_player2["status"] == "playing"):
    WW_player2["status"] = "notplaying"
    print("Payer 2 ****kicked**** from timout")
    #pick the next playing character to be the WW_active_player
    WW_recover_tiles_from_player("Player 2")
    WW_player2["score"] = 0
    if (WW_active_player == "Player 2"):
      WW_player_turn_over()
    WW_check_no_active_players_reset()

  elif (player == "Player 3" and WW_player3["status"] == "playing"):
    WW_player3["status"] = "notplaying"
    print("Payer 1 ****kicked**** from timout")
    #pick the next playing character to be the WW_active_player
    WW_recover_tiles_from_player("Player 3")
    WW_player3["score"] = 0
    if (WW_active_player == "Player 3"):
      WW_player_turn_over()
    WW_check_no_active_players_reset()

  elif (player == "Player 4" and WW_player4["status"] == "playing"):
    WW_player4["status"] = "notplaying"
    print("Payer 4 ****kicked**** from timout")
    #pick the next playing character to be the WW_active_player
    WW_recover_tiles_from_player("Player 4")
    WW_player4["score"] = 0
    if (WW_active_player == "Player 4"):
      WW_player_turn_over()
    WW_check_no_active_players_reset()

def game_in_progress():
  if (WW_player1["status"] == "playing" or WW_player2["status"] == "playing" or WW_player3["status"] == "playing" or WW_player4["status"] == "playing"):
    return (True)
  else:
    return (False)

def WW_game_reset():
  # This is called from the ww_gameover signal from at least one client.  This resets
  # the game from the perspective of the gameserver.  All other clients will be allowed to join
  # again if they want to after this.

  global WW_GAMEBOARD_WORDS
  global WW_DIRTY_GAMEBOARD
  global WW_Client_player_last_score
  global WW_player1, WW_player2, WW_player3, WW_player4
  global WW_game_was_reset

  #Check if one player has caused a reset to the game by sending the ww_gameover signal to the server
  #Only reset the game if we have not reset the game yet.
  print("##################  Game over status: ", WW_Check_Game_Over())
  if (WW_Check_Game_Over() == True):
    print("   _____                        _____                _   ")
    print("  / ____|                      |  __ \\              | |  ")
    print(" | |  __  __ _ _ __ ___   ___  | |__) |___  ___  ___| |_ ")
    print(" | | |_ |/ _` | '_ ` _ \\ / _ \\ |  _  // _ \\/ __|/ _ \\ __|")
    print(" | |__| | (_| | | | | | |  __/ | | \\ \\  __/\\__ \\  __/ |_ ")
    print("  \\_____|\\__,_|_| |_| |_|\\___| |_|  \\_\\___||___/\\___|\\__|")

    #Reset the gameboard trackers
    for x in range(0,15):
      for y in range (0,15):
        WW_GAMEBOARD_WORDS[y][x] = '#'
        WW_DIRTY_GAMEBOARD[y][x] = '#'

    #Reset the player game data (everybody gets the boot)
    WW_player1 = {"player": "Player 1", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player2 = {"player": "Player 2", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player3 = {"player": "Player 3", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
    WW_player4 = {"player": "Player 4", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']} 

    WW_Client_player_last_score = 0

def WW_Server_refill_hand(client_socket): # cmd == 'ww_reflhand'
  global WW_GAMEBOARD_WORDS,WW_DIRTY_GAMEBOARD,WW_player1,WW_player2,WW_player3,WW_player4,WW_player_last_score
  global WW_active_player

  # Receive the size of the pickled data
  data_size = int.from_bytes(client_socket.recv(4), 'big')
 
  # Receive the pickled data
  data = b''
  while len(data) < data_size:
      packet = client_socket.recv(4096)
      if not packet:
          break
      data += packet

  # Deserialize the data
  d1 = pickle.loads(data)

  #The player passed in d1 is which player to refill
  player = d1

  print("******Refill hand called for player: ", player)
 
  WW_refill_hand (player) #Example Client sends ww_reflhand with 'Player 1'

  if (player == "Player 1"):
    refilled_player_library = WW_player1
  elif (player == "Player 2"):
    refilled_player_library = WW_player2
  elif (player == "Player 3"):
    refilled_player_library = WW_player3
  elif (player == "Player 4"):
    refilled_player_library = WW_player4
  else:
    print("Error client sent invalid hand to refill: ", player)

  print("Sending to client refilled player library: ", refilled_player_library) 

  #Send back to client the player slot they were assigned or 'gamefull' if there are too many players
  # Serialize the data
  data = pickle.dumps((refilled_player_library))

  # Send the length of the pickled data payload as a header
  size = len(data).to_bytes(4, 'big')
  client_socket.sendall(size)
  
  # Send the pickled data payload
  client_socket.sendall(data)

def WW_Server_is_gameover(client_socket):
  # Serialize the data

  gameover_check = WW_Check_Game_Over()
  data = pickle.dumps((gameover_check))

  # Send the length of the pickled data payload as a header
  size = len(data).to_bytes(4, 'big')
  client_socket.sendall(size)
  
  # Send the pickled data payload
  client_socket.sendall(data)


#   _____ _ _            _     _    _                 _ _           
#  / ____| (_)          | |   | |  | |               | | |          
# | |    | |_  ___ _ __ | |_  | |__| | __ _ _ __   __| | | ___ _ __ 
# | |    | | |/ _ \ '_ \| __| |  __  |/ _` | '_ \ / _` | |/ _ \ '__|
# | |____| | |  __/ | | | |_  | |  | | (_| | | | | (_| | |  __/ |   
#  \_____|_|_|\___|_| |_|\__| |_|  |_|\__,_|_| |_|\__,_|_|\___|_|   
#
# This server receives these 11-byte well formed commands from the client:
#
# command: ww_reqsdat1,ww_reqsdat2,ww_reqsdat3,ww_reqsdat4
# effect : Requests pickled game data to the Word Warrior client for player 1,2,3 and 4
#
# command: ww_reqslite
# effect : Requests only the game data to update client's view of: bag and status
#          Note that all the game data is sent.  The active player client must sort thru what they need.
#
# command: ww_acptdata
# effect : Accepts pickled games data from the Word Warrior client
#
# command: ww_joingame
# effect : New Client tries to join the game.  This function returns
#          the player data in the same format as WW_playerN (dictionary)
#
# command: ww_leavgame
# effect : Existing player to leave game (return their game tiles to bag)
#
# command: ww_turnover
# effect : Switch to the next player if they are an active client
#
# command: ww_gameover
# effect : If Game over is detected in the player data and this signal is recieved
#          reset the game data.
#
# command: ww_reflhand
# effect : If needed refill players hand with tiles
#
# command: ww_reqgmovr
# effect : Client side askes if a gameover has been sent to the server, respond True or False


def gameserver_client_handler(client_socket):
  #TODO Add locking to avoid multiple threads from updating the game data at the same time.

  global player1_kick_loop_time,player2_kick_loop_time,player3_kick_loop_time,player4_kick_loop_time 
  #global lock 

  while True:

      #lock.acquire() #Lock to just one thread
      
      #Receive the 11 byte command (recvdata or senddata)
      data = client_socket.recv(11)
      if not data:
          break
      cmd = data.decode()

      print("***** command: ",cmd)
      
      #Word Warrior command from Word Warrior game Clients
      if cmd == "ww_reqsdat1":
        print("WW: Sever sends word warrior game data to client (cmd=ww_reqsdata)")
        WW_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player)
        player1_kick_loop_time = 0

      elif cmd == "ww_reqsdat2":
        print("WW: Sever sends word warrior game data to client (cmd=ww_reqsdata)")
        WW_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player)
        player2_kick_loop_time = 0

      elif cmd == "ww_reqsdat3":
        print("WW: Sever sends word warrior game data to client (cmd=ww_reqsdata)")
        WW_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player)
        player3_kick_loop_time = 0
    
      elif cmd == "ww_reqsdat4":
        print("WW: Sever sends word warrior game data to client (cmd=ww_reqsdata)")
        WW_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player)
        player4_kick_loop_time = 0
      
      elif cmd == "ww_reqslite":
        print("WW: Active player client requests lite game data. (cmd=ww_reqslite)")
        WW_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player1, WW_player2, WW_player3, WW_player4, WW_bag, WW_player_last_score, WW_active_player)
      
      elif cmd == "ww_acptdata":
        print("WW: Server accepts game data from word warrior client (cmd=ww_acptdata)")
        WW_receive_data(client_socket)
        if (WW_active_player == "Player 1"):
          player1_kick_loop_time = 0
        if (WW_active_player == "Player 2"):
          player2_kick_loop_time = 0
        if (WW_active_player == "Player 3"):
          player3_kick_loop_time = 0
        if (WW_active_player == "Player 4"):
          player4_kick_loop_time = 0

      elif cmd == "ww_joingame":
        player1_kick_loop_time = 0
        player2_kick_loop_time = 0
        player3_kick_loop_time = 0
        player4_kick_loop_time = 0
        print("WW: New Client trying to join the game")
        WW_player_join_game(client_socket)

      elif cmd == "ww_leavgame":
        player1_kick_loop_time = 0
        player2_kick_loop_time = 0
        player3_kick_loop_time = 0
        player4_kick_loop_time = 0
        print("WW: Existing player trying to leave the game")
        WW_player_leave_game(client_socket)

      elif cmd == "ww_turnover":
        player1_kick_loop_time = 0
        player2_kick_loop_time = 0
        player3_kick_loop_time = 0
        player4_kick_loop_time = 0
        print("WW: Signal Server the Existing players turn is over")
        print("WW: Player turnover called from client: ", client_socket)
        WW_player_turn_over()
        
      elif cmd == "ww_gameover":
        player1_kick_loop_time = 0
        player2_kick_loop_time = 0
        player3_kick_loop_time = 0
        player4_kick_loop_time = 0
        print("WW: ================> Signal Server a Client has detected Game over <==================")
        WW_game_reset()

      elif cmd == "ww_reflhand":
        player1_kick_loop_time = 0
        player2_kick_loop_time = 0
        player3_kick_loop_time = 0
        player4_kick_loop_time = 0
        print("WW: Signal Server to refill a hand (their turn is over)")
        WW_Server_refill_hand(client_socket)

      elif cmd == "ww_reqgmovr":
        print("WW: Ask server if there was a game over signal sent")
        WW_Server_is_gameover(client_socket)
      
      else:
          print("WW: Unknown command from client: ", repr(cmd))

      #lock.release()

def gameserver_start_server():
    global addr,port,run
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((addr, port))
    server_socket.listen(5)

    print("WW: Server listening on :",addr,port)

    while run:
        client_socket, addr = server_socket.accept()
        print(f"WW: Connection from {addr}")
        thread = threading.Thread(target=gameserver_client_handler, args=(client_socket,))
        thread.start()
 
#  _   _      _                      _       _____      _               
# | \ | |    | |                    | |     / ____|    | |              
# |  \| | ___| |___      _____  _ __| | __ | (___   ___| |_ _   _ _ __  
# | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /  \___ \ / _ \ __| | | | '_ \ 
# | |\  |  __/ |_ \ V  V / (_) | |  |   <   ____) |  __/ |_| |_| | |_) |
# |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\ |_____/ \___|\__|\__,_| .__/ 
#                                                                | |    
#                                                                |_|    

port = 5000
hostname = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
addr = sock.getsockname()[0]

print("Welcome to the Boulder Creek Video Games: Gameserer Rev 1.0, 8-Nov-2024")
print("Your Computer Name is:", hostname)
print("Your Computer IP Address is:", addr)

#game_server_address = 'bouldercreekgames.duckdns.org'
game_server_address = addr 
print("Binding to: ",addr," Listening on port: ", port)
print("Make sure to port forward TCP/IP port: ",port, "on your router/gateway/modem.")

url        = 'https://checkip.amazonaws.com'
request    = req.get(url)
InternetIP = request.text
print("Your internet IP Address is:", InternetIP)


#Check for test argument
if(len(sys.argv)==2):
  if (sys.argv[1] == "-player1"):
    player1_test_client()
  elif (sys.argv[1] == "-player2"):
    player2_test_client()
  elif (sys.argv[1] == "-player3"):
    player3_test_client()
  elif (sys.argv[1] == "-player4"):
    player4_test_client()

#Start game data server
server_thread = threading. Thread(target=gameserver_start_server)
server_thread.start()

print("Press 't' to toggle dumping game data.")
print("Press CTRL-BREAK (sometimes CTRL-SCRLK Button) to stop the server.")

#  __  __       _         _                       
# |  \/  |     (_)       | |                      
# | \  / | __ _ _ _ __   | |     ___   ___  _ __  
# | |\/| |/ _` | | '_ \  | |    / _ \ / _ \| '_ \ 
# | |  | | (_| | | | | | | |___| (_) | (_) | |_) |
# |_|  |_|\__,_|_|_| |_| |______\___/ \___/| .__/ 
#                                          | |    
#                                          |_|    

count = 0

player1_kick_loop_time = 0
player2_kick_loop_time = 0
player3_kick_loop_time = 0
player4_kick_loop_time = 0

dump_data = True
char = ''
kick_time_limit = 9 # 10 seconds of inactive with the sever gets you kicked
time.sleep (2)

while run:
  count += 1 

  if (system() != 'Windows'):
    if linux_is_data():
      char = linux_getch()
  else:
    if (msvcrt.kbhit()):
      char = msvcrt.getch()
      print("char: ", char)
  
  if (char == b't'):
      char = ''
      if (dump_data == False):
        dump_data = True
        #print("Dumping data")
      else:
        dump_data = False 
        print("Game data dump 'stopped'  Press 't' to toggle back on")

  if (dump_data):
    print("Server uptime: ", str(datetime.timedelta(seconds=count))," Bag Size (",len(WW_bag),")")
    print("Player kick_loop_time (1-4): ", player1_kick_loop_time,":",player2_kick_loop_time,":",player3_kick_loop_time,":",player4_kick_loop_time)
    print("Active player is: ", WW_active_player)
    print(WW_player1)
    print(WW_player2)
    print(WW_player3)
    print(WW_player4)
    #print("WW_bag: ",WW_bag)

  #Three second rule:  The current players client is inactive with requesting server data for 3seconds then they get kicked
  if (player1_kick_loop_time > kick_time_limit):
    player1_kick_loop_time = 0
    WW_kick_timedout_player("Player 1")    

  if (player2_kick_loop_time > kick_time_limit):
    player2_kick_loop_time = 0
    WW_kick_timedout_player("Player 2")    

  if (player3_kick_loop_time > kick_time_limit):
    player3_kick_loop_time = 0
    WW_kick_timedout_player("Player 3")    

  if (player4_kick_loop_time > kick_time_limit):
    player4_kick_loop_time = 0
    WW_kick_timedout_player("Player 4")    

  player1_kick_loop_time += 1
  player2_kick_loop_time += 1
  player3_kick_loop_time += 1
  player4_kick_loop_time += 1
  
  time.sleep(1)