#word_warrior.py
#word_warrior Rev 1.0
#Boulder Creek Video Games
#Jim Nolan, Connor Nolan, Alissa Nolan
#27-Oct-2024
#
#Dependancies:
# - Must install pygame
#
#Game Notes:
# - Player 1 and Player 2 local supported
# 
#
#TODO:
# - More testing
# - Add splash screen
# - Save/Load Game
# = Add Network server (player 1), Client (player 2) TCP/IP socket support
# - Fun animation and sounds
# - Dictonary scrubbing of words
# - CP player
# 

import pygame
import math
import sys 
from gameboard import *

pygame.init()

#define screen size +1 for room on the size for game data.
SCREEN_WIDTH  = (GAMEBOARD_X_TILES + 1) * TILES_WIDTH  
SCREEN_HEIGHT = (GAMEBOARD_Y_TILES + 1) * TILES_HEIGHT

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Warrior Rev 1.0 - Boulder Creek Video Games - 2024")

#define colors
GREEN  = (0, 255, 0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
WHITE  = (255, 255, 255)
YELLOW = (255,255,0)
BLACK  = (0,0,0)
GRAY   = (200,200,200)

word_warrior_font        = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 25)
word_warrior_score_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 15)
word_warrior_value_font  = pygame.font.Font("assets/fonts/Arial-Unicode-Regular.ttf", 10)
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
go_tile        = pygame.image.load("assets/imgs/go_tile.png").convert_alpha()
black_tile     = pygame.image.load("assets/imgs/black_tile.png").convert_alpha()

# player
PLAYER1 = 1
PLAYER2 = 2

player = PLAYER1

player1_score = 0
player2_score = 0

player_last_score = 0

selected_tile_letter = '#' # = no tile selected

#function for drawing text
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#Draw Background
def drawbackground(screen):
  j = 0
  for i in range(len(GAMEBOARD)):
    for j in range(len(GAMEBOARD[i])):
      tile = GAMEBOARD[i][j]

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

def gameboard_update(screen):
  j = 0
  for i in range(len(GAMEBOARD_WORDS)):
    for j in range(len(GAMEBOARD_WORDS[i])):
      tile = GAMEBOARD_WORDS[i][j]  

      if (tile != '#'):
        #Upper case letters on the gameboard are player 1, Lower case letters are player 2
        #if (tile.isupper()):
        if (player == PLAYER1):
          img = blank_tile3
        else:
          img = blank_tile2

        #if the tile is fixed draw it with tan background
        if(DIRTY_GAMEBOARD[i][j] == '0'):
          img = blank_tile1

        screen.blit(img,(j*blank_space.get_width(),i*blank_space.get_height()))

        #Don't render blank tile text
        if (tile != ' ' and tile != '$'):
          font_img = word_warrior_font.render(tile.upper(), True, BLACK)
          screen.blit(font_img,((j*blank_space.get_width())+10,(i*blank_space.get_height())+ 0))

        font_value_img = word_warrior_value_font.render(str(letter_value[tile.upper()]), True, BLACK)
        screen.blit(font_value_img,((j*blank_space.get_width())+25,(i*blank_space.get_height())+ 25))

def player1_hand_empty():
  for i in range(0,7):
    if player1_hand[i] != '#':
      return (False)
  else:
    return(True)

def player2_hand_empty():
  for i in range(0,7):
    if player2_hand[i] != '#':
      return (False)
  else:
    return(True)

def value_player1_hand():
  value = 0

  for i in range(0,7):
    if (player1_hand[i] != '#'):
      value += letter_value[player1_hand[i].upper()]
  return (value)

def value_player2_hand():
  value = 0

  for i in range(0,7):
    if (player2_hand[i] != '#'):
      value += letter_value[player2_hand[i].upper()]
  return (value)

def hand_mouse_drag_update(screen):
  x = 0
  y = 40*15
  global selected_tile_letter
  global player
  global player1_score
  global player2_score
  global gameover 


  #Pick which hand to display and check for Gameover
  if (player == PLAYER1):
    if (player2_hand_empty() and how_many_tiles_left() == 0):
      player1_score -= value_player1_hand() # Remove he points from the left over tiles
      gameover = True
    hand = player1_hand
  else:
    if (player1_hand_empty() and how_many_tiles_left() == 0):
      player2_score -= value_player2_hand() # Remove he points from the left over tiles
      gameover = True
    hand = player2_hand

  #Draw each tile on the player hand
  for tile in hand:
    #Draw the tile only if it is a valid tile (A-Z or Blank)
    if (tile == '#'):  
      #Draw black-unpopulated tile
      img = black_tile
      screen.blit(img,(x,y))
    else:
      #Draw blank tile if actually a blank tile
      if (player == PLAYER1):
        img = blank_tile3
      else:
        img = blank_tile2

      screen.blit(img,(x,y))

    #Draw tile letter and value if not a blank tile
    if (tile != ' ' and tile != '$'):
      font_img = word_warrior_font.render(tile.upper(), True, BLACK)
      screen.blit(font_img,(x+10,y))

    #draw tile letter value
    font_value_img = word_warrior_value_font.render(str(letter_value[tile.upper()]), True, BLACK)
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
      
      if (player == PLAYER1):
        img = blank_tile3
      else:
        img = blank_tile2

      screen.blit(img,(mouse_x,mouse_y))

      # Don't draw the tile text if the tile is a blank
      if (selected_tile_letter != ' ' and selected_tile_letter != '$'):
        font_img = word_warrior_font.render(selected_tile_letter.upper(), True, BLACK)
        screen.blit(font_img,(mouse_x+10,mouse_y))

      font_value_img = word_warrior_value_font.render(str(letter_value[selected_tile_letter.upper()]), True, BLACK)
      screen.blit(font_value_img,(mouse_x+25,mouse_y+25))

def tile_pile_update(screen):
  number_of_tiles = how_many_tiles_left()
  if (number_of_tiles == 0):
    return

  x = 15*40
  img = blank_tile1 

  for y in range(1, number_of_tiles+1):
    screen.blit(img,(x,5*y))

  bag_count_img = word_warrior_value_font.render(str(number_of_tiles), True, BLACK)
  screen.blit(bag_count_img,(x+10,(5*y)+7))
  count_img     = word_warrior_value_font.render("LEFT",True, BLACK)
  screen.blit(count_img,(x+8,(5*y)+12+10))

def show_turn_scores_go_button(screen):
  if (player == PLAYER1):
    score_img = word_warrior_score_font.render("Player 1 Turn, P1 Score: "+str(player1_score)+"  P2 Score: "+str(player2_score), True, WHITE)
  else:
    score_img = word_warrior_score_font.render("Player 2 Turn, P1 Score: "+str(player1_score)+"  P2 Score: "+str(player2_score), True, WHITE)
  
  last_score_img = word_warrior_score_font.render("Last Player score: "+str(player_last_score),True, WHITE)

  screen.blit(score_img,(300,598))
  screen.blit(last_score_img,(300,613))

  #draw go button
  img = go_tile
  screen.blit(img,(15*40,15*40))

def pickup_tile(pos):
  x = 0
  y = 40*15
  global selected_tile_letter
  global player
  global player1_hand
  global player2_hand

  mouse_x = pos[0]
  mouse_y = pos[1]
 
  if (player == PLAYER1):
    hand = player1_hand
  else:
    hand = player2_hand

  #If tile is picked up from players hand
  if (mouse_y >= y and mouse_y <= y+40 and mouse_x >= x and mouse_x <= x+(40*7)):
    hand_position = math.floor(mouse_x/40)
    
   #Sometimes the math above sets the tile_x or tile_y to 15 at the extreme edge of the game board
    if hand_position > 6:
      hand_position = 6

    #Don't pick up empty tile
    if (hand[hand_position] != '#'):
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

    #print("pickup tile value: ",GAMEBOARD_WORDS[tile_y][tile_x], " Dirty value: ", DIRTY_GAMEBOARD[tile_y][tile_x])

    #Check that the tile clicked is not empty or and old tile
    if (GAMEBOARD_WORDS[tile_y][tile_x] != "#" and DIRTY_GAMEBOARD[tile_y][tile_x] != '0'):
      selected_tile_letter = GAMEBOARD_WORDS[tile_y][tile_x]
      GAMEBOARD_WORDS[tile_y][tile_x] = '#'
      DIRTY_GAMEBOARD[tile_y][tile_x] = '#'


  if (player == PLAYER1):
    player1_hand = hand
  else:
    player2_hand = hand

def drop_tile(pos):
  x = 0
  y = 40*15
  global selected_tile_letter
  global player
  global player1_hand
  global player2_hand

  mouse_x = pos[0]
  mouse_y = pos[1]

  successful_insert = False

  if (player == PLAYER1):
    hand = player1_hand
  else:
    hand = player2_hand

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
    if (GAMEBOARD_WORDS[tile_y][tile_x] == '#' and selected_tile_letter != '#'):
      if (player == PLAYER1):
        GAMEBOARD_WORDS[tile_y][tile_x] = selected_tile_letter.upper()
        DIRTY_GAMEBOARD[tile_y][tile_x] = '1'
      else:
        if (selected_tile_letter == ' '):
          GAMEBOARD_WORDS[tile_y][tile_x] = '$'    
        else:
          GAMEBOARD_WORDS[tile_y][tile_x] = selected_tile_letter.lower()    
        DIRTY_GAMEBOARD[tile_y][tile_x] = '1'

      selected_tile_letter = '#'
    else:
      #return the character to the hand at the first available blank
      for i in range(0,7):
        if hand[i] == '#':
          hand[i] = selected_tile_letter
          selected_tile_letter = '#'
          break
  
  if (player == PLAYER1):
    player1_hand = hand
  else:
    player2_hand = hand

#Handle swaping the player who controls the board
def player_swap():
  global player

  if (player == PLAYER1):
    player = PLAYER2
    refill_hand(player1_hand)
  else:
    player = PLAYER1
    refill_hand(player2_hand)

def ismytile(pos):
  x = 0
  y = 40*15

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
    #Note ' ' blank tile belongs to Player 1, '$' coded blank belongs to player 2
    if (player == PLAYER1):
      if(GAMEBOARD_WORDS[tile_y][tile_x].isupper() or GAMEBOARD_WORDS[tile_y][tile_x] == ' '):
        #print("is player 1's tile")
        return(True)
    if (player == PLAYER2):
      if (GAMEBOARD_WORDS[tile_y][tile_x].islower() or GAMEBOARD_WORDS[tile_y][tile_x] == '$'):
        #print("is player 2's tile")
        return(True)
    return (False)

def out_of_bounds(pos):
  x = 0
  y = 40*15

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
  global player1_hand
  global player2_hand
  global player

  if (player == PLAYER1):
    hand = player1_hand
  else:
    hand = player2_hand

  #return the character to the hand at the first available blank
  for i in range(0,7):
    if hand[i] == '#':
      hand[i] = selected_tile_letter
      selected_tile_letter = '#'
      break

  if (player == PLAYER1):
    player1_hand = hand
  else:
    player2_hand = hand

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
    if (GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (GAMEBOARD[y][x] == '4' and DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 2

    if GAMEBOARD_WORDS[y][x] == '#':
      west_most_tile_x = x+1
      break
    if x==0: #found the west edge of the board
      west_most_tile_x = 0

  for x in range (start_x,15): # look at the tiles east of the new tile for the end of the word

    #Check for tripple word or double word multiplier under a new tile
    if (GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (GAMEBOARD[y][x] == '4' and DIRTY_GAMEBOARD[y][x] == '1' and x != start_x):
        word_multiplier *= 3
      #Look for double multiplier
      if (GAMEBOARD[y][x] == '5' and DIRTY_GAMEBOARD[y][x] == '1' and x != start_x):
        word_multiplier *= 2

    if GAMEBOARD_WORDS[y][x] == "#":
      east_most_tile_x = x-1
      break
    if x==14:
      east_most_tile_x = 14 #found the east edge of the board 

  #print("west most: ",west_most_tile_x," east most: ",east_most_tile_x)

  #Sum up the values of the WE root word
  for x in range (west_most_tile_x, east_most_tile_x+1):
    #Check for double letter
    if (GAMEBOARD[y][x] == '2' and DIRTY_GAMEBOARD[y][x] == '1'):
      score += 2*(letter_value[GAMEBOARD_WORDS[y][x].upper()])
      #print("added 2x letter score: ", 2*(letter_value[GAMEBOARD_WORDS[y][x].upper()]),"at x y:",x, y)

    #Check for tripple letter
    elif (GAMEBOARD[y][x] == '3' and DIRTY_GAMEBOARD[y][x] == '1'):
      score += 3*(letter_value[GAMEBOARD_WORDS[y][x].upper()])
      #print("added 3x score: ", 3*(letter_value[GAMEBOARD_WORDS[y][x].upper()]),"at x y:",x,y)

    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[GAMEBOARD_WORDS[y][x].upper()]
      #print ("added score: ", letter_value[GAMEBOARD_WORDS[y][x].upper()],"at x y:",x,y)   

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
    if (GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (GAMEBOARD[y][x] == '4' and DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 3
      #Look for double multiplier (include center square (7,7) as a 2x multiplier)
      if ((GAMEBOARD[y][x] == '5' or (x == 7 and y == 7)) and DIRTY_GAMEBOARD[y][x] == '1'):
        word_multiplier *= 2

    if GAMEBOARD_WORDS[y][x] == '#':
      north_most_tile_y = y+1
      break
    if y==0: #found the north edge of the board
      north_most_tile_y = 0

  for y in range (start_y,15): # look at the tiles east of the new tile for the end of the word
    #Check for tripple word or double word multiplier under a new tile
    if (GAMEBOARD_WORDS[y][x] != '#'):
      #Look for tripple multiplier
      if (GAMEBOARD[y][x] == '4' and DIRTY_GAMEBOARD[y][x] == '1' and y != start_y):
        word_multiplier *= 3
      #Look for double multiplier
      if (GAMEBOARD[y][x] == '5' and DIRTY_GAMEBOARD[y][x] == '1' and y != start_y):
        word_multiplier *= 2

    if GAMEBOARD_WORDS[y][x] == "#":
      south_most_tile_y = y-1
      break
    if y==14:
      south_most_tile_y = 14 #found the south edge of the board 

  #print ("north most: ",north_most_tile_y," south most: ",south_most_tile_y)
  #Sum up the values of the NS root word
  for y in range (north_most_tile_y, south_most_tile_y+1):
    #print("Dirty @ XY",DIRTY_GAMEBOARD[y][x])
    
    #Check for double letter
    if (GAMEBOARD[y][x] == '2' and DIRTY_GAMEBOARD[y][x] == '1'):
      score += 2*(letter_value[GAMEBOARD_WORDS[y][x].upper()])
      #print("added 2x letter score: ", 2*(letter_value[GAMEBOARD_WORDS[y][x].upper()]),"at x y:",x, y)
    
    #Check for tripple letter
    elif (GAMEBOARD[y][x] == '3' and DIRTY_GAMEBOARD[y][x] == '1'):
      score += 3*(letter_value[GAMEBOARD_WORDS[y][x].upper()])
      #print("added 3x letter score: ", 3*(letter_value[GAMEBOARD_WORDS[y][x].upper()]),"at x y:",x, y)
    
    else:
      #If the tile was not a newly placed tile on a letter multiplier from the if/elif above then add the face value
      score += letter_value[GAMEBOARD_WORDS[y][x].upper()]
      #print ("added score: ", letter_value[GAMEBOARD_WORDS[y][x].upper()],"at x y:",x,y)   
  
  #Factor in word multiplier
  score *= word_multiplier

  return(score)

def detect_west_east_word (x,y):
  #check west and east of tile at x,y to see if there is a word
  if (x-1>=0):
    if (GAMEBOARD_WORDS[y][x-1] != '#'):
      return(True) #found letter to the west of the first new tile
  if (x+1<=14):
    if (GAMEBOARD_WORDS[y][x+1] != '#'):
      return(True)
  return(False)

def detect_north_south_word (x,y):
  #check north and south of tile at x,y to see if there is a word
  if (y-1>=0):
    if (GAMEBOARD_WORDS[y-1][x] != '#'):
      return(True) #found letter to the north of the first new tile
  if (y+1<=14):
    if (GAMEBOARD_WORDS[y+1][x] != '#'):
      return(True) #Found letter to the south of the first new tile
  return (False)

def score_word ():
  x = 0
  y = 0
  global player
  global player1_score
  global player2_score
  player_score = 0
  global player_last_score

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
      if (DIRTY_GAMEBOARD[y][x] == '1'):
        new_tiles [number_of_new_tiles][0] = GAMEBOARD_WORDS[y][x]
        new_tiles [number_of_new_tiles][1] = x 
        new_tiles [number_of_new_tiles][2] = y
        new_tiles [number_of_new_tiles][3] = GAMEBOARD[y][x] #tile type aka multipler

        number_of_new_tiles += 1 

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
    #print("more than a single character word")
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
  
  if (player == PLAYER1):
    player1_score += player_score
  else:
    player2_score += player_score
  
  player_last_score = player_score

def lock_word ():
  global DIRTY_GAMEBOARD

  for x in range(0,15):
    for y in range(0,15):
      if DIRTY_GAMEBOARD[y][x] == '1':
        DIRTY_GAMEBOARD[y][x] = '0'

def reset_game():
  global player1_score
  global player2_score
  global gameover 
  global run
  global player1_hand 
  global player2_hand
  global pickup
  global GAMEBOARD_WORDS
  global DIRTY_GAMEBOARD
  global player
  global player_last_score
  global selected_tile_letter

  #Reset the gameboard trackers
  for x in range(0,15):
    for y in range (0,15):
      GAMEBOARD_WORDS[y][x] = '#'
      DIRTY_GAMEBOARD[y][x] = '#'

  player1_score = 0
  player2_score = 0

  player = PLAYER1

  player_last_score = 0

  selected_tile_letter = '#' # = no tile selected
  
  #game loop
  gameover = False
  run = True

  #Setup board
  mix_word_warrior_bag()

  #for debugging endgame remove 90 tiles
  #for i in range(0,90):
  #  word_warrior_bag.pop()

  #Reset the hands to empty before refilling
  for i in range(0,7):
    player1_hand[i] = '#'
    player2_hand[i] = '#'

  refill_hand(player1_hand)
  refill_hand(player2_hand)

  #Record if a drag and drop (pickup) is active
  pickup = False

def wait_for_keypress():
  pygame.event.clear()
  
  while True:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        return

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

#reset game and get ready to run
pygame.mouse.set_visible(True)
reset_game()

while run:

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

   #Check for gameover
  if gameover == True:
    pygame.time.wait(500)
    str1 = "GAMEOVER: Player 1 score: " + str(player1_score) + " Player 2 score: " + str(player2_score)
    str2 = "PRESS ANY KEY FOR NEW GAME"
    popup_box(str1,str2)
    #pygame.display.flip()
    #wait_for_keypress()
    reset_game()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

    if event.type == pygame.MOUSEBUTTONDOWN:
      pos = pygame.mouse.get_pos()
      #Check if changing players who control the board
      if (start_button_click(pos) == True):
        #Calculate new word score and add it to player's score
        score_word()
        #Turn new character dirty bits to locked bits ones to zeros
        lock_word()
        player_swap()
        #todo send network sync data
      else:
        if ismytile(pos) == True:
          #print("it's my tile")
          pickup = True
          pickup_tile(pos)
         
    if event.type == pygame.MOUSEBUTTONUP:
      pos = pygame.mouse.get_pos()
      if (pickup == True):
        if (out_of_bounds(pos)):
          drop_tile_hand()
        else:
          drop_tile(pos)   
        pickup = False

  
  #update display
  pygame.display.flip()

  #set game over
  #gameover = True
pygame.quit()