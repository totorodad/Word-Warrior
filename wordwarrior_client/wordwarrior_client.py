# __          __           _  __          __             _            
# \ \        / /          | | \ \        / /            (_)           
#  \ \  /\  / /__  _ __ __| |  \ \  /\  / /_ _ _ __ _ __ _  ___  _ __ 
#   \ \/  \/ / _ \| '__/ _` |   \ \/  \/ / _` | '__| '__| |/ _ \| '__|
#    \  /\  / (_) | | | (_| |    \  /\  / (_| | |  | |  | | (_) | |   
#     \/  \/ \___/|_|  \__,_|     \/  \/ \__,_|_|  |_|  |_|\___/|_|   
#                                                                     
#                                                                     
# Big text generator used: https://www.fancytextpro.com/BigTextGenerator/Big
#
#wordwarrior_client.py (client only)
#word_warrior Rev 3.0 (Use with gameserver.py)
#Boulder Creek Video Games
#Jim Nolan and Family
#27-Oct-2024
#
#Dependancies:
# - Must install pygame
#
#Game Notes:
# - 4 players supported
# 
#
#TODO:
# - Add dictionary lookup for words
# 

# installed libraries:
# pip install pygame requests

import pygame # pip install pygame
import math,time,sys,random,pickle,socket,threading
import requests as req # pip install requests


port = 5000

hostname = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
addr = sock.getsockname()[0]

print("Your Computer Name is:", hostname)
print("Your Computer IP Address is:", addr)

game_server_address = addr 
print("Connect to gameserver on port: ", port)

#Get internet address.  Note this function is dependent on amazonaws
#After the Amazon corprate wars in 2082 this function may not work any
#more.
url:str = 'https://checkip.amazonaws.com'
request = req.get(url)
InternetIP:str = request.text
print("Your internet IP Address is:", InternetIP)

TILES_WIDTH  = 40
TILES_HEIGHT = 40

GAMEBOARD_X_TILES = 15
GAMEBOARD_Y_TILES = 15

WW_Client_player_last_score = 0
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
WW_player1 = {"player": "Player 1", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player2 = {"player": "Player 2", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player3 = {"player": "Player 3", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}
WW_player4 = {"player": "Player 4", "score": 0, "status": "notplaying", "hand": ['#','#','#','#','#','#','#']}

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

pygame.init()

#define screen size +1 for room on the size for game data.
SCREEN_WIDTH  = (GAMEBOARD_X_TILES + 1) * TILES_WIDTH  
SCREEN_HEIGHT = ((GAMEBOARD_Y_TILES + 2) * TILES_HEIGHT) - 20

HAND_PLAYER_GO_Y_OFFSET = 40 * 15 + 20

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Warrior Rev 2.0 - Boulder Creek Video Games - 2024")

#define colors
GREEN  = (0, 255, 0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
WHITE  = (255, 255, 255)
YELLOW = (255,255,0)
BLACK  = (0,0,0)
GRAY   = (200,200,200)

WW_font        = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 25)
WW_score_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 10)
WW_value_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 10)
WW_help_text_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 15)
font = pygame.font.Font(None, 30)

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
help_screen    = pygame.image.load("assets/imgs/help_screen.png").convert_alpha()
setup_screen   = pygame.image.load("assets/imgs/setup_screen.png").convert_alpha()

dictionary     = "assets/dictionary/Collins Scrabble Words (2019).txt"

def load_words(file_path):
  with open(file_path, 'r') as file:
    words = [line.strip() for line in file]
  print("Loaded: ",len(words)," words from the dictionary")
  return words

#Get the words to check spelling
dict_words = load_words(dictionary)

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

  if (mouse_x >= 0 and mouse_x <= (15*40) and mouse_y >= 0 and mouse_y <=(15*40)):
    tile_x = math.floor(mouse_x/40)
    tile_y = math.floor(mouse_y/40)

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
  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET

  mouse_x = pos[0]
  mouse_y = pos[1]
 
  #If tile is picked up from players hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    hand_position = math.floor(mouse_x/40)
 
    #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if hand_position > 6:
      hand_position = 6
    
    return (hand_position)
  else:
    return(-1)

def is_word(word):
  start_milliseconds = int(time.time() * 1000)
  if word.upper() in dict_words:
    delta_time = int(time.time() * 1000) - start_milliseconds
    #print("word found in: ", delta_time," ms")
    return True 
  else:
    delta_time = int(time.time() * 1000) - start_milliseconds
    #print("word not found in: ", delta_time," ms")
    return False

def test_dictionary_lookup():
  print("AAL is in dictionary? ", is_word ("aal"))
  print("BAAL is in dictionary? ", is_word ("baal"))
  print("PONY is in dictionary? ", is_word ("pony"))
  print("CANTANKEROUSLY is in dictionary? ", is_word ("CANTANKEROUSLY"))

def get_server_ip_address():
  global addr 

  font = pygame.font.Font(None, 32)
  clock = pygame.time.Clock()
  input_box = pygame.Rect(39, 220, 400, 32)
  color = pygame.Color(BLACK)
  active = True
  text = game_server_address

  pygame.event.clear()
  
  while True:
      # Render the background image
      img = setup_screen
      screen.blit(img, (0, 0))

      # Render the current text.
      txt_surface = font.render(text, True, color)
      # Resize the box if the text is too long.
      width = max(200, txt_surface.get_width()+10)
      input_box.w = width
      # Blit the text.
      screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
      # Blit the input_box rect.
      pygame.draw.rect(screen, color, input_box, 2)

      pygame.display.flip()

      for event in pygame.event.get(): #event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
          if active:
            if event.key == pygame.K_RETURN:
              print("Server hostname: ",text)
              addr = socket.gethostbyname(text)
              print("IP address: ", addr)
              return
            elif event.key == pygame.K_BACKSPACE:
              text = text[:-1]
            else:
              text += event.unicode

      clock.tick(30)

def dictionary_button_check():
  pos = pygame.mouse.get_pos()
  mouse_x = pos[0]
  mouse_y = pos[1]
  
  #Check that the user clicked on the button and also make sure it's their turn
  if (mouse_x >= (15*40) and mouse_y >= (14*40) and mouse_y < (15*40)):
    pygame.event.get()
    while(pygame.mouse.get_pressed()[0]):
      check_spelling()
      pygame.event.get()
  
def check_spelling():
  list_of_words = find_new_words()

  if (list_of_words == 0):
    print("No words found to check spelling on")
    return
  
  j = 0
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

        screen.blit(img,(j*fixed_tile.get_width(),i*fixed_tile.get_height()))

        good_tile = good_letter(list_of_words,j,i)

        #Don't render blank tile text
        if (tile != ' '):
          if (good_tile):
            font_img = WW_font.render(tile, True, BLACK)
          else:
            font_img = WW_font.render(tile, True, RED)
          
          if (tile.islower()):
            screen.blit(font_img,((j*fixed_tile.get_width())+13,(i*fixed_tile.get_height())+ 0))
          else:
            screen.blit(font_img,((j*fixed_tile.get_width())+10,(i*fixed_tile.get_height())+ 0))


        if(good_tile):
          font_value_img = WW_value_font.render(str(letter_value[tile]), True, BLACK)
        else:
          font_value_img = WW_value_font.render(str(letter_value[tile]), True, RED)
        screen.blit(font_value_img,((j*fixed_tile.get_width())+25,(i*fixed_tile.get_height())+ 25))

        pygame.display.flip()

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
      y_offset = words[i][2]
      #print(west_index,east_index,y_offset)
      if (x <= east_index and x >= west_index and y == y_offset and words[i][6] == 2):
        found_good_word = False
        #print ("WE word x:",x,"y:",y,":",WW_GAMEBOARD_WORDS[y][x],"G/B: ", found_good_word)

    #Check NS
    if (words[i][4] == 2):
      north_index = words[i][0]
      south_index = words[i][1]
      x_offset = words[i][3]
      if (y <=south_index and y >= north_index and x == x_offset and words[i][6] == 2):
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

def go_button_click(pos):
  global go_button_clicked

  mouse_x = pos[0]
  mouse_y = pos[1]

  #Check that the user clicked on the button and also make sure it's their turn
  if (mouse_x >= (15*40) and mouse_y >= HAND_PLAYER_GO_Y_OFFSET and mouse_y < HAND_PLAYER_GO_Y_OFFSET+40 and myturn() and go_button_clicked == False):
      go_button_clicked = True
      return (True)
  else:
      return (False)

#Count how many new tiles placed on the board
def count_new_tiles_played():
  count = 0
  for x in range (0,15):
    for y in range (0,15):
      if (WW_DIRTY_GAMEBOARD[y][x] == '1'):
        count +=1
  return (count)

#If there are 7 then the player used all their tiles
def all_tiles_played():
  if (count_new_tiles_played() == 7):
    return (True)
  else:
    return (False)

def drawbackground(screen):
  j = 0
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

      screen.blit(img,(j*img.get_width(),i*img.get_height()))

      #Draw myturn icon
      if (myturn()):
        img = myturn_icon
        screen.blit(img,((7*40),(15*40)))

      #Draw help screen text
      help_text_surface = WW_help_text_font.render("PRESS F1 FOR HELP", True, WHITE)
      screen.blit(help_text_surface, (10*40,15*40))   

def gameboard_update(screen):
  j = 0
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

        screen.blit(img,(j*fixed_tile.get_width(),i*fixed_tile.get_height()))

        #Don't render blank tile text
        if (tile != ' '):
          font_img = WW_font.render(tile, True, BLACK)
          if (tile.islower()):
            screen.blit(font_img,((j*fixed_tile.get_width())+13,(i*fixed_tile.get_height())+ 0))
          else:
            screen.blit(font_img,((j*fixed_tile.get_width())+10,(i*fixed_tile.get_height())+ 0))

        font_value_img = WW_value_font.render(str(letter_value[tile]), True, BLACK)
        screen.blit(font_value_img,((j*fixed_tile.get_width())+25,(i*fixed_tile.get_height())+ 25))

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

  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET

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
    x = x + blank_tile1.get_width()
    
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

  x = 15*40
  img = blank_tile1 

  for y in range(1, number_of_tiles+1):
    screen.blit(img,(x,5*y))

  bag_count_img = WW_value_font.render(str(number_of_tiles), True, BLACK)
  screen.blit(bag_count_img,(x+10,(5*y)+7))
  count_img     = WW_value_font.render("LEFT",True, BLACK)
  screen.blit(count_img,(x+8,(5*y)+12+10))

def show_turn_scores_go_button(screen):
  p1_score = WW_player1["score"]
  p2_score = WW_player2["score"]
  p3_score = WW_player3["score"]
  p4_score = WW_player4["score"]
  
  y_offset = HAND_PLAYER_GO_Y_OFFSET
  score_text_y_offset_p1 = (10*40) + 12
  score_text_y_offset_p2 = (11*40) + 12
  score_text_y_offset_p3 = (12*40) + 12
  score_text_y_offset_p4 = (13*40) + 12
  

  #Draw palyer1 Name and score tile, score is '---' = nonplaying player)
  if (WW_player1["status"] == "playing"):
    img = blank_tile1
    screen.blit(img, (10*40,y_offset))
    player_name_img = WW_score_font.render("Player 1", True, BLACK)
    screen.blit(player_name_img,( (10*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render(str(p1_score), True, BLACK)
    screen.blit(score_img,( score_text_y_offset_p1, (y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (10*40,y_offset))
    player_name_img = WW_score_font.render("Player 1", True, WHITE)
    screen.blit(player_name_img,( (10*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_y_offset_p1, (y_offset)+16) )

  #Draw palyer2 Name and score tile, score is '---' = nonplaying player)
  if (WW_player2["status"] == "playing"):
    img = blank_tile2
    screen.blit(img, (11*40,y_offset))
    player_name_img = WW_score_font.render("Player 2", True, BLACK)
    screen.blit(player_name_img,( (11*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render(str(p2_score), True, BLACK)
    screen.blit(score_img,( score_text_y_offset_p2, (y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (11*40,y_offset))
    player_name_img = WW_score_font.render("Player 2", True, WHITE)
    screen.blit(player_name_img,( (11*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_y_offset_p2, (y_offset)+16) )

  #Draw palyer3 Name and score tile, score is '---' = nonplaying player)
  if (WW_player3["status"] == "playing"):
    img = blank_tile3
    screen.blit(img, (12*40,y_offset))
    player_name_img = WW_score_font.render("Player 3", True, BLACK)
    screen.blit(player_name_img,( (12*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render(str(p3_score), True, BLACK)
    screen.blit(score_img,( score_text_y_offset_p3, (y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (12*40,y_offset))
    player_name_img = WW_score_font.render("Player 3", True, WHITE)
    screen.blit(player_name_img,( (12*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_y_offset_p3, (y_offset)+16) )

  #Draw palyer3 Name and score tile, score is '---' = nonplaying player)
  if (WW_player4["status"] == "playing"):
    img = blank_tile4
    screen.blit(img, (13*40,y_offset))
    player_name_img = WW_score_font.render("Player 4", True, BLACK)
    screen.blit(player_name_img,( (13*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render(str(p4_score), True, BLACK)
    screen.blit(score_img,( score_text_y_offset_p4, (y_offset)+16) )
  else:
    img = grey_tile
    screen.blit(img, (13*40,y_offset))
    player_name_img = WW_score_font.render("Player 4", True, WHITE)
    screen.blit(player_name_img,( (13*40)+2,(y_offset)+3) )
    score_img = WW_score_font.render("----", True, WHITE)
    screen.blit(score_img,( score_text_y_offset_p4, (y_offset)+16) )

  #draw go button
  if (myturn() and go_button_clicked == False):
    img = go_tile # allow the user to press the go button when they finished their turn
  else:
    img = wait_tile # let the player know the other player is working on their word.
  screen.blit(img,(15*40,y_offset))

  #draw dictionary button
  img = dictonary_icon # let the player know the other player is working on their word.
  screen.blit(img,(15*40,14*40))

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

  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET

  mouse_x = pos[0]
  mouse_y = pos[1]
 
  hand = get_my_hand()

  #If tile is picked up from players hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    hand_position = math.floor(mouse_x/40)

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
  if (mouse_x >= 0 and mouse_x <= (15*40) and mouse_y >= 0 and mouse_y <=(15*40)):
    tile_x = math.floor(mouse_x/40)
    tile_y = math.floor(mouse_y/40)

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

  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET
  
  mouse_x = pos[0]
  mouse_y = pos[1]

  successful_insert = False

  hand = get_my_hand()

  # Check for drop in new positon of hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    drop_tile_hand_location = math.floor(mouse_x/40)

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
  if (mouse_x >= 0 and mouse_x <= (15*40) and mouse_y >= 0 and mouse_y <=(15*40)):
    tile_x = math.floor(mouse_x/40)
    tile_y = math.floor(mouse_y/40)

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
  
#Handle swaping the player who controls the board
def player_swap_refill_hand():
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
  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET

  global player

  mouse_x = pos[0]
  mouse_y = pos[1]

  #Check if clicking in our hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    return (True)

  #Check if clicking the gameboard (make sure it's our tile)
  if (mouse_x >= 0 and mouse_x <= (15*40) and mouse_y >= 0 and mouse_y <=(15*40)):
    tile_x = math.floor(mouse_x/40)
    tile_y = math.floor(mouse_y/40)

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
  x = 0
  y = HAND_PLAYER_GO_Y_OFFSET

  global player

  mouse_x = pos[0]
  mouse_y = pos[1]

  #If dragging on the hand then not out of bounds
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    return (False)

  #If dragging over game board then not out of bounds
  if (mouse_x >= 0 and mouse_x <= (15*40) and mouse_y >= 0 and mouse_y <=(15*40)):
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
  
def score_west_east_word(start_x,start_y):
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
    if (WW_GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((WW_GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and WW_DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 2

    if WW_GAMEBOARD_WORDS[y][x] == '#':
      west_most_tile_x = x+1
      break
    if x==0: #found the west edge of the board
      west_most_tile_x = 0

  for x in range (start_x,15): # look at the tiles east of the new tile for the end of the word

    #Check for tripple word or double word multiplier under a new tile
    if (WW_GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and WW_DIRTY_GAMEBOARD[y][x] == '1' and x != start_x):
        word_multiplier *= 3
      #Look for double multiplier
      if ((WW_GAMEBOARD[y][x] == '5' or WW_GAMEBOARD[y][x] == '0') and WW_DIRTY_GAMEBOARD[y][x] == '1' and x != start_x):
        word_multiplier *= 2

    if WW_GAMEBOARD_WORDS[y][x] == "#":
      east_most_tile_x = x-1
      break
    if x==14:
      east_most_tile_x = 14 #found the east edge of the board 

  #Sum up the values of the WE root word
  for x in range (west_most_tile_x, east_most_tile_x+1):
    #Check for double letter
    if (WW_GAMEBOARD[y][x] == '2' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
      score += 2*(letter_value[WW_GAMEBOARD_WORDS[y][x]])

    #Check for tripple letter
    elif (WW_GAMEBOARD[y][x] == '3' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
      score += 3*(letter_value[WW_GAMEBOARD_WORDS[y][x]])

    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[WW_GAMEBOARD_WORDS[y][x]]

  #Factor in word multiplier
  score *= word_multiplier

  return (score)

def score_north_south_word(start_x,start_y):
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
    if (WW_GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((WW_GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and WW_DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 2

    if WW_GAMEBOARD_WORDS[y][x] == '#':
      north_most_tile_y = y+1
      break
    if y==0: #found the north edge of the board
      north_most_tile_y = 0

  for y in range (start_y,15): # look at the tiles east of the new tile for the end of the word
    #Check for tripple word or double word multiplier under a new tile
    if (WW_GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (WW_GAMEBOARD[y][x] == '4' and WW_DIRTY_GAMEBOARD[y][x] == '1' and y != start_y):
        word_multiplier *= 3
      #Look for double multiplier
      if ((WW_GAMEBOARD[y][x] == '5' or WW_GAMEBOARD[y][x] == '0') and WW_DIRTY_GAMEBOARD[y][x] == '1' and y != start_y):
        word_multiplier *= 2

    if WW_GAMEBOARD_WORDS[y][x] == "#":
      south_most_tile_y = y-1
      break
    if y==14:
      south_most_tile_y = 14 #found the south edge of the board 

  #print ("north most: ",north_most_tile_y," south most: ",south_most_tile_y)
  #Sum up the values of the NS root word
  for y in range (north_most_tile_y, south_most_tile_y+1):
    
    #Check for double letter
    if (WW_GAMEBOARD[y][x] == '2' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
      score += 2*(letter_value[WW_GAMEBOARD_WORDS[y][x]])
    
    #Check for tripple letter
    elif (WW_GAMEBOARD[y][x] == '3' and WW_DIRTY_GAMEBOARD[y][x] == '1'):
      score += 3*(letter_value[WW_GAMEBOARD_WORDS[y][x]])
    
    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[WW_GAMEBOARD_WORDS[y][x]]
  
  #Factor in word multiplier
  score *= word_multiplier

  return(score)

def detect_west_east_word (x,y):
  #check west and east of tile at x,y to see if there is a word
  if (x-1>=0):
    if (WW_GAMEBOARD_WORDS[y][x-1] != '#'):
      return(True) #found letter to the west of the first new tile
  if (x+1<=14):
    if (WW_GAMEBOARD_WORDS[y][x+1] != '#'):
      return(True)
  return(False)

def detect_north_south_word (x,y):
  #check north and south of tile at x,y to see if there is a word
  if (y-1>=0):
    if (WW_GAMEBOARD_WORDS[y-1][x] != '#'):
      return(True) #found letter to the north of the first new tile
  if (y+1<=14):
    if (WW_GAMEBOARD_WORDS[y+1][x] != '#'):
      return(True) #Found letter to the south of the first new tile
  return (False)

def score_word ():
  x = 0
  y = 0
  global WW_Client_player
  player_score = 0
  global WW_Client_player_last_score

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
      if (WW_DIRTY_GAMEBOARD[y][x] == '1'):
        new_tiles [number_of_new_tiles][0] = WW_GAMEBOARD_WORDS[y][x]
        new_tiles [number_of_new_tiles][1] = x 
        new_tiles [number_of_new_tiles][2] = y
        new_tiles [number_of_new_tiles][3] = WW_GAMEBOARD[y][x] #tile type aka multipler

        number_of_new_tiles += 1 

  #print(new_tiles)
  if (number_of_new_tiles == 0):
    #print("Whoops no new tiles found")
    return

  #location of the root tile (most north west tile)
  x = new_tiles[0][1] #first new tile x coordinate
  y = new_tiles[0][2] #first new tile y coordinate

  #Score root word WE and NS if there are words formed in those directions
  if (detect_north_south_word(x,y)):
    player_score += score_north_south_word(x,y)
    #print("NS word found at root. Player score = ",player_score)
  if (detect_west_east_word(x,y)):
    #print("WE word found at root. Player score = ", player_score)
    player_score += score_west_east_word(x,y)

  #Scan along the new tiles (but not the root tile which was already scored) for new words made and count their score
  if (new_tiles[1][0] != '#'): #Check if there is only one new tile
    print("more than a single character word")
    for i in range (1,14):
      if (new_tiles[i][0] != '#'):
        x = new_tiles[i][1]
        y = new_tiles[i][2]
        if (new_tiles[0][1] == new_tiles[1][1]): # A north south word (x's are the same)
          if(detect_west_east_word(x,y)):
            #print("added WE word score for root tile: ", new_tiles[i][0])
            player_score += score_west_east_word(x,y)
        else:
          if(detect_north_south_word(x,y)):
            #print("added NS word score for root tile: ", new_tiles[i][0])
            player_score += score_north_south_word(x,y)
  
  if (all_tiles_played()):
    player_score += 50 #Add the 50 point bonus for playing all tiles

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

  WW_Client_player_last_score = player_score

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
    return (WW_player1["hand"])
  elif (WW_Client_player == "Player 2"):
    return (WW_player2["hand"])
  elif (WW_Client_player == "Player 3"):
    return (WW_player3["hand"])
  elif (WW_Client_player == "Player 4"):
    return (WW_player4["hand"])
  else:
    print("Error: WW_Client_player not set properly, it's set to:", WW_Client_player)
    exit()

def set_my_hand (hand):
  global WW_player1, WW_player2, WW_player3, WW_player4

  if (WW_Client_player == "Player 1"):
    WW_player1["hand"] = hand
  elif (WW_Client_player == "Player 2"):
    WW_player2["hand"] = hand
  elif (WW_Client_player == "Player 3"):
    WW_player3["hand"] = hand
  elif (WW_Client_player == "Player 4"):
    WW_player4["hand"] = hand

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
  global WW_Client_player_last_score
  global selected_tile_letter
  
  #Reset the gameboard trackers
  for x in range(0,15):
    for y in range (0,15):
      WW_GAMEBOARD_WORDS[y][x] = '#'
      WW_DIRTY_GAMEBOARD[y][x] = '#'

  set_my_score(0)
  set_my_hand(['#','#','#','#','#','#','#'])

  WW_Client_player_last_score = 0

  selected_tile_letter = '#' # = no tile selected
  
  #Ensure server has this plyers latest game data
  #WW_client_send_game_over_to_server()
  WW_client_request_game_data_from_server()
  
  gameover = False
  run = True
  pickup = False

#  _   _ ______ _________          ______  _____  _  _______ _   _  _____ 
# | \ | |  ____|__   __\ \        / / __ \|  __ \| |/ /_   _| \ | |/ ____|
# |  \| | |__     | |   \ \  /\  / / |  | | |__) | ' /  | | |  \| | |  __ 
# | . ` |  __|    | |    \ \/  \/ /| |  | |  _  /|  <   | | | . ` | | |_ |
# | |\  | |____   | |     \  /\  / | |__| | | \ \| . \ _| |_| |\  | |__| |
# |_| \_|______|  |_|      \/  \/   \____/|_|  \_\_|\_\_____|_| \_|\_____|

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
    if (WW_Client_player == "Player 1"):
      server_socket.sendall(b'ww_reqsdat1')
    elif (WW_Client_player == "Player 2"):
      server_socket.sendall(b'ww_reqsdat2')
    elif (WW_Client_player == "Player 3"):
      server_socket.sendall(b'ww_reqsdat3')      
    elif (WW_Client_player == "Player 4"):
      server_socket.sendall(b'ww_reqsdat4')
    else:
      print("WW_Client_player not set.  Current setting is: ", WW_Client_player)
      exit(1)

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
  if (WW_Client_player != "Player 2"):
    WW_player2 = d4
  if (WW_Client_player != "Player 3"):
    WW_player3 = d5
  if (WW_Client_player != "Player 4"):
    WW_player4 = d6
    
  WW_bag = d7
  WW_player_last_score = d8

  WW_active_player = d9

def WW_client_request_game_data_from_server_lite():
  global addr, port

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
      server_socket.connect((addr,port))
      server_socket.sendall(b'ww_reqslite')

      #Receive the game data from server
      WW_client_request_game_data_from_server_receive_data_lite(server_socket)
      server_socket.close()  

def WW_client_request_game_data_from_server_receive_data_lite(client_socket):
  global WW_player1,WW_player2,WW_player3,WW_player4,WW_bag,WW_active_player
  
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

  # Note that in the lite version of this we only use:
  # d3 = WW_player1
  # d4 = WW_player2
  # d5 = WW_player3
  # d6 = WW_player4
  # d7 = WW_bag

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
      print(" Sent Player 1 data to Server")
    elif (WW_Client_player == "Player 2"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player2, WW_player_last_score)
      print(" Sent Player 2 data to Server")
    elif (WW_Client_player == "Player 3"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player3, WW_player_last_score)
      print(" Sent Player 3 data to Server")
    elif (WW_Client_player == "Player 4"):
      WW_client_send_game_data_to_server_send_data(client_socket, WW_GAMEBOARD_WORDS, WW_DIRTY_GAMEBOARD, WW_player4, WW_player_last_score)
      print(" Sent Player 4 data to Server")
    else:
      print("WW_Client_player not set properly in WW_client_send_game_data_to_server")
      exit(1)

    client_socket.close()
def WW_client_send_game_data_to_server_send_data(client_socket,d1,d2,d3,d4):
  # Serialize the data
  data = pickle.dumps((d1,d2,d3,d4))

  # Send the length of the pickled data payload as a header
  size = len(data).to_bytes(4, 'big')
  client_socket.sendall(size)
  
  # Send the pickled data payload
  client_socket.sendall(data)

def WW_client_send_game_over_to_server():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((addr,port))
    #Ask server to accept pickled game data
    client_socket.sendall(b'ww_gameover')
    client_socket.close()
    print("================> Client sent gameover <=================")

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
      print(" Send command for: ", WW_player_name," to leave the game")
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

def WW_client_refill_hand(player):
  global addr, port

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
      server_socket.connect((addr,port))
      #Send the request to refill players hand
      server_socket.sendall(b'ww_reflhand')

      #Send the player name to refill
      # Serialize the data
      data = pickle.dumps((player))

      # Send the length of the pickled data payload as a header
      size = len(data).to_bytes(4, 'big')
      server_socket.sendall(size)
      
      # Send the pickled data payload
      server_socket.sendall(data)

      #Receive the game data from server
      WW_client_refill_hand_receive_data(player, server_socket)
      server_socket.close() 
def WW_client_refill_hand_receive_data(player, client_socket):
  global WW_player1,WW_player2,WW_player3,WW_player4
  
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

  player_library = d1
 
  #Decode which refilled player library was returned and store it in our local player library
  if (player_library["player"] == "Player 1"):
    WW_player1 = d1
  elif (player_library["player"] == "Player 2"):
    WW_player2 = d1
  elif (player_library["player"] == "Player 3"):
    WW_player3 = d1
  elif (player_library["player"] == "Player 4"):
    WW_player4 = d1
  else:
    print ("Error: server returned invalid player refill name")
    exit()

def WW_client_request_gameover_status():
  #Send request to server to ask if a gameover was sent to the server
  #answer = True or False

  global addr, port

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.connect((addr,port))
    #Send the request to refill players hand
    server_socket.sendall(b'ww_reqgmovr')
    
    # Receive the size of the pickled data
    data_size = int.from_bytes(server_socket.recv(4), 'big')

    # Receive the pickled data
    data = b''
    while len(data) < data_size:
        packet = server_socket.recv(4096)
        if not packet:
            break
        data += packet

    # Deserialize the data
    d1 = pickle.loads(data)

    server_socket.close() 

  return(d1)

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

display_help_screen = False

def register_with_server():
  global start_time, run, gameover, new_game, WW_Client_player
  global WW_player1, WW_player2, WW_player3, WW_player4

  #Allow user to enter the server address
  get_server_ip_address()

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
      elif (WW_Client_player == "Player 2"):
        WW_player2 = Join_Game_Player_library
      elif (WW_Client_player == "Player 3"):
        WW_player3 = Join_Game_Player_library
      elif (WW_Client_player == "Player 4"):
        WW_player4 = Join_Game_Player_library
      print("*** Server assigned us player: ", Join_Game_Player_library)
    else:
      print(" Game is full")
      #Show game over summary box
      str1 = "         GAME FULL:"
      str2 = "     Hit key to try again"
      popup_box(str1,str2)

      time.sleep(1)

  print("Getting server data after joining the game")
  WW_client_request_game_data_from_server()

  print("*** after requesting data from server player 1 library = ", WW_player1)
  #Read the data on the server to update our game data (include WW_active_player)
  if (myturn()):
    print(" We are the active player")

  start_time = time.time()
  run = True 
  gameover = False
  new_game = False
  
while run:

  while (new_game == True):
    register_with_server()

  elapsed_time = time.time()

  #Set the game title to include the current player
  pygame.display.set_caption("Word Warrior Rev 2.0 - Boulder Creek Video Games - 2024 ("+WW_Client_player+")")

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

        #Check the played word with the dictionary
        dictionary_button_check()

        #Check if changing players who control the board
        if (go_button_click(pos) == True):
          #Calculate new word score and add it to player's score
          score_word()
          #Turn new character dirty bits to locked bits ones to zeros
          lock_word()
          player_swap_refill_hand()
          go_button_clicked = False
        else:
          if ismytile(pos) == True:
            #print("it's my tile")
            pickup = True
            pickup_tile(pos)

    if event.type == pygame.MOUSEBUTTONUP:
      pos = pygame.mouse.get_pos()
      if (event.button == 1): # wait for left button up.
        if (pickup == True):
          if (out_of_bounds(pos)):
            drop_tile_hand()
          else:
            drop_tile(pos)   
          pickup = False

      #Detect right mouse click up to roll blanks
      if (event.button == 3): #Detect right click
        if (myturn()):
          roll_blank_tile(pos)
          toggle_hand_tile_for_exchange(pos)

    #toggle showing the help screen with F1 key
    if event.type == pygame.KEYUP:
      if(event.key == pygame.K_F1):
        display_help_screen = not display_help_screen

  #Sync server data ever 1 second
  if ((elapsed_time - start_time) >= 2):
    start_time = time.time()
    #If it's this clients turn then send game data to the server
    if (myturn()):
      WW_client_send_game_data_to_server()
      print("Active Player send data")
      WW_client_request_game_data_from_server_lite()
    else:
      #get the latest server data4
      WW_client_request_game_data_from_server()

    #If the bag is empty and this players hand is empty then set gameover = True. 
    check_gameover()

  #Process gameover if set by check_gameover()
  if gameover == True:
    for sync in range (6,0,-1):  #Sync 6 times with the sever at 500ms per sync cylces = 3sec's.  The server game data is sync'd ever 2sec's
      print("Gameover Sync: ",sync)
      score_word()
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
    
    #Show game over summary box
    str1 = "       GAMEOVER:"
    str2 = "PRESS ANY KEY FOR NEW GAME"
    popup_box(str1,str2)

    time.sleep(2) #Allow server to detect game over and reset the game data (bag)
    #WW_client_send_turn_over_command()
    print("Leaving the game")
    new_game = True #Start back over with the IP join game screen
    WW_client_send_game_over_to_server()

  if (display_help_screen):
    screen.blit(help_screen, (0, 0))

  #update display
  pygame.display.flip()

pygame.quit()