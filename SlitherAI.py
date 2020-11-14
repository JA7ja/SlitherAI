from pyautogui import *
import pyautogui
import time
import keyboard
#import random
import win32api, win32con
import math
import neat
import numpy as np
import cv2
import imutils
import pickle
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

 #TITLE SCREEN PIXELS
 # FIRST i        =  X:  553 Y:  262 RGB: (128, 255, 160)
 # SECOND i       =  X:  807 Y:  261 RGB: (152,  80, 255)
 # SHARE BUTTON   =  X:  118 Y:  145 RGB: ( 24, 101, 200)
 # Start button   =  X:  675 Y:  553
 # Quality button =  X: 1283 Y:  176

##Clicks the mouse at a specified x and y
def click_at_pos(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

#Creates the driver for opening and closing google chrome
def create_driver():
    PATH = "C:\\Program Files (x86)\\Chrome_Driver\\chromedriver.exe" #Path to the chrome driver
    driver = webdriver.Chrome(PATH) #Creates webdriver from chromedriver
    return driver

#Enters the bot name into the text box
def enter_name():
    click_at_pos(675, 508) #Clicks on name box
    keyboard.write("SlitherAI")

#Opens google chrome to slither.io and sets the website up to start
def open_slither(driver):
    driver.set_window_size(1364,1023)
    driver.set_window_position(-8,0) #Places window at the top left of screen (idk why this works but it does)
    driver.get("http://slither.io/")
    click_at_pos(1283, 176) #Sets to low grphics
    

##Checks if the game has ended and presses the play button
def is_start_screen():
    #Checks a pixel in the first i, the second i, and the share button to see if they match the colors (Only true on title screen)
    if pyautogui.pixelMatchesColor(553, 262, (128, 255, 160)) and pyautogui.pixelMatchesColor(807, 261, (152,  80, 255)) and pyautogui.pixelMatchesColor(118, 145, (24, 101, 200)):
        return True
    else:
        return False

#Sets the cursor position based on the current given angle
def set_cursor_pos(angle):
    #X and Y of the middle of the game window
    mid_x = 673
    mid_y = 570

    #Calculates the coords of the mouse corresponding to the angle of the circle
    x_mouse_offset = round(250 * math.cos(angle * 360))
    y_mouse_offset = round(250 * math.sin(angle * 360))

    win32api.SetCursorPos((mid_x + x_mouse_offset, mid_y + y_mouse_offset))

#Activates the boost based on a threshold value
def boost(threshold):
    if(threshold < .5):
        pyautogui.keyDown("up")
    else:
        pyautogui.keyUp("up")

#Gets the current score of the bot
def get_score(driver):
    #Gets the score from the site
    try:
        score = driver.find_element(By.XPATH, "/html/body/div[13]/span[1]/span[2]").text
    except:
        return -1

    #Handles undefined/Unexpected results (Not numbers)
    try:
        ret_score = int(score)
    except:
        return -1

    return ret_score

#Full Slither.io game loop from start to end
def run_game():
    driver = create_driver() #Creates driver to interact with webpages
    open_slither(driver)


    curr_angle = 0 #Current angle the mouse is at * 360 from the center of the screen
    control_toggle = False #FOR TESTING: Toggles free mouse vs angled control
    best_score = 0 #Keeps track of the highest score of the bot

    #Waits for the page to load and then starts the game
    while(True):
        if(is_start_screen()):
            click_at_pos(675, 553) #Clicks start button
            break

    while keyboard.is_pressed('q') == False:
        if(is_start_screen()):
            break; #If the bot dies and returns to the start screen, break
        else:
            if control_toggle:
                ##TESTING | If up arrow or down arrow is pressed, adds or subtracts from current mouse angle
                if keyboard.is_pressed('up'):
                    curr_angle = (curr_angle + 0.05) % 1
                if keyboard.is_pressed('down'):
                    curr_angle = (curr_angle - 0.05) % 1

                #Sets the cursor position based on the current angle
                set_cursor_pos(curr_angle)

            else:
                #For manually moving mouse (DEFAULT)
                if keyboard.is_pressed('g'):
                    control_toggle = True

            #Updates best_score if curr_score is greater
            curr_score = get_score(driver)
            if(curr_score > best_score):
                best_score = curr_score

    #Closes the window and returns the score
    driver.quit()
    return best_score

#Starts Slither.io game
def start_game():
    driver = create_driver() #Creates driver to interact with webpages
    open_slither(driver)

    #Waits for the page to load and then starts the game
    while(True):
        if(is_start_screen()):
            click_at_pos(675, 553) #Clicks start button
            break

    return driver

def eval_genomes(genomes, config):
    #print("=============== New Generation ===============")
    #fits = []
    #best_fit = -1
    driver = create_driver()
    open_slither(driver)

    for genome_id, genome in genomes:
        time.sleep(.5)

        enter_name()

        #Waits for the page to load and then starts the game
        while(True):
            if(is_start_screen()):
                click_at_pos(675, 553) #Clicks start button
                break

        time.sleep(1)

        frame = pyautogui.screenshot(region=(1, 125, 1342, 889))
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        shapex, shapey, shapec = frame.shape
        shapex = int(shapex/16)
        shapey = int(shapey/16)

        neural_network = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

        curr_max_fitness = 0
        curr_fitness = 0

        while not is_start_screen():

            frame = cv2.resize(frame, (shapex, shapey))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = frame.flatten()

            nnOutput = neural_network.activate(frame)

            set_cursor_pos(nnOutput[0])
            boost(nnOutput[1])

            curr_fitness = get_score(driver)
            if curr_fitness > curr_max_fitness:
                curr_max_fitness = curr_fitness

            frame = pyautogui.screenshot(region=(1, 125, 1342, 889))
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

            genome.fitness = curr_fitness

        driver.refresh()
        #if curr_max_fitness > best_fit:
            #best_fit = curr_max_fitness
        #fits.append(curr_max_fitness)
        #print(str(genome_id) + " | Max Fitness = " + str(curr_max_fitness))

    #printf("END OF GENERATION:\n  Best Fitness =  " + str(best_fit) +"\n  Avg Fitness  =  " + str(sum(fits)/len(fits)))
    driver.close()




def main():

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "C:\\Users\\Jack\\Desktop\\SlitherAI\\neat-config.txt")

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))

    winner = p.run(eval_genomes)



main()
