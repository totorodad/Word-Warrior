# __          __           _  __          __             _            
# \ \        / /          | | \ \        / /            (_)           
#  \ \  /\  / /__  _ __ __| |  \ \  /\  / /_ _ _ __ _ __ _  ___  _ __ 
#   \ \/  \/ / _ \| '__/ _` |   \ \/  \/ / _` | '__| '__| |/ _ \| '__| + AL
#    \  /\  / (_) | | | (_| |    \  /\  / (_| | |  | |  | | (_) | |   
#     \/  \/ \___/|_|  \__,_|     \/  \/ \__,_|_|  |_|  |_|\___/|_|   
#                                                                     
#                                                                     
# Big text generator used: https://www.fancytextpro.com/BigTextGenerator/Big
#
#wordwarrior_client_5.6.py (client only)
#Use with gameserver_5.6.py
REVISION = "5.6"
#Boulder Creek Video Games
#Jim Nolan and Family
#14-JAN-2025
#
#Dependancies:
# - Must install pygame and requests
#
#Game Notes:
# - 4 players supported
# - Added capability to return characters by right clicking on characters in hand
# - Added dictionary lookup by clicking on the dictionary icon.
# - Added F1 help screen
# - Added center click on work for deffinition pop up.
# - Created computer player AL (Artificail Linguist) implemented on the server (and local test F2 copy)
# - Added spell check and word formation check on Go button.
# - Added forfeit check box
# - Added left click on player card to show the last 10 words they have played.
# - Added F3 pop up screen for the list of tiles that are available
# - Re-write network API to be more robust supporting re-tries
# - 5.2
# - Added more robustness to the socket connection, message send, cmd send, and message receive.
# - Connect to a socket at the Join game and keep the socket connected until the game is over.
# - 5.3-5.6 Optimize data sharing with the server.
#
# TODO:
# - TBD
#
# installed libraries:
# pip install pygame requests

import pygame # pip install pygame
import math,time,sys,random,pickle,socket,threading,textwrap,copy,os
import requests as req # pip install requests
import traceback

verbose = False

port = 5000

hostname = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
addr = sock.getsockname()[0]
#print ("Forcing addr to 10.0.0.7")
#addr = "10.0.0.7"

print("Your Computer Name is:", hostname)
print("Your Computer IP Address is:", addr)

game_server_address = addr 
print("Connect to gameserver on port: ", port)

# NOTE: this method for getting internet address is not reliable
#Get internet address.  Note this function is dependent on amazonaws
#After the Amazon corprate wars in 2082 this function may not work any
#more.
#url        = 'https://checkip.amazonaws.com'
#request    = req.get(url)
#InternetIP = request.text
#print("Your internet IP Address is:", InternetIP)

TILES_WIDTH  = 40
TILES_HEIGHT = 40

GAMEBOARD_X_TILES = 15
GAMEBOARD_Y_TILES = 15

WW_player_last_score = 0
selected_tile_letter = '#' # = no tile selected

# Key:
# 0=Center star = double word
# 1=Normal tile
# 2=Double letter
# 3=Tripple letter
# 4=Tripple word
# 5=Double word


             # 0   1   2   3   4   5   6   7   8   9   0   1   2   3   4  
                # 0   1   2   3   4   5   6   7   8   9   0   1   2   3   4             
WW_GAMEBOARD = [['4','1','1','2','1','1','1','4','1','1','1','2','1','1','4'],
                ['1','5','1','1','1','3','1','1','1','3','1','1','1','5','1'],
                ['1','1','5','1','1','1','2','1','2','1','1','1','5','1','1'],
                ['2','1','1','5','1','1','1','2','1','1','1','5','1','1','2'],
                ['1','1','1','1','5','1','1','1','1','1','5','1','1','1','1'],
                ['1','3','1','1','1','3','1','1','1','3','1','1','1','3','1'],
                ['1','1','2','1','1','1','2','1','2','1','1','1','2','1','1'],
                ['4','1','1','2','1','1','1','0','1','1','1','2','1','1','4'],
                ['1','1','2','1','1','1','2','1','2','1','1','1','2','1','1'],
                ['1','3','1','1','1','3','1','1','1','3','1','1','1','3','1'],
                ['1','1','1','1','5','1','1','1','1','1','5','1','1','1','1'],
                ['2','1','1','5','1','1','1','2','1','1','1','5','1','1','2'],
                ['1','1','5','1','1','1','2','1','2','1','1','1','5','1','1'],
                ['1','5','1','1','1','3','1','1','1','3','1','1','1','5','1'],
                ['4','1','1','2','1','1','1','4','1','1','1','2','1','1','4']]

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

# Key
# # = empty
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
# hand: '#' = empty, or blank
# status: 'playing', 'notplaying', 'out'
# Support up to 4 players
# avatar_index points to the image of the chosen avatar
WW_player1 = {"player": "Player 1", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#'], "player name" : "empty1", "avatar index" : 0, "words":[]}
WW_player2 = {"player": "Player 2", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#'], "player name" : "empty2", "avatar index" : 0, "words":[]}
WW_player3 = {"player": "Player 3", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#'], "player name" : "empty3", "avatar index" : 0, "words":[]}
WW_player4 = {"player": "Player 4", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#'], "player name" : "empty4", "avatar index" : 0, "words":[]}
WW_AL      = {"player": "AL",       "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#'], "player name" : "AL",     "avatar index" : 0, "words":[]}

letter_value = {
                
                'A':1, 'B':3,  'C':3, 'D':2, 'E':1, 
                'F':4, 'G':2,  'H':4, 'I':1, 'J':8, 
                'K':5, 'L':1,  'M':3, 'N':1, 'O':1, 
                'P':3, 'Q':10, 'R':1, 'S':1, 'T':1, 
                'U':1, 'V':8,  'W':4, 'X':8, 'Y':4, 
                'Z':10,

                ' ':0,'#':0,

                'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 
                'f':0, 'g':0, 'h':0, 'i':0, 'j':0, 
                'k':0, 'l':0, 'm':0, 'n':0, 'o':0, 
                'p':0, 'q':0, 'r':0, 's':0, 't':0, 
                'u':0, 'v':0, 'w':0, 'x':0, 'y':0, 
                'z':0 } # ' ' = Player 1 blank, '#' = EMPTY, lowercase are for 0 value blank tiles

# Total of 101 tiles in a normal set, # = BLANK
WW_letter_key = {'A':9, 'B':2,  'C':2, 'D':4, 'E':12, 
                 'F':2, 'G':3,  'H':2, 'I':9, 'J':1, 
                 'K':1, 'L':4,  'M':2, 'N':6, 'O':8, 
                 'P':2, 'Q':1,  'R':6, 'S':4, 'T':6, 
                 'U':4, 'V':2,  'W':2, 'X':1, 'Y':2, 
                 'Z':1, ' ':2} # ' ' = BLANK TILE, '#' = EMPTY

# word_warrior bag of tiles
WW_bag = []

WW_active_player = "none"

#Test: Client_player
WW_Client_player = "none"

pickup = False
go_button_clicked = False

computer_player = False

#Track AL's progress from the server
AL_percent_complete = 0


#Version 4.0 changes
#Added chat

local_chat_box = []
you_got_mail = False 

pygame.init()

#define screen size +1 for room on the size for game data.
SCREEN_WIDTH  = (GAMEBOARD_X_TILES + 1 + 3) * TILES_WIDTH  
SCREEN_HEIGHT = ((GAMEBOARD_Y_TILES + 2) * TILES_HEIGHT) - 20

X_OFFSET = 40 * 3
Y_OFFSET = 0

HAND_PLAYER_GO_Y_OFFSET = 40 * 15 + 20

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

title_string = "Word Warrior " + REVISION + " - Boulder Creek Video Games "
pygame.display.set_caption(title_string)

#define colors
GREEN  = (0, 255, 0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
WHITE  = (255, 255, 255)
YELLOW = (255,255,0)
BLACK  = (0,0,0)
GRAY   = (200,200,200)

WW_font        = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 25)
WW_definition  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 15)
courier_bold   = pygame.font.match_font("Courier", bold = True)
WW_definition_bold = pygame.font.Font(courier_bold, 15)
WW_chat_font   = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 12)
WW_score_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 10)
WW_value_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 10)
WW_help_text_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 13)
WW_full_screen_text_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 13)
font = pygame.font.Font(None, 20)

blank_space    = pygame.image.load("assets/imgs/blank_space.png").convert_alpha()
double_letter  = pygame.image.load("assets/imgs/double_letter.png").convert_alpha()
double_word    = pygame.image.load("assets/imgs/double_word.png").convert_alpha()
tripple_letter = pygame.image.load("assets/imgs/tripple_letter.png").convert_alpha()
tripple_word   = pygame.image.load("assets/imgs/tripple_word.png").convert_alpha()
center_star    = pygame.image.load("assets/imgs/center_star.png").convert_alpha()
blank_tile1    = pygame.image.load("assets/imgs/blank_tile1.png").convert_alpha()
blank_tile2    = pygame.image.load("assets/imgs/blank_tile2.png").convert_alpha()
blank_tile3    = pygame.image.load("assets/imgs/blank_tile3.png").convert_alpha()
blank_tile4    = pygame.image.load("assets/imgs/blank_tile4.png").convert_alpha()
go_tile        = pygame.image.load("assets/imgs/go_tile.png").convert_alpha()
black_tile     = pygame.image.load("assets/imgs/black_tile.png").convert_alpha()
wait_tile      = pygame.image.load("assets/imgs/wait_tile.png").convert_alpha()
grey_tile      = pygame.image.load("assets/imgs/grey_tile.png").convert_alpha()
fixed_tile     = pygame.image.load("assets/imgs/fixed_tile.png").convert_alpha()
myturn_icon    = pygame.image.load("assets/imgs/myturn.png").convert_alpha()
dictonary_icon = pygame.image.load("assets/imgs/dictionary.png").convert_alpha()
red_tile       = pygame.image.load("assets/imgs/red_tile.png").convert_alpha()
help_screen1   = pygame.image.load("assets/imgs/help_screen1.png").convert_alpha() # Base help screen / rules
help_screen2   = pygame.image.load("assets/imgs/help_screen2.png").convert_alpha() # 2-letter words
help_screen3   = pygame.image.load("assets/imgs/help_screen3.png").convert_alpha() # Tile Values
chat_msg_box   = pygame.image.load("assets/imgs/chat_msg_box.png").convert_alpha()
new_chat_msg_box = pygame.image.load("assets/imgs/new_chat_msg_box.png").convert_alpha()

#Load the setup screen and resize if needed
setup_screen_lg = pygame.image.load("assets/imgs/setup_screen.png").convert_alpha()
setup_screen_width = setup_screen_lg.get_width()
setup_screen_height = setup_screen_lg.get_height()
if setup_screen_width > 640 or setup_screen_height > 640:
  setup_screen = pygame.transform.scale(setup_screen_lg,(640,640))
else:
  setup_screen = setup_screen_lg

#load avatars
avatar = []
avatar_load_count = 0

file_name = "assets/imgs/avatar_0.png"
while (os.path.exists(file_name)):
  avatar_img = pygame.image.load(file_name).convert_alpha() 
  original_width = avatar_img.get_width()
  original_height = avatar_img.get_height()
  if original_width > 80 or original_height > 80:
    resized_img = pygame.transform.scale(avatar_img,(80,80))
    avatar.append(resized_img)
  else:
    avatar.append(avatar_img)
  avatar_load_count += 1
  file_name = "assets/imgs/avatar_"+str(avatar_load_count)+".png"
print ("Loaded: ",avatar_load_count," avatars.")

al_avatar = []
al_avatar_load_count = 0

file_name = "assets/imgs/al_avatar_0.png"
while (os.path.exists(file_name)):
  al_avatar_img = pygame.image.load(file_name).convert_alpha() 
  original_width = al_avatar_img.get_width()
  original_height = al_avatar_img.get_height()
  if original_width > 80 or original_height > 80:
    al_resized_img = pygame.transform.scale(al_avatar_img,(80,80))
    al_avatar.append(al_resized_img)
  else:
    al_avatar.append(al_avatar_img)
  al_avatar_load_count += 1
  file_name = "assets/imgs/al_avatar_"+str(al_avatar_load_count)+".png"
print ("Loaded: ",al_avatar_load_count," avatars.")

#avatar_AL           = pygame.image.load("assets/imgs/avatar_1010.png").convert_alpha()
left_arrow          = pygame.image.load("assets/imgs/arrow_left.png").convert_alpha()
left_arrow.set_colorkey(WHITE)
right_arrow         = pygame.image.load("assets/imgs/arrow_right.png").convert_alpha()
right_arrow.set_colorkey(WHITE)
avatar_background   = pygame.image.load("assets/imgs/avatar_background.png").convert_alpha()
avatar_background2  = pygame.image.load("assets/imgs/avatar_background2.png").convert_alpha()
invite_al_button    = pygame.image.load("assets/imgs/invite_al_button.png").convert_alpha()
kick_al_button      = pygame.image.load("assets/imgs/kick_al_button.png").convert_alpha()

dictionary         = "assets/dictionary/Collins Scrabble Words (2019) with definitions.txt"
offical_word_file  = "assets/dictionary/offical_words_list.txt"

#   _____                        ______             _            
#  / ____|                      |  ____|           (_)           
# | |  __  __ _ _ __ ___   ___  | |__   _ __   __ _ _ _ __   ___ 
# | | |_ |/ _` | '_ ` _ \ / _ \ |  __| | '_ \ / _` | | '_ \ / _ \
# | |__| | (_| | | | | | |  __/ | |____| | | | (_| | | | | |  __/
#  \_____|\__,_|_| |_| |_|\___| |______|_| |_|\__, |_|_| |_|\___|
#                                              __/ |             
#                                             |___/              

def read_word_definition(file_path):
  word_definitions = {}
  with open(file_path, 'r') as file:
    next(file) #skip 1st line with file title
    next(file) #skip 2nd line with blank space
    for line in file:
        line = line.strip()
        if line:
          word, definition = line.split('\t', 1)
          word_definitions[word.strip()] = definition.strip()
  return word_definitions

def read_offical_english_words(file_path):
  offical_words = []
  with open(file_path, "r") as file:
    for word in file:
      offical_words.append(word.strip())
  return offical_words 

word_definitions    = read_word_definition(dictionary)
offical_words_list  = read_offical_english_words(offical_word_file)

def is_word(word):
  return(word.lower() in offical_words_list)

def test_dictionary_lookup():
  print("ROT is in dictionary? ", is_word ("rot"))
  print("The definition of ROT is: ", word_definitions["ROT"])
  print("SEX is in dictionary? ", is_word ("sex"))
  print("The definition of SEX is: ", word_definitions["SEX"])
  print("PONY is in dictionary? ", is_word ("pony"))
  print("The definition of PONY is: ", word_definitions["PONY"])
  print("CANTANKEROUSLY is in dictionary? ", is_word ("CANTANKEROUSLY"))
  print("The definition of CANTANKEROUSLY is: ", word_definitions["CANTANKEROUSLY"])
  print("deadbeef is in the dictionary?", is_word("deadbeef"))
  #print("The definition of deadbeef is: ", word_definitions["deadbeef"])

def roll_blank_tile(pos):
  global WW_GAMEBOARD_WORDS

  tile_x, tile_y = get_gameboard_tile_coordinate(pos)
  #print(tile_x,tile_y)

  if (tile_x == -1 and tile_y == -1):
    return

  #If it's still 'Blank' then roll to 'a'
  if (WW_GAMEBOARD_WORDS[tile_y][tile_x] == ' ' or WW_GAMEBOARD_WORDS[tile_y][tile_x] == 'z'):
    WW_GAMEBOARD_WORDS[tile_y][tile_x] = 'a'
  elif (WW_GAMEBOARD_WORDS[tile_y][tile_x].islower()):
    WW_GAMEBOARD_WORDS[tile_y][tile_x] = chr(ord(WW_GAMEBOARD_WORDS[tile_y][tile_x])+1)

def get_gameboard_tile_coordinate(pos):
  #Calculate the x,y coordinate based on mouse position
  mouse_x = pos[0]
  mouse_y = pos[1]

  if (mouse_x >= 0+X_OFFSET and mouse_x <= (15*40)+X_OFFSET and mouse_y >= 0+Y_OFFSET and mouse_y <=(15*40)+Y_OFFSET):
    tile_x = math.floor((mouse_x-X_OFFSET)/40)
    tile_y = math.floor((mouse_y-Y_OFFSET)/40)

    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if (tile_x > 14):
      tile_x = 14
    if (tile_y > 14):
      tile_y = 14
    return(tile_x,tile_y)
  else:
    return(-1,-1)

def player_has_not_put_tile_on_the_gameboard():
  for x in range (0,15):
    for y in range (0,15):
      if (WW_DIRTY_GAMEBOARD[y][x] == '1'):
        return (False)
  return (True)

def toggle_hand_tile_for_exchange(pos):
  global WW_GAMEBOARD_WORDS

  #print("hand_position: ",hand_position," hand: ",hand)
  #If it's still 'Blank' then roll to 'a'
  if (player_has_not_put_tile_on_the_gameboard()):

    hand_position = get_hand_tile_coordinate(pos)
    if (hand_position == -1):
      return

    hand = get_my_hand()

    if (hand[hand_position].islower()):
      hand[hand_position] = hand[hand_position].upper()
    else:
      hand[hand_position] = hand[hand_position].lower()
  
    set_my_hand (hand)

def get_hand_tile_coordinate(pos):
  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET

  mouse_x = pos[0]
  mouse_y = pos[1]
 
  #If tile is picked up from players hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    hand_position = math.floor((mouse_x-X_OFFSET)/40)
 
    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if hand_position > 6:
      hand_position = 6
    
    return (hand_position)
  else:
    return(-1)

def get_WE_word(tile_x,tile_y):
  #If the user clicked on a blank space no word data
  if (WW_GAMEBOARD_WORDS[tile_y][tile_x] == '#'):
    return False, ""

  word = ""
  #print("get_WE_word (x,y): ",tile_x,tile_y)

  y = tile_y
  for x in range (tile_x,-1,-1):
    if (WW_GAMEBOARD_WORDS[y][x] != "#"):
      #print("WE: range(tile_x,-1,-1): ",x,WW_GAMEBOARD_WORDS[y][x])
      west_index = x
    else:
      break
  for x in range (tile_x,15):
    if(WW_GAMEBOARD_WORDS[y][x] != "#"):
      #print("WE: range(tile_x,15): ",x,WW_GAMEBOARD_WORDS[y][x])
      east_index = x
    else:
      break

  if (east_index - west_index >= 1):
    #print("found word length:",east_index-west_index+1)
    for x in range (west_index, east_index+1):
      word += WW_GAMEBOARD_WORDS[y][x].upper()
    #print("True: ", word)
    return True, word
  else:
    #print(False,"no word")
    return False, ""

def get_NS_word(tile_x,tile_y):
  #If the user clicked on a blank space no word data
  if (WW_GAMEBOARD_WORDS[tile_y][tile_x] == '#'):
    return False, ""

  word = ""
  x = tile_x
  for y in range (tile_y,-1,-1):
    if (WW_GAMEBOARD_WORDS[y][x] != "#"):
      north_index = y
    else:
      break
  for y in range (tile_y,15):
    if(WW_GAMEBOARD_WORDS[y][x] != "#"):
      south_index = y
    else:
      break

  if (south_index - north_index >= 1):
    for y in range (north_index, south_index+1):
      word += WW_GAMEBOARD_WORDS[y][x].upper()
    return True, word
  else:
    return False, ""

def pop_up_definition(pos):
  tile_x, tile_y = get_gameboard_tile_coordinate(pos)
  if (tile_x == -1 and tile_y == -1):
    return

  #print(get_WE_word(tile_x,tile_y))

  #we_word_found = True 
  #we_word = "PONY"
  #ns_word_found = True 
  #ns_word = "HORSE"

  we_word_found, we_word = get_WE_word(tile_x,tile_y)
  ns_word_found, ns_word = get_NS_word(tile_x,tile_y)

  #print("we and ns words found: we: ",we_word_found,we_word,"ns: ", ns_word_found,ns_word)

  text1 = "No horizontal word"
  text2 = "No vertical word"
  if (we_word_found):
    if (is_word(we_word)):
      text1 = "Definition: ("+we_word+"): "+word_definitions[we_word.upper()]
  if (ns_word_found):
    if (is_word(ns_word)):
      text2 = "Definition: ("+ns_word+"): "+word_definitions[ns_word.upper()]    

  # Create a surface for the popup
  popup_width = 600
  popup_height = 500
  # Center the popup on the screen
  x = (SCREEN_WIDTH - popup_width) // 2
  y = (SCREEN_HEIGHT - popup_height) // 2

  popup_surface = pygame.Surface((popup_width, popup_height))
  popup_surface.fill(GRAY)
  pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

  #fnt = font.render("test", True, BLACK)
  #popup_surface.blit (fnt, (0,0))

  txtX = 50
  txtY = 1
  wraplen = 70
  count = 0
  my_wrap = textwrap.TextWrapper(width=wraplen)
  wrap_list1 = my_wrap.wrap(text=text1)
  wrap_list2 = my_wrap.wrap(text=text2)

  #print(wrap_list)
  # Draw one line at a time further down the screen
  for i in wrap_list1:
    txtY = txtY + 30
    Mtxt = WW_definition.render(f"{i}", True, BLACK)
    popup_surface.blit(Mtxt, (txtX, txtY))
    count += 1

  txtY += 20 # add gap between definitions

  # Draw one line at a time further down the screen
  for i in wrap_list2:
    txtY = txtY + 30
    Mtxt = WW_definition.render(f"{i}", True, BLACK)
    popup_surface.blit(Mtxt, (txtX, txtY))
    count += 1

  screen.blit(popup_surface, (x, y))
  pygame.display.flip()
  
def draw_text (screen,x,y,text,size,color):
  font = pygame.font.Font(None, size)
  
  font_img = font.render(text, True, color)
  screen.blit(font_img, (x,y))
  return(font.size(text)) #returns the text_width, text_height of the font size calle dout

def draw_text_on_mask (mask, screen,x,y,text,size,color):
  #todo make this work
  font = pygame.font.Font(None, size)
  
  font_img = font.render(text, True, color)
  screen.blit(font_img, (x,y))
  return(font.size(text)) #returns the text_width, text_height of the font size calle dout

def draw_text_center (screen,x,y,text,size,color):
  font = pygame.font.Font(None, size)
  
  font_img = font.render(text, True, color)
  width = font_img.get_width()

  screen.blit(font_img, (x-(width/2),y))
  return(font.size(text)) #returns the text_width, text_height of the font size calle dout

cursor_timer = time.time()
cursor_on = True
CURSOR_FLASH_RATE = .5 #sec's

def cursor(ch):
  global cursor_timer, cursor_on
  if (time.time() > cursor_timer + CURSOR_FLASH_RATE):
    cursor_timer = time.time()
    if cursor_on == True:
      cursor_on = False
    else:
      cursor_on = True 

  if (cursor_on == True):
    return(ch)
  else:
    return('  ')

toggle_timer = time.time()
toggle_on = True

#toggle on and off at rate [seconds]
def toggle(rate):
  TOGGLE_FLASH_RATE = rate

  global toggle_timer, toggle_on

  if (time.time() > toggle_timer + TOGGLE_FLASH_RATE):
    toggle_timer = time.time()
    if toggle_on == True:
      toggle_on = False
    else:
      toggle_on = True 

  return (toggle_on)

# Text entry modes

def click_area(pos,x1,y1,x2,y2):
  mouse_x = pos[0]
  mouse_y = pos[1]

  if mouse_x >= x1 and mouse_x <=x2 and mouse_y >=y1 and mouse_y <= y2:
    return True 
  else:
    return False

GET_IP_ADDRESS   = 0
GET_NAME         = 1
SET_AVATAR       = 2
GET_PORT_ADDRESS = 3
GET_AL_FAIRNESS  = 4

player_avatar_index = 0
al_avatar_index     = 0

player_name = "Your_name_here"

def start_screen_get_server_ip_address():
  global addr, port, computer_player, player_avatar_index, player_name, al_avatar_index

  clock = pygame.time.Clock()
  input_box = pygame.Rect(39, 220, 400, 32)
  color = pygame.Color(BLACK)
  active = True
  text_ip = game_server_address
  text_port = "5000"
  pygame.event.clear()
  
  #get top left x and y
  x = (SCREEN_WIDTH/2)  - (setup_screen.get_width()/2) 
  y = (SCREEN_HEIGHT/2) - (setup_screen.get_height()/2)

  mode = GET_IP_ADDRESS 

  page = 1

  # Render splash screen
  #img = splash_screen
  #screen.blit(img, (x,y))
  #pygame.display.flip()
  #pygame.time.wait(300)

  while True:
    # Render the background image
    img = setup_screen
    screen.blit(img, (x,y))
    
    #img = text_mask
    #img.set_colorkey(WHITE)
    #screen.blit(img, (x,y))

    text_x = (SCREEN_WIDTH/2) - 150
    text_y = 190 + 52
    font_size = 20

    if mode == GET_IP_ADDRESS:
      ip_text_width, ip_text_height     = draw_text_center(screen,text_x,y+text_y,"Gameserver Address: "+text_ip+cursor("_"),font_size,BLUE)
    else:
      ip_text_width, ip_text_height     = draw_text_center(screen,text_x,y+text_y,"Gameserver Address: "+text_ip,font_size,BLACK)

    text_y += ip_text_height + 8

    if mode == GET_PORT_ADDRESS:
      port_text_width, port_text_height = draw_text_center(screen,text_x,y+text_y,"Enter Gameserver port: "+text_port+cursor("_"),font_size,BLUE)
    else:
      port_text_width, port_text_height = draw_text_center(screen,text_x,y+text_y,"Enter Gameserver port: "+text_port,font_size,BLACK)
    
    text_y += port_text_height + 8
    
    if mode == GET_NAME:
      name_text_width, name_text_height = draw_text_center(screen,text_x,y+text_y,"Enter Name: "+player_name+cursor("_"),font_size,BLUE)
    else:
      name_text_width, name_text_height = draw_text_center(screen,text_x,y+text_y,"Enter Name: "+player_name,font_size,BLACK)

    left_arrow_img = left_arrow
    right_arrow_img = right_arrow
    avatar_img = avatar[player_avatar_index]

    avatar_x = 295 - 150
    avatar_y = text_y + name_text_height + 38

    if mode == SET_AVATAR:
      avatar_text_width, avatar_text_height = draw_text_center(screen,text_x,avatar_y-20,"Choose Avatar",font_size,BLUE)
    else:
      avatar_text_width, avatar_text_height = draw_text_center(screen,text_x,avatar_y-20,"Choose Avatar",font_size,BLACK)

    avatar_img.set_colorkey(WHITE)
    screen.blit(left_arrow_img,  (avatar_x,avatar_y+25))
    screen.blit(avatar_img,      (avatar_x+30+20,avatar_y))
    screen.blit(right_arrow_img, (avatar_x+30+20+80+10,avatar_y+25))

    #Draw AL avatar selector
    left_arrow_img = left_arrow
    right_arrow_img = right_arrow
    al_avatar_img = al_avatar[al_avatar_index]

    #avatar_x = 295
    avatar_y += 120 - 10

    al_level_text = ["EASY","MEDIUM","HARD","NO MERCY"]

    if mode == GET_AL_FAIRNESS:
      avatar_text_width, avatar_text_height = draw_text_center(screen,text_x,avatar_y-20,"Choose AL Level: "+al_level_text[al_avatar_index],font_size,BLUE)
    else:
      avatar_text_width, avatar_text_height = draw_text_center(screen,text_x,avatar_y-20,"Choose Al Level: "+al_level_text[al_avatar_index],font_size,BLACK)

    al_avatar_img.set_colorkey(WHITE)
    screen.blit(left_arrow_img, (avatar_x,avatar_y+25))
    screen.blit(al_avatar_img, (avatar_x+30+20,avatar_y))
    screen.blit(right_arrow_img, (avatar_x+30+20+80+10,avatar_y+25))

    text_y = avatar_y+130
    font_size = 16
    text_x += 90

    if (cursor('#') == '#'):
      draw_text_center(screen,text_x,text_y,"USE 'TAB' TO SELECT OPTION TO EDIT",font_size,BLACK)
      text_y += 20
      draw_text_center(screen,text_x,text_y,"PRESS 'RETURN' TO START GAME",font_size,YELLOW)
    else:
      draw_text_center(screen,text_x,text_y,"USE 'TAB' TO SELECT OPTION TO EDIT",font_size,RED)
      text_y += 20
      draw_text_center(screen,text_x,text_y,"PRESS 'RETURN' TO START GAME",font_size,BLUE)


    pygame.display.flip()

    for event in pygame.event.get(): #event = pygame.event.wait()
      if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()

      if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        #print(pos)
        if click_area(pos,117,253,369,264):
          mode = GET_IP_ADDRESS
        elif (click_area(pos,106,273,360,283)):
          mode = GET_PORT_ADDRESS
        elif (click_area(pos,114,297,369,306)):
          mode = GET_NAME
        elif (click_area(pos,145,367,185,396)):
          mode = SET_AVATAR
          if player_avatar_index > 0:
            player_avatar_index -= 1
        elif (click_area(pos,285,366,322,396)):
          mode = SET_AVATAR
          if player_avatar_index < avatar_load_count-1:
            player_avatar_index += 1
        elif (click_area(pos,144,477,183,506)):
          mode = GET_AL_FAIRNESS
          if al_avatar_index > 0:
            al_avatar_index -= 1
        elif (click_area(pos,284,477,322,506)):
          mode = GET_AL_FAIRNESS
          if al_avatar_index < al_avatar_load_count-1:
            al_avatar_index += 1

      if event.type == pygame.KEYDOWN:
        if active:
          if event.key == pygame.K_TAB:  # Detect tab to move to editing the name
            if mode == GET_IP_ADDRESS:
              mode = GET_PORT_ADDRESS
            elif mode == GET_PORT_ADDRESS:
              mode = GET_NAME
            elif mode == GET_NAME:
              mode = SET_AVATAR
            elif mode == SET_AVATAR:
              mode = GET_AL_FAIRNESS
            elif mode == GET_AL_FAIRNESS:
              mode = GET_IP_ADDRESS
          elif event.key == pygame.K_RETURN:
            print("Server hostname: ",text_ip)
            
            player_name = player_name.replace(" ","_") # replace the spaces with underscores

            print("Player name: ",player_name)
            print("Player avatar: ",player_avatar_index)
            print("AL avatar: ",al_avatar_index)
            #WW_Set_AL_Fairness()
            print("Server port: ", text_port)
            addr = socket.gethostbyname(text_ip)
            port = int(text_port)
            print("IP address: ", addr)
            return
          elif event.key == pygame.K_F2:
            print("Starting client side Al")
            print("Server hostname: ",text_ip)
            addr = socket.gethostbyname(text_ip)
            print("IP address: ", addr)
            computer_player = True
            return
          elif event.key == pygame.K_LEFT and mode == SET_AVATAR:
            if player_avatar_index > 0:
              player_avatar_index -= 1
              #print(player_avatar_index)
          elif event.key == pygame.K_LEFT and mode == GET_AL_FAIRNESS:
            if al_avatar_index >0:
              al_avatar_index -= 1
              #print(player_avatar_index)
          elif event.key == pygame.K_RIGHT and mode == SET_AVATAR:
            if player_avatar_index < avatar_load_count-1:
              player_avatar_index += 1
              #print(player_avatar_index)
          elif event.key == pygame.K_RIGHT and mode == GET_AL_FAIRNESS:
            if al_avatar_index < al_avatar_load_count-1:
              al_avatar_index += 1
              #print(al_avatar_index)
          elif event.key == pygame.K_BACKSPACE:
            if mode == GET_IP_ADDRESS:
              text_ip = text_ip[:-1]
            elif mode == GET_NAME:
              player_name = player_name[:-1]
            elif mode == GET_PORT_ADDRESS:
              text_port = text_port[:-1]
          else:
            if mode == GET_IP_ADDRESS:
              text_ip += event.unicode
            elif mode == GET_NAME:
              if len(player_name) <= 11:
                player_name += event.unicode
            elif mode == GET_PORT_ADDRESS:
              text_port += event.unicode
              
      clock.tick(30)

def dictionary_button_check():
  pos = pygame.mouse.get_pos()
  mouse_x = pos[0]
  mouse_y = pos[1]
  
  #Check that the user clicked on the button and also make sure it's their turn
  if (mouse_x >= X_OFFSET+(15*40) and mouse_y >= Y_OFFSET+(14*40) and mouse_y < Y_OFFSET+(15*40)):
    pygame.event.get()
    while(pygame.mouse.get_pressed()[0]):
      check_spelling()
      pygame.event.get()
  
def check_spelling():
  words_spelled_correctly = True

  list_of_words = find_new_words()

  if (list_of_words == 0):
    print("No words found to check spelling on")
    return
  
  #print(list_of_words)

  for i in range(len(WW_GAMEBOARD_WORDS)):
    for j in range(len(WW_GAMEBOARD_WORDS[i])):
      tile = WW_GAMEBOARD_WORDS[i][j]  

      if (tile != '#'):
        if (WW_Client_player == "Player 1"):
          img = blank_tile1
        elif (WW_Client_player == "Player 2"):
          img = blank_tile2
        elif (WW_Client_player == "Player 3"):
          img = blank_tile3
        elif (WW_Client_player == "Player 4"):
          img = blank_tile4

        #if the tile is fixed draw it with tan background
        if(WW_DIRTY_GAMEBOARD[i][j] == '0'):
          img = fixed_tile

        screen.blit(img,(X_OFFSET + (j*40),Y_OFFSET + (i*40)))

        good_tile = good_letter(list_of_words,j,i)

        #Don't render blank tile text
        if (tile != ' '):
          if (good_tile):
            font_img = WW_font.render(tile, True, BLACK)
          else:
            font_img = WW_font.render(tile, True, RED)
            words_spelled_correctly = False
          
          if (tile.islower()):
            screen.blit(font_img,(X_OFFSET +(j*40)+13,Y_OFFSET+(i*40)+ 0))
          else:
            screen.blit(font_img,(X_OFFSET+(j*40)+10,Y_OFFSET+(i*40)+ 0))


        if(good_tile):
          font_value_img = WW_value_font.render(str(letter_value[tile]), True, BLACK)
        else:
          font_value_img = WW_value_font.render(str(letter_value[tile]), True, RED)
        screen.blit(font_value_img,(X_OFFSET+(j*40)+25,Y_OFFSET+(i*40)+ 25))

        pygame.display.flip()
  return(words_spelled_correctly)

def good_letter(words, x, y):
  # x = x coordinate of the tile being painted to the screen.
  # y = y coordinate of the tile being painted to the screen.
  #  
  # words[i][0] = west/north index 
  # words[i][1] = east/south index
  # words[i][2] = Y offset (West East Word)
  # words[i][3] = X offset (North south word)
  # words[i][4] = 0 = non word, 1= WE word, 2 = NS word
  # words[i][5] = "" for blank and the word when defined 
  # words[i][6] = 1 goodly spelt word, 2 = badly spelt word

  #print("Start of good_letter")
  #print(words)

  found_good_word = True

  for i in range (0,8):
    #Check WE words
    #print ("good_letter: ", i)
    if (words[i][4] == 1):
      west_index = words[i][0]
      east_index = words[i][1]
      WW_y_offset = words[i][2]
      #print(west_index,east_index,y_offset)
      if (x <= east_index and x >= west_index and y == WW_y_offset and words[i][6] == 2):
        found_good_word = False
        #print ("WE word x:",x,"y:",y,":",WW_GAMEBOARD_WORDS[y][x],"G/B: ", found_good_word)

    #Check NS
    if (words[i][4] == 2):
      north_index = words[i][0]
      south_index = words[i][1]
      WW_x_offset = words[i][3]
      if (y <=south_index and y >= north_index and x == WW_x_offset and words[i][6] == 2):
        found_good_word = False
        #print ("NS word x:",x,"y:",y,":",WW_GAMEBOARD_WORDS[y][x],"G/B: ", found_good_word)

  #print("End of good letter")
  return(found_good_word)

def find_new_words():
  x = 0
  y = 0

  # words[i][0] = west/north index 
  # words[i][1] = east/south index
  # words[i][2] = Y offset (West East Word)
  # words[i][3] = X offset (North south word)
  # words[i][4] = 0 = non word, 1= WE word, 2 = NS word
  # words[i][5] = "" for blank and the word when defined 
  # words[i][6] = 1 goodly spelt word, 2 = badly spelt word

  words = [[0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0],
           [0, 0, 0, 0, 0, "",0]]

  word_count = 0

  # Find new tiles
  # Tile character, x-pos, y-pos
  new_tiles = [['#', 0, 0],
               ['#', 0, 0],
               ['#', 0, 0],
               ['#', 0, 0],
               ['#', 0, 0],
               ['#', 0, 0],
               ['#', 0, 0]]

  #find new tiles played and store them and their position in new_tiles
  number_of_new_tiles = 0
  for x in range (0,15):
    for y in range (0,15):
      if (WW_DIRTY_GAMEBOARD[y][x] == '1'):
        new_tiles [number_of_new_tiles][0] = WW_GAMEBOARD_WORDS[y][x]
        new_tiles [number_of_new_tiles][1] = x 
        new_tiles [number_of_new_tiles][2] = y

        number_of_new_tiles += 1 

        #print("%%%%%% add tile x: ",x,"y: ",y," :",WW_GAMEBOARD_WORDS[y][x])

  #print(new_tiles)
  if (number_of_new_tiles == 0):
    print("No new words to check")
    return 0

  #Check each new tile found for WE word.  Add it if not aready found
  for i in range(0,7):
    if (new_tiles[i][0] != '#'):

      x = new_tiles[i][1]
      y = new_tiles[i][2]

      west_index = x
      for j in range (x,-1,-1):
        if (WW_GAMEBOARD_WORDS[y][j] != '#'):
          west_index = j
        else:
          break

      east_index = x
      for j in range(x,15):
        if (WW_GAMEBOARD_WORDS[y][j] != '#'):
          east_index = j
        else:
          break

      if east_index - west_index >= 1:
        word_found = False
        #Check if word has already been added (indexed)
        for j in range (0,8):
          if (words[j][0] == west_index and words[j][1] == east_index and words[j][2] == y and words[j][3] == 0 and words[j][4] == 1):
            word_found = True      

        if word_found == False:
          #store new WE word if found
          if (word_count >= 8):
            print("Illeagal number of new words.")
            return
        
          #print("adding new WE word: ", word_count)
          words[word_count][0] = west_index
          words[word_count][1] = east_index
          words[word_count][2] = y
          words[word_count][3] = 0
          words[word_count][4] = 1 # valid WE word
          word_count += 1

  #Check each new tile found for NS word.  Add it if not aready found
  for i in range(0,7):
    if (new_tiles[i][0] != '#'):
      x = new_tiles[i][1]
      y = new_tiles[i][2]
      north_index = y
      for j in range (y,-1,-1):
        if (WW_GAMEBOARD_WORDS[j][x] != '#'):
          #print("NS range(j=",j,",-1,-1): ", WW_GAMEBOARD_WORDS[j][x])
          north_index = j
        else:
          break

      south_index = y
      for j in range(y,15):
        if (WW_GAMEBOARD_WORDS[j][x] != '#'):
          #print("NS range(j=",j,",15): ", WW_GAMEBOARD_WORDS[j][x])
          south_index = j
        else:
          break

      if south_index - north_index >= 1:
        word_found = False
        #Check if word has already been added (indexed)
        for j in range (0,8):
          if (words[j][0] == north_index and words[j][1] == south_index and words[j][2] == 0 and words[j][3] == x and words[j][4] == 2):
            word_found = True      

        if word_found == False:
          if (word_count >= 8):
            print("Illeagal number of new words.")
            return

          words[word_count][0] = north_index
          words[word_count][1] = south_index
          words[word_count][2] = 0
          words[word_count][3] = x
          words[word_count][4] = 2 # valid NS word
          word_count += 1
  
  #print(new_tiles)
  #print(words) 
  
  #Build the words
  for i in range (0,8):
    #print(words[i])
    #print("west index: ", words[i][0]," east index: ",words[i][1]," y offset: ", words[i][2])
    test_word = ""
  
    # Is it WE for valid WE word words[i][4] == 1
    if (words[i][4] == 1):
      y = words[i][2]
      west_index = words[i][0]
      east_index = words[i][1]
      for x in range (west_index,east_index+1):
        test_word += WW_GAMEBOARD_WORDS[y][x]
  
      words[i][5] = test_word

      #print ("WE looking up test_word: ", test_word)
      if (is_word(test_word)):
        words[i][6] = 1 # Goodly spelt word
      else:
        words[i][6] = 2 # Badly word

    # Is it NS for valid NS word words[i][4] == 1
    if (words[i][4] == 2):
      x = words[i][3]
      north_index = words[i][0]
      south_index = words[i][1]
      for y in range (north_index,south_index+1):
        test_word += WW_GAMEBOARD_WORDS[y][x]

      words[i][5] = test_word
      
      #print ("NS looking up test_word: ", test_word)
      if (is_word(test_word)):
        words[i][6] = 1 # Goodly spelt word
      else:
        words[i][6] = 2 # Badly spelt word

  #print("WE words")
  #print(words)
  #time.sleep(1)
  return (words)

def tiles_played():
  tile_count = 0
  for x in range(0,15):
    for y in range(0,15):
      if WW_DIRTY_GAMEBOARD[y][x] == '1':
        tile_count += 1
  return tile_count

#fixed 17-feb-2025 (rev 5.1) Fixed lower boundry of +1 neighbor check
def tile_has_neighbor(x,y):
  found_neighbor = False
  if WW_DIRTY_GAMEBOARD[y][x] == '1':
    if x>0:
      if WW_DIRTY_GAMEBOARD[y][x-1] != '#':
        found_neighbor = True 
    if x<14:
      if WW_DIRTY_GAMEBOARD[y][x+1] != '#':
        found_neighbor = True 
    if y>0:
      if WW_DIRTY_GAMEBOARD[y-1][x] != '#':
        found_neighbor = True 
    if y<14:
      if WW_DIRTY_GAMEBOARD[y+1][x] != '#':
        found_neighbor = True
  return found_neighbor

def new_tiles_connected():
  new_tiles = []
  
  #Find first tile NS and WE
  for x in range (0,15):
    for y in range (0,15):
      if (WW_DIRTY_GAMEBOARD[y][x] == '1'):
        new_tiles.append((x,y))  # x,y coordinate of the new tile, 0 = not connected, 1 = connected
        last_x = x 
        last_y = y

  #if verbose:
  #  print(new_tiles)

  #No new tiles found
  if len (new_tiles) == 0:
    return False 

  #One new tile found
  if len (new_tiles) == 1:
    x = new_tiles[0][0]
    y = new_tiles[0][1]
    if (tile_has_neighbor(x,y) == True):
      return True
    else:
      return False

  #More than one tile found
  x1 = new_tiles[0][0]
  y1 = new_tiles[0][1]
  x2 = new_tiles[1][0]
  y2 = new_tiles[1][1]

  #print("x1,y1,x2,y2: ",x1,y1,x2,y2)
  #check for co-linearity
  vertical_word_found   = True
  horizontal_word_found = True

  for tile in new_tiles:
    if tile[0] != x1:
      vertical_word_found = False #tiles no vertically co-linear
    if tile[1] != y1:
      horizontal_word_found = False #tile are not horizontally co-linear

  #If words are not co-linear in any direction then don't alow Go.
  if (vertical_word_found == False and horizontal_word_found == False):
    return False 

  if (vertical_word_found == True):
    #check for continguous word in the vertical direction
    for y in range (y1,last_y+1):
      if WW_DIRTY_GAMEBOARD[y][x1] == '#':
        return False # found gap

  else:
    #check for continguous word in the horizontal direction
    for x in range (x1,last_x+1):
      if WW_DIRTY_GAMEBOARD[y1][x] == '#':
        return False # found gap

  # All checks good return True and allow word to be accepted for continguous placement
  return True

def go_button_click(pos):
  global go_button_clicked

  mouse_x = pos[0]
  mouse_y = pos[1]

  # Check if the player is trying to exchanged tiles
  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False):
    if (tiles_played() == 0):
      hand = get_my_hand()
      for i in range (0,7):
        if hand[i].islower():
          return True

  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False):
    if (tiles_played() == 0):
      str1 = "No Tiles Played: Press 'ENTER' to forfeit."
      str2 = "Pres 'SPACE' to go back"
      if (generic_popup_box(X_OFFSET+(7*40),Y_OFFSET+(15*40),(10*40),60,str1,str2)):
        return True
  
  #If there is a poorly spelled word then highlight like the spell check button, and do not allow the player to continue
  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False and not check_spelling()):
    pygame.event.get()

    #If the user presses shift and go it will accept the word even if it's not in the dictionary
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
      return True

    while(pygame.mouse.get_pressed()[0]):
      check_spelling()
      pygame.event.get()
    return(False)

  #If multiple words are played (accidentally...) then don't allow the Go button
  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False):
    if check_spelling() == True:
      if not new_tiles_connected():
        return (False)

  #Check that the user clicked on the button and also make sure it's their turn
  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False):
    if check_spelling():
      go_button_clicked = True
      return (True)

  return False

def chat_button_pressed(pos):
  if (selected_tile_letter == '#'):
    return(click_area(pos,20,Y_OFFSET+(15*40)+20,20+80,Y_OFFSET+(15*40)+20+40))
  else:
    return(False)

def count_new_tiles_played(db):
  #Count how many new tiles placed on the board
  count = 0
  for x in range (0,15):
    for y in range (0,15):
      if (db[y][x] == '1'):
        count +=1
  return (count)

def all_tiles_played(db):
  #If there are 7 then the player used all their tiles
  if (count_new_tiles_played(db) == 7):
    return (True)
  else:
    return (False)

def drawbackground(screen):
  for i in range(len(WW_GAMEBOARD)):
    for j in range(len(WW_GAMEBOARD[i])):
      tile = WW_GAMEBOARD[i][j]

      # Key:
      # 0=Center star (double word)
      # 1=Blank
      # 2=Double letter
      # 3=Tripple letter
      # 4=Tripple word
      # 5=Double word

      # Pick the correct tiles to blit to the screen based on the LEVEL map
      if(tile == '4'):
        img = tripple_word
      elif (tile == '5'):
        img = double_word
      elif (tile == '1'):
        img = blank_space
      elif (tile == '2'):
        img = double_letter 
      elif (tile == '3'):
        img = tripple_letter
      elif (tile == '0'):
        img = center_star

      screen.blit(img,(X_OFFSET+(j*40),Y_OFFSET+(i*40)))

      #Draw myturn icon
      if (myturn()):
        img = myturn_icon
        screen.blit(img,(X_OFFSET+(7*40),Y_OFFSET+(15*40)))

      #Draw help screen text
      help_text_surface = WW_help_text_font.render("PRESS F1 FOR HELP", True, WHITE)
      screen.blit(help_text_surface, (X_OFFSET+(10*40),Y_OFFSET+(15*40)))   

      #Draw 'q'uit and F11 full screen text
      help_text_surface = WW_full_screen_text_font.render("PRESS 'END' TO QUIT, F11 = FULL SCREEN", True, WHITE)
      screen.blit(help_text_surface, (X_OFFSET+3,Y_OFFSET+(15*40)))

      #Draw chat button
      if you_got_mail == True:
        img = new_chat_msg_box
      else:
        img = chat_msg_box
      
      img.set_colorkey(WHITE)
      screen.blit(img,(20,Y_OFFSET+(15*40)+20))

def gameboard_update(screen):
  for i in range(len(WW_GAMEBOARD_WORDS)):
    for j in range(len(WW_GAMEBOARD_WORDS[i])):
      tile = WW_GAMEBOARD_WORDS[i][j]  

      if (tile != '#'):
        if (WW_Client_player == "Player 1"):
          img = blank_tile1
        elif (WW_Client_player == "Player 2"):
          img = blank_tile2
        elif (WW_Client_player == "Player 3"):
          img = blank_tile3
        elif (WW_Client_player == "Player 4"):
          img = blank_tile4

        #if the tile is fixed draw it with tan background
        if(WW_DIRTY_GAMEBOARD[i][j] == '0'):
          img = fixed_tile

        screen.blit(img,(X_OFFSET+(j*40),Y_OFFSET+(i*40)))

        #Don't render blank tile text
        if (tile != ' '):
          font_img = WW_font.render(tile, True, BLACK)
          if (tile.islower()):
            screen.blit(font_img,(X_OFFSET+(j*40)+13,Y_OFFSET+(i*40)+0))
          else:
            screen.blit(font_img,(X_OFFSET+(j*40)+10,Y_OFFSET+(i*40)+0))

        font_value_img = WW_value_font.render(str(letter_value[tile]), True, BLACK)
        screen.blit(font_value_img,(X_OFFSET+(j*40)+25,Y_OFFSET+(i*40)+25))

def player_hand_empty(hand):
  for i in range(0,7):
    if hand[i] != '#':
      return (False)
  else:
    return(True)

def value_player_hand(hand):
  value = 0
  for i in range(0,7):
    if (hand[i] != '#'):
      value += letter_value[hand[i]]
  return (value)

def WW_get_player_data():
  if (WW_Client_player == "Player 1"):
    return (WW_player1)
  elif (WW_Client_player == "Player 2"):
    return (WW_player2)
  elif (WW_Client_player == "Player 3"):
    return (WW_player3)
  elif (WW_Client_player == "Player 4"):
    return (WW_player4)
  else:
    print("Error: WW_Client_player not defined.")
    exit()

def hand_mouse_drag_update(screen):

  global selected_tile_letter

  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET

  hand = WW_get_player_data()["hand"]

  #Draw each tile on the player hand
  for tile in hand:
    #Draw the tile only if it is a valid tile (A-Z or Blank)
    if (tile == '#'):  
      #Draw black-unpopulated tile
      img = black_tile
      screen.blit(img,(x,y))
    else:
      #Draw blank tile if actually a blank tile
      if (WW_Client_player == "Player 1"):
        img = blank_tile1
      elif (WW_Client_player == "Player 2"):
        img = blank_tile2
      elif (WW_Client_player == "Player 3"):
        img = blank_tile3
      elif (WW_Client_player == "Player 4"):
        img = blank_tile4

      #if the tile is going to be thrown back in the bag paint the background red
      if (tile.islower()):
        img = red_tile

      screen.blit(img,(x,y))


    #Draw tile letter and value if not a blank tile
    if (tile != ' '):
      font_img = WW_font.render(tile.upper(), True, BLACK)
      screen.blit(font_img,(x+10,y))

    #draw tile letter value
    font_value_img = WW_value_font.render(str(letter_value[tile]), True, BLACK)
    screen.blit(font_value_img,(x+25,y+25))

    #advance to the next available hand tile spot
    x = x + 40
    
    # if there is a selected tile then draw it at the mouse positon (drag)
    #
    # Update dragged tile with mouse
    #
    #
    if (selected_tile_letter != '#'):
      # get the mos positon and use that to draw the tile
      mouse_position = pygame.mouse.get_pos()
      mouse_x = mouse_position[0] - 20
      mouse_y = mouse_position[1] - 20
      
      if (WW_Client_player == "Player 1"):
        img = blank_tile1
      elif (WW_Client_player == "Player 2"):
        img = blank_tile2
      elif (WW_Client_player == "Player 3"):
        img = blank_tile3
      elif (WW_Client_player == "Player 4"):
        img = blank_tile4
      screen.blit(img,(mouse_x,mouse_y))

      # Don't draw the tile text if the tile is a blank
      if (selected_tile_letter != ' '):
        font_img = WW_font.render(selected_tile_letter, True, BLACK)
        screen.blit(font_img,(mouse_x+10,mouse_y))

      font_value_img = WW_value_font.render(str(letter_value[selected_tile_letter]), True, BLACK)
      screen.blit(font_value_img,(mouse_x+25,mouse_y+25))

def tile_pile_update(screen):
  number_of_tiles = len(WW_bag)
  if (number_of_tiles == 0):
    return

  x = X_OFFSET + 15*40
  img = blank_tile1 

  for y in range(1, number_of_tiles+1):
    screen.blit(img,(x,Y_OFFSET+(5*y)))

  bag_count_img = WW_value_font.render(str(number_of_tiles), True, BLACK)
  screen.blit(bag_count_img,(x+10,Y_OFFSET+(5*y)+7))
  count_img     = WW_value_font.render("LEFT",True, BLACK)
  screen.blit(count_img,(x+8,Y_OFFSET+(5*y)+12+10))

start_time_player_background_modulation = time.time()
active_player_background_highlight = True  

game_card_coodinates = {"Player 1":(0,0,0,0),"Player 2":(0,0,0,0),"Player 3":(0,0,0,0),"Player 4":(0,0,0,0),"AL":(0,0,0,0)}

def player_card_clicked(pos):
  if (click_area(pos,game_card_coodinates["Player 1"][0],game_card_coodinates["Player 1"][1],game_card_coodinates["Player 1"][2],game_card_coodinates["Player 1"][3])):
    return("Player 1")
  if (click_area(pos,game_card_coodinates["Player 2"][0],game_card_coodinates["Player 2"][1],game_card_coodinates["Player 2"][2],game_card_coodinates["Player 2"][3])):
    return("Player 2")
  if (click_area(pos,game_card_coodinates["Player 3"][0],game_card_coodinates["Player 3"][1],game_card_coodinates["Player 3"][2],game_card_coodinates["Player 3"][3])):
    return("Player 3")
  if (click_area(pos,game_card_coodinates["Player 4"][0],game_card_coodinates["Player 4"][1],game_card_coodinates["Player 4"][2],game_card_coodinates["Player 4"][3])):
    return("Player 4")
  if (click_area(pos,game_card_coodinates["AL"][0],game_card_coodinates["AL"][1],game_card_coodinates["AL"][2],game_card_coodinates["AL"][3])):
    return("AL")
  else:
    return("NONE")

def show_player_words(card_display):
  # Create a surface for the popup
  popup_width = 600
  popup_height = 500

  # Center the popup on the screen
  x = (SCREEN_WIDTH - popup_width) // 2
  y = (SCREEN_HEIGHT - popup_height) // 2

  # Create the popup surface  
  popup_surface = pygame.Surface((popup_width, popup_height))
  popup_surface.fill(GRAY)
  pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

  # X,Y offset
  txtX = 50
  txtY = 1
  gap = 15
  wraplen = 70
  
  # Title Text:
  text1 = "Last 10 words for: "+card_display
  my_wrap = textwrap.TextWrapper(width=wraplen)
  wrap_list1 = my_wrap.wrap(text=text1)

  # Draw title text1
  for i in wrap_list1:
    txtY = txtY + gap
    Mtxt = WW_definition_bold.render(f"{i}", True, BLACK)
    popup_surface.blit(Mtxt, (txtX, txtY))

  txtY += gap # add gap between title and words

  #Render words and definitions
  text2 = "empty"


  if (card_display == "Player 1"):
    player_words = WW_player1
  elif (card_display == "Player 2"):
    player_words = WW_player2
  elif (card_display == "Player 3"):
    player_words = WW_player3
  elif (card_display == "Player 4"):
    player_words = WW_player4
  elif (card_display == "AL"):
    player_words = WW_AL

  #print(player_words["words"])

  count = 0
  if (len(player_words["words"]) != 0) and (player_words["status"] == "playing"):
    for word_score in reversed(player_words["words"]):
      if (count < 10):
        word  = word_score[0]
        score = word_score[1]

        text2 = "Word: "+word+", Score: "+str(score)+", Def: "+word_definitions[word.upper()]   

        wrap_list2 = my_wrap.wrap(text=text2)

        # Draw one line at a time further down the screen
        for i in wrap_list2:
          txtY = txtY + gap
          Mtxt = WW_definition.render(f"{i}", True, BLACK)
          popup_surface.blit(Mtxt, (txtX, txtY))

        txtY += gap
        count += 1

  screen.blit(popup_surface, (x, y))
  pygame.display.flip()

def display_player (x,y,active_player,score,name,avatar_index,hand,player,progress_bar,words):
  global start_time_player_background_modulation, active_player_background_highlight
  global game_card_coodinates

  #print ("line 1439: AL player data: ", WW_AL)

  tile_count = 0

  #Chech how many tiles left in the players hand
  for i in range (0,7):
    if hand[i] != '#':
      tile_count += 1

  if time.time() - start_time_player_background_modulation >= 1:
    start_time_player_background_modulation = time.time()

    if active_player_background_highlight == True:
      active_player_background_highlight = False
    else:
      active_player_background_highlight = True

  if (active_player and active_player_background_highlight):
    img = avatar_background2
  else:
    img = avatar_background
  screen.blit(img,(x,y))

  draw_text_center (screen,x+60,y+14,name,18,BLACK)

  if player == "AL":
    avatar_image = al_avatar[avatar_index]
  else:
    avatar_image = avatar[avatar_index]
  avatar_image.set_colorkey(WHITE)
  screen.blit(avatar_image,(x+20,y+25)) #blit the avatar on and make white the transparent color
  draw_text_center (screen,x+60,y+104,"Score: "+str(score),19,BLACK)

  tile_text = "TILES: "+str(tile_count)
  draw_text (screen, x+83,y+5,tile_text,13,BLACK)

  if (progress_bar > 0):
    pygame.draw.rect(screen,GREEN,pygame.Rect(x+120-5-7,y+15,5,AL_percent_complete))
   
  #Record the player card coordinates
  game_card_coodinates[player] = (x,y,x+avatar_background.get_width(),y+avatar_background.get_height())

def show_turn_scores_go_button(screen):
  #Draw palyer1 Name and score tile, score is '---' = nonplaying player)
  x = 0
  y = 0
  player_card_height = 120

  if (WW_player1["status"] == "playing"):
    display_player(x,y,WW_player1["player"] == WW_active_player,WW_player1["score"],WW_player1["player name"],WW_player1["avatar index"],WW_player1["hand"],WW_player1["player"],0,WW_player1["words"])
    
    #print("line 1504: ", WW_player1)

  if (WW_player2["status"] == "playing"):
    y += player_card_height
    display_player(x,y,WW_player2["player"] == WW_active_player,WW_player2["score"],WW_player2["player name"],WW_player2["avatar index"],WW_player2["hand"],WW_player2["player"],0,WW_player2["words"])
  
  if (WW_player3["status"] == "playing"):
    y += player_card_height
    display_player(x,y,WW_player3["player"] == WW_active_player,WW_player3["score"],WW_player3["player name"],WW_player3["avatar index"],WW_player3["hand"],WW_player3["player"],0,WW_player3["words"])
  
  if (WW_player4["status"] == "playing"):
    y += player_card_height
    display_player(x,y,WW_player4["player"] == WW_active_player,WW_player4["score"],WW_player4["player name"],WW_player4["avatar index"],WW_player4["hand"],WW_player4["player"],0,WW_player4["words"])

  if (WW_AL["status"] == "playing"):
    y += player_card_height
    #print("line 1499 avatar index: ", WW_AL["avatar index"])
    display_player(x,y,WW_AL["player"] == WW_active_player,WW_AL["score"],WW_AL["player name"],WW_AL["avatar index"],WW_AL["hand"],WW_AL["player"],AL_percent_complete,WW_AL["words"])
  
  #draw go button
  if (myturn() and go_button_clicked == False):
    img = go_tile # allow the user to press the go button when they finished their turn
  else:
    img = wait_tile # let the player know the other player is working on their word.
  screen.blit(img,(X_OFFSET+(15*40),Y_OFFSET+20+(15*40)))

  #draw dictionary button
  img = dictonary_icon # let the player know the other player is working on their word.
  screen.blit(img,(X_OFFSET+(15*40),Y_OFFSET+(14*40)))

  #draw AL button
  if (WW_AL["status"] == "notplaying"):
    img = invite_al_button # let the player know the other player is working on their word.
  else:
    img = kick_al_button
  screen.blit(img,(X_OFFSET+(15*40),Y_OFFSET+(13*40)))

  #Show last score
  draw_text_center (screen,X_OFFSET+(12*40)-5,Y_OFFSET+(15*40)+25,"Last Score: "+str(WW_player_last_score),30,WHITE)  
  
def show_turn_scores_go_button_old(screen):
  p1_score = WW_player1["score"]
  p2_score = WW_player2["score"]
  p3_score = WW_player3["score"]
  p4_score = WW_player4["score"]
  
  WW_y_offset = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET
  score_text_x_offset_p1 = X_OFFSET + (10*40) + 12
  score_text_x_offset_p2 = X_OFFSET + (11*40) + 12
  score_text_x_offset_p3 = X_OFFSET + (12*40) + 12
  score_text_x_offset_p4 = X_OFFSET + (13*40) + 12
  

  #Draw palyer1 Name and score tile, score is '---' = nonplaying player)
  if (WW_player1["status"] == "playing"):
    img = blank_tile1
    screen.blit(img, (X_OFFSET+(10*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 1", True, BLACK)
    screen.blit(player_name_img,(X_OFFSET+(10*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render(str(p1_score), True, BLACK)
    screen.blit(score_img,(score_text_x_offset_p1, (WW_y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (X_OFFSET+(10*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 1", True, WHITE)
    screen.blit(player_name_img,(X_OFFSET+ (10*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,(score_text_x_offset_p1, (WW_y_offset)+16) )

  #Draw palyer2 Name and score tile, score is '---' = nonplaying player)
  if (WW_player2["status"] == "playing"):
    img = blank_tile2
    screen.blit(img, (X_OFFSET+(11*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 2", True, BLACK)
    screen.blit(player_name_img,(X_OFFSET+ (11*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render(str(p2_score), True, BLACK)
    screen.blit(score_img,(score_text_x_offset_p2, (WW_y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (X_OFFSET+(11*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 2", True, WHITE)
    screen.blit(player_name_img,(X_OFFSET+(11*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_x_offset_p2, (WW_y_offset)+16) )

  #Draw palyer3 Name and score tile, score is '---' = nonplaying player)
  if (WW_player3["status"] == "playing"):
    img = blank_tile3
    screen.blit(img, (X_OFFSET+(12*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 3", True, BLACK)
    screen.blit(player_name_img,(X_OFFSET+(12*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render(str(p3_score), True, BLACK)
    screen.blit(score_img,( score_text_x_offset_p3, (WW_y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (X_OFFSET+(12*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 3", True, WHITE)
    screen.blit(player_name_img,(X_OFFSET+ (12*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_x_offset_p3, (WW_y_offset)+16) )

  #Draw palyer3 Name and score tile, score is '---' = nonplaying player)
  if (WW_player4["status"] == "playing"):
    img = blank_tile4
    screen.blit(img, (X_OFFSET+(13*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 4", True, BLACK)
    screen.blit(player_name_img,(X_OFFSET+ (13*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render(str(p4_score), True, BLACK)
    screen.blit(score_img,( score_text_x_offset_p4, (WW_y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (X_OFFSET+(13*40),WW_y_offset))
    player_name_img = WW_score_font.render("Player 4", True, WHITE)
    screen.blit(player_name_img,(X_OFFSET + (13*40)+2,(WW_y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_x_offset_p4, (WW_y_offset)+16) )

  #draw go button
  if (myturn() and go_button_clicked == False):
    img = go_tile # allow the user to press the go button when they finished their turn
  else:
    img = wait_tile # let the player know the other player is working on their word.
  screen.blit(img,(X_OFFSET+(15*40),WW_y_offset))

  #draw dictionary button
  img = dictonary_icon # let the player know the other player is working on their word.
  screen.blit(img,(X_OFFSET+(15*40),14*40))

def no_tiles_set_for_exchange():
  #If there is a single character identified for eachange return False
  hand = get_my_hand()
  for tile in hand:
    if tile.islower():
      return (False)
  return(True)

def pickup_tile(pos):
  global WW_GAMEBOARD_WORDS
  global WW_DIRTY_GAMEBOARD
  global selected_tile_letter
  global WW_Client_player
  global WW_player1, WW_player2, WW_player3, WW_player4

  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET

  mouse_x = pos[0]
  mouse_y = pos[1]
 
  hand = get_my_hand()

  #If tile is picked up from players hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    hand_position = math.floor((mouse_x-X_OFFSET)/40)

   #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if hand_position > 6:
      hand_position = 6

    #Don't pick up empty tile
    if (hand[hand_position] != '#' and no_tiles_set_for_exchange()):
      selected_tile_letter = hand[hand_position]
      hand[hand_position] = '#'
    else:
      selected_tile_letter = '#'

  #if tile is picked up from gameboard
  if (mouse_x >= 0+X_OFFSET and mouse_x <= X_OFFSET + (15*40) and mouse_y >= 0+Y_OFFSET and mouse_y <=(15*40)+Y_OFFSET):
    tile_x = math.floor((mouse_x-X_OFFSET)/40)
    tile_y = math.floor((mouse_y-Y_OFFSET)/40)

    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if (tile_x > 14):
      tile_x = 14
    if (tile_y > 14):
      tile_y = 14

    #Check that the tile clicked is not empty or and old tile and it is my turn
    if (WW_GAMEBOARD_WORDS[tile_y][tile_x] != "#" and WW_DIRTY_GAMEBOARD[tile_y][tile_x] != '0' and myturn()):
      if (WW_GAMEBOARD_WORDS[tile_y][tile_x].islower()): #If picking up an assigned letter blank tile then reset to blank
        selected_tile_letter = ' '
      else:
        selected_tile_letter = WW_GAMEBOARD_WORDS[tile_y][tile_x]
      WW_GAMEBOARD_WORDS[tile_y][tile_x] = '#'
      WW_DIRTY_GAMEBOARD[tile_y][tile_x] = '#'
  
  set_my_hand(hand)

def myturn():
  return (WW_Client_player == WW_active_player)

def notmyturn():
  return (WW_Client_player != WW_active_player)

def drop_tile(pos):
  global selected_tile_letter
  global WW_player1, WW_player2, WW_player3, WW_player4
  global WW_GAMEBOARD_WORDS
  global WW_DIRTY_GAMEBOARD

  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET
  
  mouse_x = pos[0]
  mouse_y = pos[1]

  successful_insert = False

  hand = get_my_hand()

  # Check for drop in new positon of hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    drop_tile_hand_location = math.floor((mouse_x-X_OFFSET)/40)

    if (drop_tile_hand_location > 6):
      drop_tile_hand_location = 6

    #print("drop location in hand: ", drop_tile_hand_location)
    #If the postion the tile is dropped in the hand is free then drop the tile there
    if (hand[drop_tile_hand_location] == '#'):
      hand[drop_tile_hand_location] = selected_tile_letter
      selected_tile_letter = '#'

    else:
      #if the tile is dropped on a existing tile in the hand then bump the existing ones as needed
      #Check for empty location to the left of the drop
      #print("trying to insert tile in hand")
      for i in range (0,drop_tile_hand_location):
        #print("made it in left hand search for empty slot: ", i, " ", player1_hand[i])
        if hand[i] == '#':
          #print("found blank on left at positon: ",i)
          #move tiles left
          for y in range(i,drop_tile_hand_location+1):
            #print("y = ",y)
            if (y+1 != 7):
              hand[y] = hand[y+1]
          hand[drop_tile_hand_location] = selected_tile_letter # put the tile in the new spot
          successful_insert = True
          selected_tile_letter = '#'
          break 

      if (successful_insert == False):
        #Bump hand at insertion point to the right
        for i in range (drop_tile_hand_location+1, 7): # 7 is the stoping case
          if hand[i] == '#':
            #print("found blank on right at position: ",i)
            #move tiles rigth
            for y in range(i,drop_tile_hand_location, -1):
              hand[y]=hand[y-1]
            hand[drop_tile_hand_location]=selected_tile_letter # put the tile in the new spot
            selected_tile_letter = '#'
            break

  # check for drop on the gameboard
  if (mouse_x >= 0+X_OFFSET and mouse_x <= (15*40)+X_OFFSET and mouse_y >= 0+Y_OFFSET and mouse_y <=(15*40)+Y_OFFSET):
    tile_x = math.floor((mouse_x-X_OFFSET)/40)
    tile_y = math.floor((mouse_y-Y_OFFSET)/40)

    #print (tile_x,tile_y)

    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if (tile_x > 14):
      tile_x = 14
    if (tile_y > 14):
      tile_y = 14

    #Check to see if the game tile location is occupied
    if (WW_GAMEBOARD_WORDS[tile_y][tile_x] == '#' and selected_tile_letter != '#' and myturn()):
      WW_GAMEBOARD_WORDS[tile_y][tile_x] = selected_tile_letter
      WW_DIRTY_GAMEBOARD[tile_y][tile_x] = '1'

      selected_tile_letter = '#'
    else:
      #return the character to the hand at the first available blank
      for i in range(0,7):
        if hand[i] == '#':
          hand[i] = selected_tile_letter
          selected_tile_letter = '#'
          break

  set_my_hand(hand)  

def player_swap_refill_hand():
  #Handle swaping the player who controls the board
  #refill my hand
  #refill_hand()
  #Send current player data to server
  WW_client_send_game_data_to_server()
  
  #Ask server to refill my hand (update the local Client version of my hand)
  WW_client_refill_hand(WW_Client_player)

  #Ask server to select the next player
  WW_client_send_turn_over_command()
  
  #Get data from server
  WW_client_request_game_data_from_server()

  #print("Player: (",WW_Client_player,") asked server to end turn.  New active player is (",WW_active_player,")")

def ismytile(pos):
  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET

  global player

  mouse_x = pos[0]
  mouse_y = pos[1]

  #Check if clicking in our hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    return (True)

  #Check if clicking the gameboard (make sure it's our tile)
  if (mouse_x >= 0+X_OFFSET and mouse_x <= (15*40)+X_OFFSET and mouse_y >= 0 + Y_OFFSET and mouse_y <=(15*40) + Y_OFFSET):
    tile_x = math.floor((mouse_x-X_OFFSET)/40)
    tile_y = math.floor((mouse_y-Y_OFFSET)/40)

    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if (tile_x > 14):
      tile_x = 14
    if (tile_y > 14):
      tile_y = 14

    #Check to see if the game tile location is occupied
    if WW_DIRTY_GAMEBOARD[tile_y][tile_x] == '1':
      return(True)
    else:
      return (False)

def out_of_bounds(pos):
  x = 0 + X_OFFSET
  y = HAND_PLAYER_GO_Y_OFFSET + Y_OFFSET

  global player

  mouse_x = pos[0]
  mouse_y = pos[1]

  #If dragging on the hand then not out of bounds
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    return (False)

  #If dragging over game board then not out of bounds
  if (mouse_x >= X_OFFSET and mouse_x <= X_OFFSET+(15*40) and mouse_y >= Y_OFFSET and mouse_y <= Y_OFFSET+(15*40)):
    return (False)

  #If draging elsewhere then out of bounds.
  return(True)

def drop_tile_hand():
  global selected_tile_letter
  global WW_player1, WW_player2, WW_player3, WW_player4
  global WW_Client_player

  hand = get_my_hand()

  #return the character to the hand at the first available blank
  for i in range(0,7):
    if hand[i] == '#':
      hand[i] = selected_tile_letter
      selected_tile_letter = '#'
      break

  set_my_hand(hand)
  
def score_west_east_word(gb,db,start_x,start_y):
  global WW_player1, WW_player2, WW_player3, WW_player4

  score = 0
  word_multiplier = 1
  # Multipliers on new tiles
  # 1=Normal Tile
  # 2=Double letter
  # 3=Tripple letter
  # 4=Tripple word
  # 5=Double word

  # find west most tile
  for x in range (start_x,-1,-1): # look at the tiles west of the new tile end of the word
    y = start_y # First new tile y coodinate

    #Check for tripple word or double word multiplier under a new tile
    if (gb[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and db[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((WW_GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and db[y][x] == '1'):
        word_multiplier *= 2

    if gb[y][x] == '#':
      west_most_tile_x = x+1
      break
    if x==0: #found the west edge of the board
      west_most_tile_x = 0

  for x in range (start_x,15): # look at the tiles east of the new tile for the end of the word

    #Check for tripple word or double word multiplier under a new tile
    if (gb[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and db[y][x] == '1' and x != start_x):
        word_multiplier *= 3
      #Look for double multiplier
      if ((WW_GAMEBOARD[y][x] == '5' or WW_GAMEBOARD[y][x] == '0') and db[y][x] == '1' and x != start_x):
        word_multiplier *= 2

    if gb[y][x] == "#":
      east_most_tile_x = x-1
      break
    if x==14:
      east_most_tile_x = 14 #found the east edge of the board 

  #Sum up the values of the WE root word
  new_word = ""
  for x in range (west_most_tile_x, east_most_tile_x+1):
    new_word += WW_GAMEBOARD_WORDS[y][x].upper()

    #Check for double letter
    if (WW_GAMEBOARD[y][x] == '2' and db[y][x] == '1'):
      score += 2*(letter_value[gb[y][x]])

    #Check for tripple letter
    elif (WW_GAMEBOARD[y][x] == '3' and db[y][x] == '1'):
      score += 3*(letter_value[gb[y][x]])

    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[gb[y][x]]

  if (WW_Client_player == "Player 1"):
    WW_player1["words"].append([new_word,score])
    #print ("Added word to WW_player1:",WW_player1)

  if (WW_Client_player == "Player 2"):
    WW_player2["words"].append([new_word,score])
    #print ("Added word to WW_player2:",WW_player2)

  if (WW_Client_player == "Player 3"):
    WW_player3["words"].append([new_word,score])
    #print ("Added word to WW_player3:",WW_player3)

  if (WW_Client_player == "Player 4"):
    WW_player4["words"].append([new_word,score])
    #print ("Added word to WW_player4:",WW_player4)

  #Factor in word multiplier
  score *= word_multiplier

  return (score)

def score_north_south_word(gb,db,start_x,start_y):
  global WW_player1, WW_player2, WW_player3, WW_player4
  score = 0
  word_multiplier = 1
  # Multipliers on new tiles
  # 1=Normal Tile
  # 2=Double letter
  # 3=Tripple letter
  # 4=Tripple word
  # 5=Double word

  # find north most tile
  for y in range (start_y,-1,-1): # look at the tiles west of the new tile end of the word
    x = start_x # First new tile x coodinate

    #Check for tripple word or double word multiplier under a new tile
    if (gb[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and db[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((WW_GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and db[y][x] == '1'):
        word_multiplier *= 2

    if gb[y][x] == '#':
      north_most_tile_y = y+1
      break
    if y==0: #found the north edge of the board
      north_most_tile_y = 0

  for y in range (start_y,15): # look at the tiles east of the new tile for the end of the word
    #Check for tripple word or double word multiplier under a new tile
    if (gb[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and db[y][x] == '1' and y != start_y):
        word_multiplier *= 3
      #Look for double multiplier
      if ((WW_GAMEBOARD[y][x] == '5' or WW_GAMEBOARD[y][x] == '0') and db[y][x] == '1' and y != start_y):
        word_multiplier *= 2

    if gb[y][x] == "#":
      south_most_tile_y = y-1
      break
    if y==14:
      south_most_tile_y = 14 #found the south edge of the board 

  #print ("north most: ",north_most_tile_y," south most: ",south_most_tile_y)
  #Sum up the values of the NS root word
  new_word = ""
  for y in range (north_most_tile_y, south_most_tile_y+1):
    new_word += WW_GAMEBOARD_WORDS[y][x].upper()

    #Check for double letter
    if (WW_GAMEBOARD[y][x] == '2' and db[y][x] == '1'):
      score += 2*(letter_value[gb[y][x]])
    
    #Check for tripple letter
    elif (WW_GAMEBOARD[y][x] == '3' and db[y][x] == '1'):
      score += 3*(letter_value[gb[y][x]])
    
    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[gb[y][x]]
  
  if (WW_Client_player == "Player 1"):
    WW_player1["words"].append([new_word,score])
    #print ("Added word to WW_player1:",WW_player1)

  if (WW_Client_player == "Player 2"):
    WW_player2["words"].append([new_word,score])
    #print ("Added word to WW_player2:",WW_player2)

  if (WW_Client_player == "Player 3"):
    WW_player3["words"].append([new_word,score])
    #print ("Added word to WW_player3:",WW_player3)

  if (WW_Client_player == "Player 4"):
    WW_player4["words"].append([new_word,score])
    #print ("Added word to WW_player4:",WW_player4)

  #Factor in word multiplier
  score *= word_multiplier

  return(score)

def detect_west_east_word (gb,x,y):
  #check west and east of tile at x,y to see if there is a word
  if (x-1>=0):
    if (gb[y][x-1] != '#'):
      return(True) #found letter to the west of the first new tile
  if (x+1<=14):
    if (gb[y][x+1] != '#'):
      return(True)
  return(False)

def detect_north_south_word (gb,x,y):
  #check north and south of tile at x,y to see if there is a word
  if (y-1>=0):
    if (gb[y-1][x] != '#'):
      return(True) #found letter to the north of the first new tile
  if (y+1<=14):
    if (gb[y+1][x] != '#'):
      return(True) #Found letter to the south of the first new tile
  return (False)

def calculate_score (gb,db):
  x = 0
  y = 0
  player_score = 0

  #new_tiles ['Tile Letter', Tile X, Tile Y, Multiplier]
  # Multiplier: 
  # 2=Double letter
  # 3=Tripple letter
  # 4=Tripple word
  # 5=Double word

  new_tiles = [['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0],
               ['#', 0, 0, 0]]


  #find new tiles played and store them and their position in new_tiles
  number_of_new_tiles = 0
  for x in range (0,15):
    for y in range (0,15):
      if (db[y][x] == '1'):
        if (number_of_new_tiles > 14):
          print("found too many tiles")
          print(new_tiles)
          exit(1)
        new_tiles [number_of_new_tiles][0] = gb[y][x]
        new_tiles [number_of_new_tiles][1] = x 
        new_tiles [number_of_new_tiles][2] = y
        new_tiles [number_of_new_tiles][3] = WW_GAMEBOARD[y][x] #tile type aka multipler

        number_of_new_tiles += 1 

  #print(new_tiles)
  if (number_of_new_tiles == 0):
    #print("Whoops no new tiles found")
    return 0

  #location of the root tile (most north west tile)
  x = new_tiles[0][1] #first new tile x coordinate
  y = new_tiles[0][2] #first new tile y coordinate

  #Score root word WE and NS if there are words formed in those directions
  if (detect_north_south_word(gb,x,y)):
    player_score += score_north_south_word(gb,db,x,y)
    #print("NS word found at root. Player score = ",player_score)
  if (detect_west_east_word(gb,x,y)):
    #print("WE word found at root. Player score = ", player_score)
    player_score += score_west_east_word(gb,db,x,y)

  #Scan along the new tiles (but not the root tile which was already scored) for new words made and count their score
  if (new_tiles[1][0] != '#'): #Check if there is only one new tile
    #print("more than a single character word")
    for i in range (1,14):
      if (new_tiles[i][0] != '#'):
        x = new_tiles[i][1]
        y = new_tiles[i][2]
        if (new_tiles[0][1] == new_tiles[1][1]): # A north south word (x's are the same)
          if(detect_west_east_word(gb,x,y)):
            #print("added WE word score for root tile: ", new_tiles[i][0])
            player_score += score_west_east_word(gb,db,x,y)
        else:
          if(detect_north_south_word(gb,x,y)):
            #print("added NS word score for root tile: ", new_tiles[i][0])
            player_score += score_north_south_word(gb,db,x,y)
  
  if (all_tiles_played(db)):
    player_score += 50 #Add the 50 point bonus for playing all tiles

  return(player_score)

def score_word (gb,db):
  global WW_player_last_score
  global WW_player1, WW_player2, WW_player3, WW_player4

  player_score = calculate_score (gb,db)

  if (WW_Client_player == "Player 1"):
    WW_player1["score"] += player_score
    print("P1_score_add: ", player_score)
  if (WW_Client_player == "Player 2"):
    WW_player2["score"] += player_score
    print("P2_score_add: ", player_score)
  if (WW_Client_player == "Player 3"):
    WW_player3["score"] += player_score
    print("P3_score_add: ", player_score)
  if (WW_Client_player == "Player 4"):
    WW_player4["score"] += player_score
    print("P4_score_add: ", player_score)

  WW_player_last_score = player_score
  WW_Client_send_last_score()

def lock_word ():
  global WW_DIRTY_GAMEBOARD

  for x in range(0,15):
    for y in range(0,15):
      if WW_DIRTY_GAMEBOARD[y][x] == '1':
        WW_DIRTY_GAMEBOARD[y][x] = '0'

def is_game_board_dirty():
  for x in range(0,15):
    for y in range(0,15):
      if WW_DIRTY_GAMEBOARD[y][x] == '1':
        return (True)
  return(False)

def gameover_box(x,y,popup_width,popup_height,text1,text2):
    # Create a surface for the popup
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(GRAY)
    pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

    # Render the text
    text_surface = font.render(text1, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)-10))
    popup_surface.blit(text_surface, text_rect)
    text_surface = font.render(text2, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)+10))
    popup_surface.blit(text_surface, text_rect)
    

    screen.blit(popup_surface, (x, y))
    pygame.display.flip()

    # Wait for a key press to close the popup
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                return

def generic_popup_box(x,y,popup_width,popup_height,text1,text2):
    # Create a surface for the popup
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(GRAY)
    pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

    # Render the text
    text_surface = font.render(text1, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)-10))
    popup_surface.blit(text_surface, text_rect)
    text_surface = font.render(text2, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)+10))
    popup_surface.blit(text_surface, text_rect)
    

    screen.blit(popup_surface, (x, y))
    pygame.display.flip()

    # Wait for a key press to close the popup
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_RETURN:
                return True
              else:
                return False

def popup_box(text1,text2):
    # Create a surface for the popup
    popup_width = 600
    popup_height = 200
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(GRAY)
    pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

    # Render the text
    text_surface = font.render(text1, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)-30))
    popup_surface.blit(text_surface, text_rect)
    text_surface = font.render(text2, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, (popup_height // 2)+30))
    popup_surface.blit(text_surface, text_rect)
    

    # Center the popup on the screen
    x = (SCREEN_WIDTH - popup_width) // 2
    y = (SCREEN_HEIGHT - popup_height) // 2
    screen.blit(popup_surface, (x, y))
    pygame.display.flip()

    # Wait for a key press to close the popup
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                return

def get_my_hand():
  if (WW_Client_player == "Player 1"):
    return (WW_player1["hand"].copy())
  elif (WW_Client_player == "Player 2"):
    return (WW_player2["hand"].copy())
  elif (WW_Client_player == "Player 3"):
    return (WW_player3["hand"].copy())
  elif (WW_Client_player == "Player 4"):
    return (WW_player4["hand"].copy())
  else:
    print("Error: WW_Client_player not set properly, it's set to:", WW_Client_player)
    exit()

def get_my_name():
  #return the name the player assigned themslefves on startup
  if (WW_Client_player == "Player 1"):
    return (WW_player1["player name"])
  elif (WW_Client_player == "Player 2"):
    return (WW_player2["player name"])
  elif (WW_Client_player == "Player 3"):
    return (WW_player3["player name"])
  elif (WW_Client_player == "Player 4"):
    return (WW_player4["player name"])
  else:
    print("Error: WW_Client_player not set properly, it's set to:", WW_Client_player)
    exit()

def set_my_hand (hand):
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (WW_Client_player == "Player 1"):
    WW_player1["hand"] = hand.copy()
  elif (WW_Client_player == "Player 2"):
    WW_player2["hand"] = hand.copy()
  elif (WW_Client_player == "Player 3"):
    WW_player3["hand"] = hand.copy()
  elif (WW_Client_player == "Player 4"):
    WW_player4["hand"] = hand.copy()

def get_my_score():
  if (WW_Client_player == "Player 1"):
    return (WW_player1["score"])
  elif (WW_Client_player == "Player 2"):
    return (WW_player2["score"])
  elif (WW_Client_player == "Player 3"):
    return (WW_player3["score"])
  elif (WW_Client_player == "Player 4"):
    return (WW_player4["score"])
  else:
    print("Error: WW_Client_player not set properly, it's set to:", WW_Client_player)
    exit()

def set_my_score (score):
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (WW_Client_player == "Player 1"):
    WW_player1["score"] = score
  elif (WW_Client_player == "Player 2"):
    WW_player2["score"] = score
  elif (WW_Client_player == "Player 3"):
    WW_player3["score"] = score
  elif (WW_Client_player == "Player 4"):
    WW_player4["score"] = score

def check_gameover():
  global gameover 

  if verbose:
    print("**** Checking for Game Over *****")

  if (WW_client_request_gameover_status()):  
    print("############ Server said the gameover!")
    hand = get_my_hand()
    score = get_my_score()
    set_my_score(score - value_player_hand (hand))
    gameover = True

def reset_game():
  global WW_Client_player
  global gameover 
  global run
  global pickup
  global WW_GAMEBOARD_WORDS
  global WW_DIRTY_GAMEBOARD
  global WW_player_last_score
  global selected_tile_letter
  
  #Reset the gameboard trackers
  for x in range(0,15):
    for y in range (0,15):
      WW_GAMEBOARD_WORDS[y][x] = '#'
      WW_DIRTY_GAMEBOARD[y][x] = '#'

  set_my_score(0)
  set_my_hand(['#','#','#','#','#','#','#'])

  WW_player_last_score = 0

  selected_tile_letter = '#' # = no tile selected
  
  #Ensure server has this plyers latest game data
  #WW_client_send_game_over_to_server(False)
  WW_client_request_game_data_from_server()
  
  gameover = False
  run = True
  pickup = False

def save_screen_capture():
  path = "assets/end_game_screen_caps/"

  isExist = os.path.exists(path)

  if not isExist:
    os.makedirs(path)
    print("Created new screen capture directory: ", path)

  screen_capture_base_str = path+"word_warrior_screen_capture_"+time.strftime("%Y%m%d-%H%M%S")
  screen_capture_full_name = screen_capture_base_str + ".jpg"

  #Append an ingrimental suffix when the same name is used
  count = 0
  while (os.path.exists(screen_capture_full_name)):
    screen_capture_full_name = screen_capture_base_str + "_" + str(count) + ".jpg"
    count += 1

  pygame.image.save(screen,screen_capture_full_name)

def clear_current_player_last_word():
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (WW_Client_player == "Player 1"):
    WW_player1["words"] = []

  elif (WW_Client_player == "Player 2"):
    WW_player2["words"] = []

  elif (WW_Client_player == "Player 3"):
    WW_player3["words"] = []

  elif (WW_Client_player == "Player 4"):
    WW_player4["words"] = []


#   _____ _           _     ______             _            
#  / ____| |         | |   |  ____|           (_)           
# | |    | |__   __ _| |_  | |__   _ __   __ _ _ _ __   ___ 
# | |    | '_ \ / _` | __| |  __| | '_ \ / _` | | '_ \ / _ \
# | |____| | | | (_| | |_  | |____| | | | (_| | | | | |  __/
#  \_____|_| |_|\__,_|\__| |______|_| |_|\__, |_|_| |_|\___|
#                                        __/ |             
#                                       |___/              
#

chat_display_buffer = []
chat_input = ""
chat_recipient = "all"
chat_recipient_name = "all"
chat_text_input = ""

def WW_chat_pop_up():
  global display_chat_box
  global local_chat_box
  global chat_display_buffer
  global chat_input, chat_text_input
  global you_got_mail

  you_got_mail = False 

  # Create a surface for the popup
  popup_width = 600
  popup_height = 500

  # Center the popup on the screen
  x = (SCREEN_WIDTH - popup_width) // 2
  y = (SCREEN_HEIGHT - popup_height) // 2

  # Create the popup surface  
  popup_surface = pygame.Surface((popup_width, popup_height))
  popup_surface.fill(GRAY)
  pygame.draw.rect(popup_surface, BLACK, (0, 0, popup_width, popup_height), 2)

  # X,Y offset
  txtX = 30
  txtY = 1
  gap = 15
  wraplen = 60

  # Title Text:
  text1 = "Chat Box: " + WW_Client_player + " (" + get_my_name() + ")"

  my_wrap = textwrap.TextWrapper(width=wraplen)
  wrap_list1 = my_wrap.wrap(text=text1)

  # Draw title text1
  for i in wrap_list1:
    txtY = txtY + gap
    Mtxt = WW_definition_bold.render(f"{i}", True, BLACK)
    popup_surface.blit(Mtxt, (txtX, txtY))

  txtY += gap # add gap between title and words
  

  #dequeue message from local_chat_box
  number_of_chat_lines = 9

  if len(local_chat_box) > 0:
    chat_text = local_chat_box.pop(0)

    if len(chat_display_buffer) >= number_of_chat_lines:
      chat_display_buffer.pop(0)
    chat_display_buffer.append(chat_text)


  for line in chat_display_buffer:
    text2 = line

    wrap_list2 = my_wrap.wrap(text=text2)

    # Draw one line at a time further down the screen
    for i in wrap_list2:
      txtY = txtY + gap
      Mtxt = WW_chat_font.render(f"{i}", True, BLACK)
      popup_surface.blit(Mtxt, (txtX, txtY))

    txtY += gap


  #draw input box
  text_x = x -70
  input_box_height = 30
  text_y = y+400
  font_size = 20

  #draw dividing line
  pygame.draw.line(popup_surface,BLACK,(text_x-8,text_y-10),(popup_width,text_y-10),5)

  color = BLUE

  if len(chat_input) > 0:
    if chat_input[0] == '@':
      color = RED 
    else:
      color = BLUE
  
  chat_text_input = "@"+chat_recipient_name+" "+chat_input

  draw_text(popup_surface,text_x,text_y,"CHAT: "+chat_text_input+cursor("_"),font_size,color)
    

  screen.blit(popup_surface, (x, y))
  pygame.display.flip()

def WW_Client_send_chat(chat_text):
  #format
  # if chat_text starts with @<name>
  # then send to that name only if they are a player

  global local_chat_box

  #format: chat_text is a string of text to send to all playing players

  if len(chat_text) > 0:
    #Ask server to accept pickled game data
    client_socket.send_cmd(b'ww_recvchat')

    #Check to make sure WW_Client_player is set
    if (WW_Client_player != "Player 1" and WW_Client_player != "Player 2" and WW_Client_player != "Player 3" and WW_Client_player != "Player 4"):
      print ("Error: WW_client_send_game_data_to_server requires WW_Client_player to be set to a valid player")
      exit()

    if WW_Client_player == "Player 1":
      d1 = WW_player1["player name"]

    if WW_Client_player == "Player 2":
      d1 = WW_player2["player name"]

    if WW_Client_player == "Player 3":
      d1 = WW_player3["player name"]

    if WW_Client_player == "Player 4":
      d1 = WW_player4["player name"]

    d2 = chat_text
    if d2[0] == "@":
      d3 = chat_text.split()[0] # get the first word which is the destination person if the word starts with @
      #print ("line 3221: send private chat to: ",d3)
    else:
      d3 = "@all" # send to all

    data = pickle.dumps((d1,d2,d3))

    # Send the pickled data payload
    client_socket.send_message(data,request_id ="ww_recvchat") 
  else:
      print("Error no text to send in WW_Client_send_chat")

def WW_Client_get_chats():
  #Reqest server to send this players chat box
  global addr, port
  global local_chat_box
  global you_got_mail

  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_getchats')

  #send the client name
  d1 = WW_Client_player

  data = pickle.dumps((d1))

  # Send the pickled data payload
  client_socket.send_message(data,request_id = "ww_getchats") 

  # Receive the size of the pickled data
  data = client_socket.receive_message(request_id = "ww_getchats")
  
  # Deserialize the data
  d1 = pickle.loads(data)

  chat = []

  chat = d1

  if len(chat) > 0:
    local_chat_box.append(chat)
    if display_chat_box != True:
      you_got_mail = True
      #print("line 2770: you_got_mail:", you_got_mail)

def rotate_chat_recipient():
  global chat_recipient_name, chat_recipient

  if chat_recipient == "all":
    if WW_player1["status"]=="playing":
      chat_recipient = "Player 1"
      chat_recipient_name = WW_player1["player name"]
    elif WW_player2["status"]=="playing":
      chat_recipient = "Player 2"
      chat_recipient_name = WW_player2["player name"]
    elif WW_player3["status"]=="playing":
      chat_recipient = "Player 3"
      chat_recipient_name = WW_player3["player name"]
    elif WW_player4["status"]=="playing":
      chat_recipient = "Player 4"
      chat_recipient_name = WW_player4["player name"]
    else:
      chat_recipient = "all"
      chat_recipient_name = "all"

  elif chat_recipient == "Player 1":
    if WW_player2["status"]=="playing":
      chat_recipient = "Player 2"
      chat_recipient_name = WW_player2["player name"]
    elif WW_player3["status"]=="playing":
      chat_recipient = "Player 3"
      chat_recipient_name = WW_player3["player name"]
    elif WW_player4["status"]=="playing":
      chat_recipient = "Player 4"
      chat_recipient_name = WW_player4["player name"]
    else:
      chat_recipient = "all"
      chat_recipient_name = "all"

  elif chat_recipient == "Player 2":
    if WW_player3["status"]=="playing":
      chat_recipient = "Player 3"
      chat_recipient_name = WW_player3["player name"]
    elif WW_player4["status"]=="playing":
      chat_recipient = "Player 4"
      chat_recipient_name = WW_player4["player name"]
    else:
      chat_recipient = "all"
      chat_recipient_name = "all"

  elif chat_recipient == "Player 3":
    if WW_player4["status"]=="playing":
      chat_recipient = "Player 4"
      chat_recipient_name = WW_player4["player name"]
    else:
      chat_recipient = "all"
      chat_recipient_name = "all"

  elif chat_recipient == "Player 4":
    chat_recipient = "all"
    chat_recipient_name = "all"

#  _   _ ______ _________          ______  _____  _  _______ _   _  _____ 
# | \ | |  ____|__   __\ \        / / __ \|  __ \| |/ /_   _| \ | |/ ____|
# |  \| | |__     | |   \ \  /\  / / |  | | |__) | ' /  | | |  \| | |  __ 
# | . ` |  __|    | |    \ \/  \/ /| |  | |  _  /|  <   | | | . ` | | |_ |
# | |\  | |____   | |     \  /\  / | |__| | | \ \| . \ _| |_| |\  | |__| |
# |_| \_|______|  |_|      \/  \/   \____/|_|  \_\_|\_\_____|_| \_|\_____|

#   _____ _ _            _              _____ _____     
#  / ____| (_)          | |   t    /\   |  __ \_   _|    ROBUST
# | |    | |_  ___ _ __ | |_  e   /  \  | |__) || |  ___ 
# | |    | | |/ _ \ '_ \| __| s  / /\ \ |  ___/ | | / __|
# | |____| | |  __/ | | | |_  t / ____ \| |    _| |_\__ \
#  \_____|_|_|\___|_| |_|\__|  /_/    \_\_|   |_____|___/


class RobustSocketClient:
    def __init__(self, host, port, timeout=2, max_retries=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.socket = None
        self.message_count = 0

    def connect(self, request_id="None"):
        for retries in range(self.max_retries):
            try:
                print(f"Connection on host: {self.host}, port: {self.port}")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(None)  # Blocking mode
                if verbose:
                  self.message_count += 1
                  print(f"{self.message_count}, Connection made: ",self.socket)
                return True
            except (socket.timeout, socket.error) as e:
                print(f"Connection error ({e}), retrying {retries + 1}/{self.max_retries}, request_id={request_id}")
                self.close()
                time.sleep(1)
        print(f"Failed to connect after {self.max_retries} attempts, request_id={request_id}")
        return False

    def send_cmd(self, cmd, max_retries=3, delay=1):
        if verbose:
          self.message_count += 1
          print(f"{self.message_count}, socket data: ",self.socket)
          print(f"{self.message_count}, send_cmd: {cmd}")
        return self._send(cmd, max_retries, delay, request_id = cmd)

    def send_message(self, message, request_id="None", max_retries=3, delay=1):
        if verbose:
          self.message_count += 1
          print(f"{self.message_count}, send_message: {request_id}")
        size = len(message).to_bytes(4, 'big')
        #send_size = self._send(size, max_retries, delay, request_id)
        #send_data = self._send(message, max_retries, delay, request_id)
        #return (send_size and send_data)
        return (self._send(size + message, max_retries, delay, request_id))
    def _send(self, data, max_retries, delay, request_id = "None"):
        for attempt in range(max_retries):
            try:
                if verbose:
                  self.message_count += 1
                  print(f"{self.message_count}, _send data: ", request_id," length: ", len(data))
                self.socket.sendall(data)
                return True
            except socket.error as e:
                print(f"Send error: {e}, attempt {attempt + 1}/{max_retries}")
                time.sleep(delay)
        return False

    def receive_message(self, buffer_size=4096, request_id="None", max_retries=3, delay=1):
        for attempt in range(max_retries):
            try:
                data_size_bytes = self.socket.recv(4)
                if len(data_size_bytes) < 4:
                    print(f"Connection closed by peer (less then 4 bytes): request_id={request_id}")
                    return None

                data_size = int.from_bytes(data_size_bytes, 'big')
                if data_size == 0:
                    print(f"Connection closed by peer (data_size == 0): request_id={request_id}")
                    return None

                # More robust receive that limits the recvie to just the amount needed or in a full 4k chunk
                data = b''
                while (len(data) < data_size):
                  get_size = data_size - len(data)
                  packet = self.socket.recv(get_size)
                  data += packet
                if verbose:
                  self.message_count += 1
                  print(f"{self.message_count}, Receive_message: {request_id}, Expected data size: {data_size}, Actual length received: {len(data)}")

                return data

            except socket.timeout:
                print(f"Timeout, retrying {attempt + 1}/{max_retries}, request_id={request_id}")
                time.sleep(delay)
            except socket.error as e:
                print(f"Receive error: {e}, request_id={request_id}")

        return None

    def close(self):
        if verbose:
          self.message_count += 1
          print(f"{self.message_count}, Socket close!!")
        if self.socket:
            self.socket.close()
            self.socket = None

def WW_client_request_game_data_from_server():
  global WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD,WW_player1,WW_player2,WW_player3,WW_player4,WW_bag,WW_player_last_score,WW_AL,AL_percent_complete
  global WW_active_player

  #if client_socket.connect(request_id = "ww_reqsdtx"):
  #Send the request pickled data from the server (player 1) client handler
  if (WW_Client_player == "Player 1"):
    client_socket.send_cmd(b'ww_reqsdat1')
    request_id_str = "ww_reqsdat1"
  elif (WW_Client_player == "Player 2"):
    client_socket.send_cmd(b'ww_reqsdat2')
    request_id_str = "ww_reqsdat2"
  elif (WW_Client_player == "Player 3"):
    client_socket.send_cmd(b'ww_reqsdat3')
    request_id_str = "ww_reqsdat3"
  elif (WW_Client_player == "Player 4"):
    client_socket.send_cmd(b'ww_reqsdat4')
    request_id_str = "ww_reqsdat4"
  else:
    print("WW_Client_player not set.  Current setting is: ", WW_Client_player)
    exit(1)

  data = client_socket.receive_message(request_id = request_id_str)
  
  #client_socket.close()

  # Deserialize the data
  d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11 = pickle.loads(data)

  WW_GAMEBOARD_WORDS = d1
  WW_DIRTY_GAMEBOARD = d2

  #************  TODO *****************
  #Add detection for being set to status == 'notplaying'

  #If I'm player 1 then don't update my hand from the server data.
  if (WW_Client_player != "Player 1"):
    WW_player1 = d3
  if (WW_Client_player != "Player 2"):
    WW_player2 = d4
  if (WW_Client_player != "Player 3"):
    WW_player3 = d5
  if (WW_Client_player != "Player 4"):
    WW_player4 = d6
    
  WW_bag = d7
  WW_player_last_score = d8

  WW_active_player = d9

  WW_AL = d10

  AL_percent_complete = d11

def WW_client_request_game_data_from_server_lite():
  global WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD,WW_player1,WW_player2,WW_player3,WW_player4,WW_bag,WW_player_last_score,WW_AL,AL_percent_complete
  global WW_active_player

  #if client_socket.connect(request_id = "ww_reqslite"):
  #Send the request pickled data from the server (player 1) client handler
  if (client_socket.send_cmd(b'ww_reqslite') == False):
    print("Failed to send ww_reqslite command")
    return False
  data = client_socket.receive_message(request_id = "ww_reqslite")
  if data == False:
    print("Failed to receive ww_reqslite data from the server")
    return False

  #print("2970: ww_reqslite: ",data)

  # Deserialize the data
  d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11 = pickle.loads(data)

  # Note that in the lite version of this we only use:
  # d3 = WW_player1
  # d4 = WW_player2
  # d5 = WW_player3
  # d6 = WW_player4
  # d7 = WW_bag
  # d10 = WW_AL

    #If I'm player 1 then don't update my hand from the server data.
  if (WW_active_player == "Player 1"):
    WW_player2 = d4
    WW_player3 = d5
    WW_player4 = d6

  if (WW_active_player == "Player 2"):
    WW_player1 = d3
    WW_player3 = d5
    WW_player4 = d6

  if (WW_active_player == "Player 3"):
    WW_player1 = d3
    WW_player2 = d4
    WW_player4 = d6

  if (WW_active_player == "Player 4"):
    WW_player1 = d3
    WW_player2 = d4
    WW_player3 = d5
  
  WW_bag = d7
  WW_player_last_score = d8
  WW_active_player = d9
  WW_AL = d10

  #print ("get lite AL: ", WW_AL)
  AL_percent_complete = d11

def WW_client_send_game_data_to_server():
  #if client_socket.connect(request_id = "ww_acptdata"):
  client_socket.send_cmd(b'ww_acptdata')
  
  #Check to make sure WW_Client_player is set
  if (WW_Client_player != "Player 1" and WW_Client_player != "Player 2" and WW_Client_player != "Player 3" and WW_Client_player != "Player 4"):
    print ("Error: WW_client_send_game_data_to_server requires WW_Client_player to be set to a valid player")
    exit()

  d1 = WW_GAMEBOARD_WORDS
  d2 = WW_DIRTY_GAMEBOARD

  #Receive the game data
  if (WW_Client_player == "Player 1"):
    d3 = WW_player1
  elif (WW_Client_player == "Player 2"):
    d3 = WW_player2
  elif (WW_Client_player == "Player 3"):
    d3 = WW_player3
  elif (WW_Client_player == "Player 4"):
    d3 = WW_player4
  else:
    print("WW_Client_player not set properly in WW_client_send_game_data_to_server")
    exit(1)

  # Serialize the data
  data = pickle.dumps((d1,d2,d3))

  #print("3048: size of ww_acptdata: ", len(data))
  # Send the pickled data payload
  client_socket.send_message(data,request_id = "ww_acptdata")

  #client_socket.close() 

def WW_client_send_game_over_to_server(force):
  #if force == True then force the gameover

  #if client_socket.connect(request_id = "ww_gameover"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_gameover')
  
  data = pickle.dumps((force))

  # Send the pickled data payload
  client_socket.send_message(data, request_id = "ww_gameover") 

  #client_socket.close()

  print("================> Client sent gameover <=================")
  if force == True:
    print("Force used")

def WW_client_try_to_join_game():
  rec_data = None 

  #Open and keep the socket for the game
  if client_socket.connect(request_id = "ww_joingame"):
    #Send the request pickled data from the server (player 1) client handler
    client_socket.send_cmd(b'ww_joingame')
    
    #Send the playes name and avatar index so other can know it
    d1 = player_name
    d2 = player_avatar_index 

    # Serialize the data
    data = pickle.dumps((d1,d2))

    # Send the pickled data payload
    client_socket.send_message(data,request_id = "ww_joingame")

    rec_data = client_socket.receive_message(request_id = "ww_joingame")

  #client_socket.close() 

  # If not none (i.e. no player slot assigned then return None)
  if rec_data != None:
    return(pickle.loads(rec_data))
  else:
    return (None)

def WW_client_leave_game(WW_player_name):

  #if client_socket.connect(request_id = "ww_leavgame"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_leavgame')
  
  # Serialize the data
  data = pickle.dumps(WW_player_name)

  print(" Send command for: ", WW_player_name," to leave the game")
  client_socket.send_message(data,request_id = "ww_leavgame")

  client_socket.close() # Close the socket at the end of the game.

def WW_client_send_turn_over_command():
  #if client_socket.connect(request_id = "ww_turnover"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_turnover')
  
  #client_socket.close() 

def WW_client_refill_hand(player):
  global WW_player1, WW_player2, WW_player3, WW_player4

  #if client_socket.connect(request_id = "ww_reflhand"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_reflhand')
  
  #Send the player name to refill
  # Serialize the data
  data = pickle.dumps((player))
  
  # Send the pickled data payload
  client_socket.send_message(data,request_id = "ww_reflhand")

  rec_data = client_socket.receive_message(request_id = "ww_reflhand")

  #client_socket.close() 

  # Deserialize the data
  player_library = pickle.loads(rec_data)

  #Decode which refilled player library was returned and store it in our local player library
  if (player_library["player"] == "Player 1"):
    WW_player1 = player_library
  elif (player_library["player"] == "Player 2"):
    WW_player2 = player_library
  elif (player_library["player"] == "Player 3"):
    WW_player3 = player_library
  elif (player_library["player"] == "Player 4"):
    WW_player4 = player_library
  else:
    print ("Error: server returned invalid player refill name")
    exit()

def WW_client_request_gameover_status():
  gover = False

  #if client_socket.connect(request_id = "ww_reqgmovr"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_reqgmovr')
  
  rec_data = client_socket.receive_message(request_id = "ww_reqgmovr")

  #client_socket.close() 

  gover = pickle.loads(rec_data)

  #Return the True or False if game is over
  return(gover)

def WW_Set_AL_Fairness():
  #if client_socket.connect(request_id = "ww_setfairn"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_setfairn')
  
  # Serialize the data
  # al_avatar_index = 0 to 3 (0 = EASY, 3 = NO MERCY)
  data = pickle.dumps(al_avatar_index)

  client_socket.send_message(data,request_id = "ww_setfairn")

  #client_socket.close()

def WW_Client_toggleAL():
  #if client_socket.connect(request_id = "ww_toggleal"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_toggleal')
  
  #client_socket.close() 

def WW_Client_send_last_score():
  #if client_socket.connect(request_id = "ww_lastscor"):
  #Send the request pickled data from the server (player 1) client handler
  client_socket.send_cmd(b'ww_lastscor')
  
  # Serialize the data
  # al_avatar_index = 0 to 3 (0 = EASY, 3 = NO MERCY)
  data = pickle.dumps(WW_player_last_score)

  client_socket.send_message(data, request_id = "ww_lastscor")

  #client_socket.close()

def WW_register_with_server():
  global start_time, run, gameover, new_game, WW_Client_player
  global WW_player1, WW_player2, WW_player3, WW_player4
  global client_socket

  #Allow user to enter the server address
  start_screen_get_server_ip_address()

  #Connect to server if not conected
  if client_socket == None:
    print(f"Creating socket host: {addr}, port: {port}")
    client_socket = RobustSocketClient(addr,port)

  #Try to join the game
  not_invited_to_game = True 

  while not_invited_to_game:
    print(" Trying to joing the game")
    Join_Game_Player_library = WW_client_try_to_join_game()
    if (Join_Game_Player_library["player"] != "none"):
      WW_Client_player = Join_Game_Player_library["player"]
      not_invited_to_game = False
      if(WW_Client_player == "Player 1"):
        WW_player1 = Join_Game_Player_library
        WW_player1["player name"]  = player_name
        WW_player1["avatar index"] = player_avatar_index
      elif (WW_Client_player == "Player 2"):
        WW_player2 = Join_Game_Player_library
        WW_player2["player name"]  = player_name
        WW_player2["avatar index"] = player_avatar_index
      elif (WW_Client_player == "Player 3"):
        WW_player3 = Join_Game_Player_library
        WW_player3["player name"]  = player_name
        WW_player3["avatar index"] = player_avatar_index
      elif (WW_Client_player == "Player 4"):
        WW_player4 = Join_Game_Player_library
        WW_player4["player name"]  = player_name
        WW_player4["avatar index"] = player_avatar_index
      print("*** Server assigned us player: ", Join_Game_Player_library["player"])
    else:
      print(" Game is full")
      str1 = "         GAME FULL:"
      str2 = "     Hit key to try again"
      popup_box(str1,str2)
      
      client_socket.close()

      time.sleep(1)

  #print("Getting server data after joining the game")
  WW_client_request_game_data_from_server()

  #print("*** after requesting data from server player 1 library = ", WW_player1)
  #Read the data on the server to update our game data (include WW_active_player)
  if (myturn()):
    print(" We are the active player")

  start_time = time.time()
  run = True 
  gameover = False
  new_game = False

#   _____                            _              _____  _                          __        _    __  
#  / ____|                          | |            |  __ \| |                        / /  /\   | |   \ \ 
# | |     ___  _ __ ___  _ __  _   _| |_ ___ _ __  | |__) | | __ _ _   _  ___ _ __  | |  /  \  | |    | |
# | |    / _ \| '_ ` _ \| '_ \| | | | __/ _ \ '__| |  ___/| |/ _` | | | |/ _ \ '__| | | / /\ \ | |    | |
# | |___| (_) | | | | | | |_) | |_| | ||  __/ |    | |    | | (_| | |_| |  __/ |    | |/ ____ \| |____| |
#  \_____\___/|_| |_| |_| .__/ \__,_|\__\___|_|    |_|    |_|\__,_|\__, |\___|_|    | /_/    \_\______| |
#                       | |                                         __/ |            \_\             /_/ 
#                       |_|                                        |___/                                 

def computer_player_takes_turn():
  # word list format
  # [0:(Found status:True/False),1:(Tile_x coordinate),2:(Tile_y coordinate), 3:(orientation: 1 vertical, 2 horizontal), 4:(score), 5:("word text")]

  test_word       = []
  found_words     = []
  high_score_word = [False,0,0,0,0,""]
  word_count = 0

  VERTICAL   = 1 
  HORIZONTAL = 2
  
  print("AL is playing: ")
  number_of_words_in_offical_list = len (offical_words_list)

  start_milliseconds = int(time.time() * 1000)
  update_server_timer = time.time()
  wpm_rate_start = time.time()

  gb = copy.deepcopy(WW_GAMEBOARD_WORDS)
  db = copy.deepcopy(WW_DIRTY_GAMEBOARD)   

  #process all the good words
  for word in offical_words_list:
    word_count += 1
    if (word_count % 1000 == 0):
      wpm_rate_end = time.time()
      delta_time = wpm_rate_end - wpm_rate_start
      wpm_rate_start = time.time()
      rate = (1000/delta_time)*60 #words per minute
      ttc = (number_of_words_in_offical_list - word_count)/rate
      print("Word count: ", word_count," out of: ",number_of_words_in_offical_list," words, rate[WPM]: ", rate, " Time to complete[m]: ", ttc)
    
    try_word = word.upper()

    for x in range(0,15):
      for y in range(0,15):
        #print("NS placement: (",x,",",y,")")
       
        test_word = try_NS_word(gb,db,x,y,try_word)
        #print("before: ", x,y,try_word)
        #print(gb)
        #print(db)
        clear_tried_letter(gb,db,x,y,VERTICAL)
        #print("after")
        #print(gb)
        #print(db)
        
        if (test_word[0] == True): #found a good word location on the GAMEBOARD
          found_words.append(test_word)
          #print("Found NS word: ", test_word)
      
        test_word = try_WE_word(gb,db,x,y,try_word)
        clear_tried_letter(gb,db,x,y,HORIZONTAL)

        if (test_word[0] == True): #found a good word location on the GAMEBOARD
          found_words.append(test_word)
          #print("Found WE word: ",test_word)

        update_server_timer_current_time = time.time()
        if (update_server_timer_current_time - update_server_timer > 1):
          WW_client_send_game_data_to_server()
          WW_client_request_game_data_from_server_lite()
          update_server_timer = time.time()
          #print("AL updated server: ",time.time())

  print("Found words list: ", found_words)  
  #Find the most valuable word
  high_score = 0
  for word_test in found_words:
    if word_test[4] > high_score:
      high_score_word = word_test
      high_score = word_test[4]
  print("high_score_word: ", high_score_word)

  #Put the new highscore word on the gameboard
  if (high_score_word[0] == True):
    place_word(high_score_word)
    print ("Als loop: Placed high_score_word: ", high_score_word)
  else:
    print("No word to place")

  end_milliseconds = int(time.time() * 1000)
  print("Al completed hand, processing time: ", (end_milliseconds - start_milliseconds)/1000)

def clear_tried_letter (gb,db,x,y,direction):
  VERTICAL   = 1 
  HORIZONTAL = 2

  if direction == HORIZONTAL:
    for i in range (x,15):
      if db[y][i] == '1':
        gb[y][i] = '#'
        db[y][i] = '#'

  if direction == VERTICAL:
    for j in range (y,15):
      if db[j][x] == '1':
        gb[j][x] = '#'
        db[j][x] = '#' 

def try_WE_word (gb,db,x,y,word_to_try):
  used_at_least_one_tile = False

  #print("test WE word: ", word_to_try, x, y)
  hand_copy = get_my_hand()
  #print("Hand_copy: ",hand_copy) 

  #If the word will not fit W to E then return False
  WE_x = x
  for letter in word_to_try:
    letter_works = False
    #Check if the edge of the baord is hit
    if WE_x >= 15:
      return(False,0,0,0,0,"")

    #Check that the westside of the word placement is blank
    if (x > 0):
      if gb[y][x-1] != '#':
        return [False,0,0,0,0,""]

    if gb[y][WE_x] == letter: #an existing letter lines up with our word
      WE_x  += 1
      letter_works = True
      #print("try_WE existing letter used: ",letter,WE_x,y)
    #If the spot didn't have the letter we needed and the space is not empty then return False
    elif (gb[y][WE_x] != '#'):
      return [False,0,0,0,0,""]
    else:
      for i in range(0,len(hand_copy)):
        if hand_copy[i] == letter: #if the letter is in our hand then use it on the gb board
          gb[y][WE_x] = letter
          db[y][WE_x] = '1' 
          hand_copy[i] = '#'
          used_at_least_one_tile = True
          letter_works = True
          #print("try_WE_word letter placed: ", letter,WE_x,y)
          WE_x += 1
          break
        #handle blank tiles
        elif (hand_copy[i] == ' ' and hand_does_not_contain(hand_copy,letter)):
          gb[y][WE_x] = letter.lower() #Place the lower case modified blank tile
          db[y][WE_x] = '1' 
          hand_copy[i] = '#'
          used_at_least_one_tile = True
          letter_works = True
          #print("try_WE_word letter placed with lower case blank type tile: ", letter.lower(),WE_x,y)
          WE_x += 1
          break

    if (letter_works == False):
      #print("could not fit WE word: ",word_to_try)
      return [False,0,0,0,0,""]

  #Check the eastside of the word to make sure it has a gap space
  if (WE_x <= 14):
    if gb[y][WE_x] != '#':
      return [False,0,0,0,0,""]

  if(NS_words_ok(gb,db,x,y,word_to_try) and used_at_least_one_tile):
    #print("NS_word_ok == True")
    score = calculate_score(gb,db)
    #print("Score for word: ", score)
    return [True,x,y,2,score,word_to_try]

  return [False,0,0,0,0,""]

def NS_words_ok(gb,db,x,y,word):
  #print("testing NS_word: ",word," starting at: ",x,y)

  new_word_connected_to_old_tile = False

  for i in range (x,x+len(word)):
    test_word = ""
    north_index = y
    for j in range (y,-1,-1):
      if gb[j][i] != '#':
        north_index = j
      else:
        break

    south_index = y
    for j in range (y,15):
      if gb[j][i] != '#':
        south_index = j 
      else:
        break

    if (south_index - north_index >= 1):
      new_word_connected_to_old_tile = True
      #test the found WE word
      for word_y in range (north_index,south_index+1):
        test_word += gb[word_y][i]

      #Check the found WE cross word is bad.  If so return False
      if (is_word(test_word) == False):
        #print("NS test word bad: ",test_word)
        return(False)
      #else:
        #print("NS test word good: ",test_word)

  if (new_word_connected_to_old_tile == True):
    #print("WE Word placed well and connected")
    return(True)
  else:
    return(False)

def hand_does_not_contain(hand, letter):
  for i in range (0,7):
    if (hand[i] == letter):
      return False 
  return True

def try_NS_word (gb,db,x,y,word_to_try):
  used_at_least_one_tile = False
  found_center_tile = False

  #print("test NS word: ", word_to_try, x, y)
  hand_copy = get_my_hand()
  #print("Hand_copy: ",hand_copy)

  #If the word will not fit W to E then return False
  NS_y = y
  for letter in word_to_try:
    letter_works = False
    
    #Check if the edge of the baord is hit
    if NS_y >= 15:
      return(False,0,0,0,0,"")

    #Check that the northside of the word placement is blank
    if (y > 0):
      if gb[y-1][x] != '#':
        return [False,0,0,0,0,""]

    if gb[NS_y][x] == letter: #an existing letter lines up with our word
      NS_y += 1
      letter_works = True
      #print("try_NS_word found existing needed tile: ",letter,x,NS_y)
    elif (gb[NS_y][x] != '#'):
      return [False,0,0,0,0,""]
    else:
      for i in range(0,len(hand_copy)):
        if hand_copy[i] == letter: #if the letter is in our hand and the then use it on the gb board
          if (NS_y == 7 and x == 7 and gb[NS_y][x] == '#'): #found cetner spot
            found_center_tile = True
          gb[NS_y][x] = letter 
          db[NS_y][x] = '1'
          hand_copy[i] = '#'
          used_at_least_one_tile = True
          letter_works = True
          #print("try_NS_word letter placed: ", letter,x,NS_y)
          NS_y += 1
          break
        #handle blank tiles
        elif (hand_copy[i] == ' ' and hand_does_not_contain(hand_copy,letter)):
          gb[NS_y][x] = letter.lower()
          db[NS_y][x] = '1'
          hand_copy[i] = '#'
          used_at_least_one_tile = True
          letter_works = True
          #print("try_NS_word letter placed blank type lower case tile: ", letter,x,NS_y)
          NS_y += 1
          break

    if (letter_works == False):
      #print("could not fit NS word: ",word_to_try)
      return [False,0,0,0,0,""]

  #Check the southside of the word to make sure it has a gap space
  if (NS_y <= 14):
    if gb[NS_y][x] != '#':
      return [False,0,0,0,0,""]

  if(found_center_tile):
    score = calculate_score(gb,db)
    return [True,x,y,1,score,word_to_try]

  if(WE_words_ok(gb,db,x,y,word_to_try) and used_at_least_one_tile):
    #print("WE_words_ok == True")
    score = calculate_score(gb,db)
    #print("Score for word: ", score)
    return [True,x,y,1,score,word_to_try]

  return [False,0,0,0,0,""]

def WE_words_ok(gb,db,x,y,word):
  #print("Testing WE_word_ok: ",word,x,y)
  new_word_connected_to_old_tile = False

  #print("testing WE_word: ",word," starting at: ",x,y)
  for i in range (y,y+len(word)):
    test_word = ""
    west_index = x
    for j in range (x,-1,-1):
      if gb[i][j] != '#':
        west_index = j
      else:
        break

    east_index = x
    for j in range (x,15):
      if gb[i][j] != '#':
        east_index = j 
      else:
        break

    if (east_index - west_index >= 1):
      new_word_connected_to_old_tile = True
      #test the found WE word
      for word_x in range (west_index,east_index+1):
        test_word += gb[i][word_x]

      #Check the found WE cross word is bad.  If so return False
      if (is_word(test_word) == False):
        #print("WE test word bad: ",test_word,"east index: ",east_index," west index: ", west_index,"x y: ",x,y)
        return(False)
      #else:
        #print("WE test word good: ",test_word)

  if (new_word_connected_to_old_tile == True):
    #print("NS Word placed well and connected")
    return(True)
  else:
    return(False)

def place_word (high_score_word):
  # word list format
  # [0:(Found status:True/False),1:(Tile_x coordinate),2:(Tile_y coordinate), 3:(orientation: 1 vertical, 2 horizontal), 4:(score), 5:("word text")]

  global WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD

  VERTICAL   = 1 
  HORIZONTAL = 2

  my_hand = get_my_hand()
  #print("place_word: my_hand: ", my_hand)

  #print("high_score_word: ", high_score_word)

  x           = high_score_word[1]
  y           = high_score_word[2]
  orientation = high_score_word[3]
  word        = high_score_word[5]

  hand_index = 0
  if (orientation == VERTICAL):
    #print("place_word: placing vertical word")
    NS_y = y
    if (NS_y >= 15):
      print("Error in place_word out of bounds word placement index NS_y: ", x, NS_y)
      exit(1)
    for letter in word:
      if WW_GAMEBOARD_WORDS[NS_y][x] == letter:
        #print("place_letter: using existing letter: ", letter, "at: ",x,NS_y)
        NS_y += 1

      else:
        if WW_GAMEBOARD_WORDS[NS_y][x] == '#':
          #print("Placing vertical letter: ", letter, "at: ", x, NS_y)
          WW_GAMEBOARD_WORDS[NS_y][x] = letter
          WW_DIRTY_GAMEBOARD[NS_y][x] = '1'

          #find the letter in the hand and erase it
          found_letter_in_hand = False
          for i in range (0,7):
            if (my_hand[i] == letter):
              my_hand[i] = '#'
              found_letter_in_hand = True
              break
          if (found_letter_in_hand == False): #must be a blank tile
            WW_GAMEBOARD_WORDS[NS_y][x] = letter.lower()
            for i in range (0,7):
              if (my_hand[i] == ' '):
                my_hand[i] = '#'
                break
          NS_y += 1
    
  if (orientation == HORIZONTAL):
    #print("place_word: placing horizontal word")
    WE_x = x
    if (WE_x >= 15):
      print("Error in place_word out of bounds word placement index WE_x: ", WE_x,y)
      exit(1)
    for letter in word:
      if WW_GAMEBOARD_WORDS[y][WE_x] == letter:
        #print("place word horizontal using existing letter: ",letter, "at: ",WE_x,y)
        WE_x += 1

      else:
        if WW_GAMEBOARD_WORDS[y][WE_x] == '#':
          #print("Placing horizontal letter: ", letter," at: ",WE_x,y)
          WW_GAMEBOARD_WORDS[y][WE_x] = letter
          WW_DIRTY_GAMEBOARD[y][WE_x] = '1'

          found_letter_in_hand = False
          for i in range (0,7):
            if (my_hand[i] == letter):
              my_hand[i] = '#'
              found_letter_in_hand = True
              break
          if (found_letter_in_hand == False): #must be a blank tile
            WW_GAMEBOARD_WORDS[y][WE_x] = letter.lower()
            for i in range (0,7):
              if (my_hand[i] == ' '):
                my_hand[i] = '#'
                break
          WE_x += 1
  
  print("place word: new hand: ", my_hand)
  set_my_hand(my_hand)



#   _____          __  __ _______  _      ____   ____  _____
#  / ____|   /\   |  \/  |  ____| | |    / __ \ / __ \|  __ \ 
# | |  __   /  \  | \  / | |__    | |   | |  | | |  | | |__) |
# | | |_ | / /\ \ | |\/| |  __|   | |   | |  | | |  | |  ___/ 
# | |__| |/ ____ \| |  | | |____  | |___| |__| | |__| | |     
#  \_____/_/    \_\_|  |_|______| |______\____/ \____/|_|                                                                
                                                             
#reset game and get ready to run
pygame.mouse.set_visible(True)

start_time = time.time()
run = True 
gameover = False
new_game = True 

definition_popup = False

display_help_screen = False
display_two_word_list = False
display_tile_values_list = False 
display_chat_box = False 

card_display = "NONE"

test_count = 0

retry_connect = 4

#print(f"Creating socket host: {addr}, port: {port}")
client_socket = None
#RobustSocketClient(addr,port)

while run:

  while (new_game == True):
    WW_register_with_server()

  elapsed_time = time.time()

  #Set the game title to include the current player
  updated_title_string = title_string + "(" + WW_Client_player + ")"
  pygame.display.set_caption(updated_title_string)

  #update background
  screen.fill(BLACK)

  #Draw Background (which is a sprite)
  drawbackground(screen)

  #Add the text tiles
  gameboard_update(screen)

  #Update the players hands on the screen
  #Put both hands on the screen for now.
  hand_mouse_drag_update(screen)

  #Update the scores and who's turn it is
  show_turn_scores_go_button(screen)

  #Update number of tiles
  tile_pile_update(screen)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

    if event.type == pygame.MOUSEBUTTONDOWN:
      if (event.button == 1): # Detect left button down
        pos = pygame.mouse.get_pos()

        #Detect if the plyaer is clicking on a player card to get the player data
        card_display = player_card_clicked(pos)

        #Check the played word with the dictionary
        dictionary_button_check()

        # Check for click on AL-enable button (and the user is not dragging a tile)
        if (selected_tile_letter == '#' and click_area(pos,X_OFFSET+(15*40),Y_OFFSET+(13*40),X_OFFSET+(16*40),Y_OFFSET+(14*40))):
          WW_Set_AL_Fairness()
          WW_Client_toggleAL()

        #If the player clicks on the chat box then turn on the chat screen
        if (chat_button_pressed(pos)):
          display_chat_box = not display_chat_box
          
        #Check if changing players who control the board
        if (go_button_click(pos) == True):
          go_button_clicked = True # turn off the button
          
          #Check gameover
          #check_gameover()

          #Calculate new word score and add it to player's score
          score_word(WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD)
          #Turn new character dirty bits to locked bits ones to zeros
          lock_word()
          player_swap_refill_hand()
        else:
          if ismytile(pos) == True:
            #print("it's my tile")
            pickup = True
            pickup_tile(pos)

      if (event.button == 2): #Detect center click for definiton
        definition_popup = True

    if event.type == pygame.MOUSEBUTTONUP:
      pos = pygame.mouse.get_pos()
  
      #Detect if the plyaer is clicking on a player card to get the player data
      card_display = "NONE"

      if (event.button == 1): # wait for left button up.
        if (pickup == True):
          if (out_of_bounds(pos)):
            drop_tile_hand()
          else:
            drop_tile(pos)  
            #save_screen_capture() 
          pickup = False

        # # Check for click on AL-enable button (and the user is not dragging a tile)
        # if (selected_tile_letter == '#' and click_area(pos,X_OFFSET+(15*40),Y_OFFSET+(13*40),X_OFFSET+(16*40),Y_OFFSET+(14*40))):
        #   WW_Client_toggleAL()

      if (event.button == 2): #clear away definition pop up
        definition_popup = False

      #Detect right mouse click up to roll blanks
      if (event.button == 3): #Detect right click
        if (myturn()):
          roll_blank_tile(pos)
          toggle_hand_tile_for_exchange(pos)

    #Check for dictionary check with ALT keys (left or right)
    if event.type == pygame.KEYDOWN:
      if (event.key == pygame.K_LALT or event.key == pygame.K_RALT):
        definition_popup = True

    if event.type == pygame.KEYUP:
      if (event.key == pygame.K_LALT or event.key == pygame.K_RALT):
        definition_popup = False

    #toggle showing the help screen with F1 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F1):
        if display_help_screen == True:
          display_help_screen = False 
        else:
          display_help_screen = True

        if display_two_word_list == True:
          display_two_word_list = False 

        if display_tile_values_list == True:
          display_tile_values_list = False 

    #toggle showing the two letter screen with F2 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F2):
        display_two_word_list = not display_two_word_list
        display_help_screen = False
        display_tile_values_list = False

    #toggle showing the two letter screen with F2 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F3):
        display_tile_values_list = not display_tile_values_list
        display_two_word_list = False
        display_help_screen = False

    #toggle showing the two letter screen with F2 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F6):
        verbose = not verbose
        
    #toggle showing the two letter screen with F2 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL):
        print("Resetting game")
        new_game = True
        WW_client_send_game_over_to_server(True) # True = force game over
        reset_game()

    # *************************************************************
    # Support chat text entry

    #toggle showing the two letter screen with F2 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_BACKQUOTE):
        display_chat_box = not display_chat_box

    max_chat_text_length = 55

    if (display_chat_box == True):
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_RETURN:
          if len(chat_input) > 1:
            WW_Client_send_chat(chat_text_input)
            chat_input = ""
            WW_Client_get_chats()
        elif event.key == pygame.K_TAB:
          rotate_chat_recipient()

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
          chat_input = chat_input[:-1]
        else:
          ch = event.unicode
          if ((ch.isalnum() or ch == ' ' or ch == '@' or ch == "'" or ch == "\"" or ch == "_") and (len(chat_input) < max_chat_text_length)):
            chat_input += event.unicode
    # *************************************************************
    
    #toggle full screen
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F11):
        pygame.display.toggle_fullscreen()

    #See if player wants to quit
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_END):
        str1 = "PRESS 'ENTER' TO QUIT"
        str2 = "PRESS 'SPACE' TO GO BACK"
        if (generic_popup_box(X_OFFSET+(7*40),Y_OFFSET+(15*40),(10*40),60,str1,str2)):
          WW_client_leave_game(WW_Client_player)
          pygame.time.wait(3000)
          run = False

  #Sync server data ever 1 second
  if ((elapsed_time - start_time) >= 3):
    start_time = time.time()
    #If it's this clients turn then send game data to the server
    if (myturn()):
      go_button_clicked = False
      WW_client_send_game_data_to_server()
      if verbose:
        print("Active Player send data")
      WW_client_request_game_data_from_server_lite()
    else:
      #get the latest server data
      WW_client_request_game_data_from_server()
      if verbose:
        print(WW_Client_player," request game data from server")

    #If the bag is empty and this players hand is empty then set gameover = True. 
    #moved to be checked when Go is pressed
    check_gameover() 
    
    #Grab chats if they exist
    WW_Client_get_chats()

    #WW_Client_send_chat("Hey have you seen becky.  OMG she is like the smartest kid on the block. I can't believe it she bowled 300 and won the spelling bee in the same day.  OMG LOL brb have to pee. "+str(test_count)) 
    test_count+=1

  #print("*************** AL_percent_complete:", AL_percent_complete)

  #Process gameover if set by check_gameover()
  if gameover == True:
    for sync in range (6,0,-1):  #Sync 6 times with the sever at 500ms per sync cylces = 3sec's.  The server game data is sync'd ever 2sec's
      print("Gameover Sync: ",sync)
      score_word(WW_GAMEBOARD_WORDS,WW_DIRTY_GAMEBOARD)
      lock_word()
      WW_client_send_game_data_to_server()
      WW_client_request_game_data_from_server()
      print(WW_player1)
      print(WW_player2)
      print(WW_player3)
      print(WW_player4)
      pygame.time.wait(500)

    #update screen one more time
    pygame.time.wait(2000) #Wait 2s for last 1s player2 data to arrive
    screen.fill(BLACK)
    drawbackground(screen)
    gameboard_update(screen)
    show_turn_scores_go_button(screen)
    pygame.display.flip()
    
    #Clear out the players words in the game data.
    clear_current_player_last_word()

    #Take a snapshot
    save_screen_capture()

    #Show game over summary box
    str1 = "GAMEOVER:"
    str2 = "PRESS ANY KEY FOR NEW GAME"
    gameover_box(X_OFFSET+(7*40),Y_OFFSET+(15*40),(10*40),60,str1,str2)

    time.sleep(2) #Allow server to detect game over and reset the game data (bag)
    #WW_client_send_turn_over_command()
    print("Leaving the game")
    new_game = True #Start back over with the IP join game screen
    WW_client_send_game_over_to_server(False) #False = do not force game over

  #AL takes a turn if needed
  if (computer_player == True):
    if (myturn()):
      computer_player_takes_turn()
       #Calculate new word score and add it to player's score
      score_word(WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD)
      #Turn new character dirty bits to locked bits ones to zeros
      lock_word()
      player_swap_refill_hand()
    
  if (definition_popup == True):
    pos = pygame.mouse.get_pos()
    pop_up_definition(pos)

  if (display_help_screen):
    screen.blit(help_screen1, (0, 0))

  if (display_two_word_list):
    screen.blit(help_screen2, (0, 0))

  if (display_tile_values_list):
    screen.blit(help_screen3, (0, 0))

  if (display_chat_box):
    WW_chat_pop_up()

  #Display the player card data
  if (card_display != "NONE"):
    show_player_words(card_display)

  #update display
  pygame.display.flip()

pygame.quit()