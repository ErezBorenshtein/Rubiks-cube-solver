import cv2
import sys
import os
import serial
import pycuber as pc
from pycuber.solver import CFOPSolver
import time
import numpy as np
import kociemba
import colorama
from Cube_Camera import calibrate_cube_colors
from Cube_Camera import init_camera
from Cube_Camera import read_cube_colors
from Cube_Camera import WaitForKey
from Cube_Camera import recalc_all_faces
from video import Webcam

from constants import (
    DIRECTION_NONE,
    DIRECTION_FLIP_HORIZONTAL,
    DIRECTION_FLIP_VERTICAL
)

web_camera = 0

Cube_Moves = {
    #F
    ("F",1): "p1 s2 p2 h s1 s2 p1",
    ("F",2): "p3 h s1 re p1",
    ("F",3): "p3 h s2 re p1 ",
    #F'
    ("F'",1) : "p3 h s2 re p1",
    ("F'",2) : "p3 h s3 re p1",
    ("F'",3) : "p1 s2 p2 h s3 s2 p1",
    #B
    ("B",1):"s3 p1 s2 p2 h s1 re s2 p3",
    ("B",2):"p1 h s1 re p3",
    ("B",3):"p1 h s2 re p3",
    #B'
    ("B'",1):"p1 h s2 re p3",
    ("B'",2):"p1 h s3 re p3",
    ("B'",3):"p3 s2 p2 h s3 re s2 p3",
    #D
    ("D",1):"h s3 re p2 s2 p2 h s3 re s2",
    ("D",2):"h s1 re",
    ("D",3):"h s2 re",
    #D'
    ("D'",1):"h s2 re",
    ("D'",2):"h s3 re",
    ("D'",3):"h s1 re p2 s2 p2 h s1 re s2",
    #R
    ("R",1):"s2 p3 h s1 re p2 s2 p2 s1 p3 s2",
    ("R",2):"s3 p3 h s2 re p2 s3 p2 s2 p3 s3",
    ("R",3):"s2 p1 h s1 re p3 s2",
    #R'
    ("R'",1):"s2 p3 h s3 re p1 s2",
    ("R'",2):"s1 p1 h s2 re p1 s1 p2",
    ("R'",3):"s2 p1 h s3 re p1 s2 p2",
    #L
    ("L",1):"s2 p1 h s1 re p1 s2 p2",
    ("L",2):"s3 p1 h s2 re p1 s3 p2",
    ("L",3):"s2 p3 h s1 re p1 s2",
    #L'
    ("L'",1):"s2 p1 h s3 re p3 s2",
    ("L'",2):"s1 p3 h s2 re p2 s1 p2 s2 p3 s1",
    ("L'",3):"s2 p3 h s3 re p2 s2 p2 s1 p1 s2",
    #U
    ("U",1):"p2 h s3 re p2 s2 p2 h s3 re s2 p2",
    ("U",2):"p2 h s1 re p2",
    ("U",3):"p2 h s2 re p2",
    #U'
    ("U'",1):"p2 h s2 re p2",
    ("U'",2):"p2 h s3 re p2",
    ("U'",3):"p2 h s1 re p2 s2 p2 h s1 re s2 p2"
}



def generate_scramble(c):
    alg = pc.Formula() #IDK what is this
    scramble = alg.random() #creating scramble
    c(scramble) #set the scramble on the cube
    return scramble

def simplify_solution(solution):
    solution = str(solution)
    solution =solution.replace("R2", "R R")
    solution =solution.replace("L2", "L L")
    solution =solution.replace("U2", "U U")
    solution =solution.replace("D2", "D D")
    solution =solution.replace("F2", "F F")
    solution =solution.replace("B2", "B B")
    return solution

def get_last_pos(command):
    return int (command[command.rfind("s")+1])

def RemovePrefixSuffix(line):
    line = str(line)
    line= line.replace("b'","")
    line= line.replace("\\r\\n'","")
    if line == "d":
        line = ""
    return line

def reset_arduino(serialInst):
    print ("Resetting Arduino...")
    serialInst.setDTR(False) # Drop DTR
    time.sleep(0.022) # similar to ide
    serialInst.setDTR(True)  # Up the DTR back
    print ("Arduino was set...")
    time.sleep(5)

def initialize_connection(serialInst):
    print ("Initializing Connection...")
    reset_arduino(serialInst) # get arduino ready
    serialInst.write("start\n".encode())
    time.sleep(2)
    line = RemovePrefixSuffix(serialInst.readline())
    while line != "arduino is ready":
        line = RemovePrefixSuffix(serialInst.readline())
        print ("Waiting for Arduino...")
    print("initialize_connection completed")

def get_num_of_steps(solution):
    last_pos = 2
    steps_in_solution = ""
    solution_moves = solution.split(" ")
    for move in solution_moves:
        step =  Cube_Moves[move,last_pos]+" "
        last_pos = get_last_pos(Cube_Moves[move,last_pos])
        steps_in_solution += step
    steps_in_solution = steps_in_solution.split(" ")
    return len(steps_in_solution)


def send_solution(serialInst,solution):    
    num_of_move = 0
    print ("Arduino status is ready before send solution...")
    last_pos = 2
    solution_moves = solution.split(" ")
    for move in solution_moves:

        step =  Cube_Moves[move,last_pos]+" "
        last_pos = get_last_pos(Cube_Moves[move,last_pos])
        serialInst.write(step.encode())
        print("sending: "+step)
        while serialInst.in_waiting == 0:
            pass
        print("getting:",num_of_move,RemovePrefixSuffix(serialInst.readline()))
        num_of_move+=1
    serialInst.write("end\n".encode())
  



def ProceedCubeToNextColor(serialInst,go_string):
    serialInst.write(go_string.encode())
    RemovePrefixSuffix(serialInst.readline())


def read_all_faces(serialInst):
    global web_camera

    RemovePrefixSuffix(serialInst.readline())

    web_camera.read_one_face()     #blue, back
    ProceedCubeToNextColor(serialInst,"Go")

    web_camera.read_one_face(True)#yellow, down
    ProceedCubeToNextColor(serialInst,"Go2")

    web_camera.read_one_face(True)#green, front - REVERSED!!
    ProceedCubeToNextColor(serialInst,"Go3")

    web_camera.read_one_face(True)#white, up
    ProceedCubeToNextColor(serialInst,"Go4")

    web_camera.read_one_face()#orange, left
    ProceedCubeToNextColor(serialInst,"Go5")
    
    web_camera.read_one_face()#red, right
    ProceedCubeToNextColor(serialInst,"Go6")

def update_square(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        web_camera.update_square((x,y))

def send_num_of_steps(serialInst,solution):
    serialInst.write(str(get_num_of_steps(solution)).encode())
    serialInst.readline()



def main():
#start serial
    serialInst = serial.Serial('COM5', 9600)
    initialize_connection(serialInst)
    global web_camera
    web_camera = Webcam()

    web_camera.turn_camera_on()
    
    cv2.namedWindow('Cube Solver')
    cv2.setMouseCallback("Cube Solver", update_square)
    #web_camera.run()
    #web_camera.waitForKey("kociemba faild, change the wrong colors manually")

    read_all_faces(serialInst)

    #init_camera()
    #WaitForKey("adjust camara")

    #calibrate_cube_colors(serialInst)
    #input("scramble the cube")
    #cube_colors=read_cube_colors(serialInst)
    #WaitForKey("adjust colors")
    is_solve_valid = False
    while is_solve_valid == False:
        try:
            is_solve_valid = True
            cube_colors = web_camera.get_result_notation()
            #cube_colors ="FLBUULFFLFDURRDBUBUUDDFFBRDDBLRDRFLLRLRULFUDRRBDBBBUFL"
            solution = kociemba.solve(cube_colors)
            time.sleep(2)#take some time between serial calls
        except:
            is_solve_valid = False
            web_camera.waitForKey("kociemba faild, change the wrong colors manually")
            cube_colors = recalc_all_faces()
    #solution = "R' D2 R' U2 R F2 D B2 U' R F' U R2 D L2 D' B2 R2 B2 U' B2"
    solution = simplify_solution(solution)
    send_num_of_steps(serialInst,solution)
    send_solution(serialInst,solution)

    
    while True:
        line = RemovePrefixSuffix(serialInst.readline()) 
        if line != "":
            print(line)

main()