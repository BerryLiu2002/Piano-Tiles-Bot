import keyboard
import cv2
import numpy as np
import pyautogui
import time
import win32api
import win32con
# https://www.gamesgames.com/game/magic-piano-tiles

GAME_OFFSET_X = 0
GAME_OFFSET_Y = 0
TILE_WIDTH = 84
TILE_HEIGHT = 147


print("Press 's' to start")
print("Press 'q' to quit")
keyboard.wait('s')

def get_game_pos():
  """
  Returns the top-left position of the game window.
  Input: None
  Returns: Tuple of (x, y, w, h)
  """
  screen = np.array(pyautogui.screenshot())
  game = cv2.imread("images/start2.png", cv2.COLOR_BGR2RGB)
  res = cv2.matchTemplate(screen, game, cv2.TM_CCOEFF_NORMED)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  if max_val > 0.60:
    # Prints overlayed rectangle on top of game window
    # cv2.rectangle(screen, max_loc, (max_loc[0] + game.shape[1], max_loc[1] + game.shape[0]), (0, 0, 255), 2)
    # cv2.imshow("screen", screen)
    # cv2.waitKey(0)

    # Prints overlayed rectange over playable area
    # cv2.rectangle(screen, (location[0], location[1]), (location[0] + location[2], location[1] + location[3]), (0, 0, 255), 2)
    # cv2.imshow("screen", screen)
    # cv2.waitKey(0)
    global GAME_OFFSET_X, GAME_OFFSET_Y
    GAME_OFFSET_X, GAME_OFFSET_Y = max_loc[0]+230, max_loc[1]
    return (max_loc[0]+230, max_loc[1], game.shape[1]-460, game.shape[0])
  else:
    raise Exception(f"Could not find game window. Closest match: {max_val}")

def start_game():
  """
  Starts the game by clicking the start button.
  Requires that the user is past the initial loading screen.
  Input: None
  Returns: None
  """
  screen = np.array(pyautogui.screenshot())
  start_button = cv2.imread("images/start_button.png", cv2.COLOR_BGR2RGB)
  res = cv2.matchTemplate(screen, start_button, cv2.TM_CCOEFF_NORMED)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  if max_val > 0.80:
    start_button_center = (max_loc[0] + start_button.shape[1] / 2, max_loc[1] + start_button.shape[0] / 2)
    click_location(start_button_center[0], start_button_center[1])
    board_loc = get_game_pos()
    run_bot(board_loc)
  else:
    raise Exception(f"Could not find start button. Closest match: {max_val}")
def get_tile_pos(game_pos):
  """
  Returns a list of tuples of the positions of the tiles on the board.
  Input: None
  Returns: List of tuples of (x, y)
  """
  board = np.array(pyautogui.screenshot(region=game_pos))
  tile = cv2.imread("images/tile.png", cv2.COLOR_BGR2RGB)
  res = cv2.matchTemplate(board, tile, cv2.TM_CCOEFF_NORMED)
  threshold = 0.90
  yloc, xloc = np.where(res >= threshold)
  tiles = []
  # cv2.groupRectangles requires at least 2 members in each group so we append twice just in case
  for x,y in zip(xloc, yloc):
    tiles.append([int(x), int(y), int(TILE_WIDTH), int(TILE_HEIGHT)])
    tiles.append([int(x), int(y), int(TILE_WIDTH), int(TILE_HEIGHT)])
  tiles, weight = cv2.groupRectangles(tiles, 1, 0.1)
  if len(tiles) != 0:
    tiles = sorted(tiles, key=lambda x: x[1], reverse=True)
    print(f"Tiles found: {tiles}")
  return sorted(tiles, key=lambda x: x[1], reverse=True) # Sort by lowest y-coordinate (Priority to click)
  
def click_location(x, y):
  win32api.SetCursorPos((int(x), int(y)))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
  time.sleep(0.01)
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def run_bot(game_pos):
  while True:
    tiles = get_tile_pos(game_pos)
    if tiles:
      x = tiles[0][0]+GAME_OFFSET_X+TILE_WIDTH/2
      y = tiles[0][1]+GAME_OFFSET_Y+TILE_HEIGHT/2
      click_location(x, y)
    if keyboard.is_pressed('q'):
      break

def main():
  start_game()

main()