import cv2
import numpy as np
import kociemba as Cube
import time
import colorama
#import serial
import time

HSV_Colors = {
    'green' : (0,0,0),
    'white' : (0,0,0),
    'orange' : (0,0,0),
    'blue' : (0,0,0),
    'red'  : (0,0,0),
    'yellow' : (0,0,0)
}

time_to_identify = 4 #4
time_to_calc_edge = 10 #4

all_states = ['up','right','front','down','left','back']
all_colors = ['green','white','blue','red','orange','yellow']

preview = np.zeros((700,800,3), np.uint8)
state=  {
            'up':['white','white','white','white','white','white','white','white','white',],
            'right':['white','white','white','white','white','white','white','white','white',],
            'front':['white','white','white','white','white','white','white','white','white',],
            'down':['white','white','white','white','white','white','white','white','white',],
            'left':['white','white','white','white','white','white','white','white','white',],
            'back':['white','white','white','white','white','white','white','white','white',]
        }

sign_conv={
            'green'  : 'F',
            'white'  : 'U',
            'blue'   : 'B',
            'red'    : 'R',
            'orange' : 'L',
            'yellow' : 'D'
          }

sign_conv_inv={
            'F' : 'green',
            'U' : 'white',  
            'B': 'blue',
            'R' : 'red',
            'L' : 'orange',
            'D' : 'yellow'
          }


color = {
        'red'    : (0,0,255),
        'orange' : (0,165,255),
        'blue'   : (255,0,0),
        'green'  : (0,255,0),
        'white'  : (255,255,255),
        'yellow' : (0,255,255)
        }

stickers = {
        'main': [
            [200, 120], [300, 120], [400, 120],
            [200, 220], [300, 220], [400, 220],
            [200, 320], [300, 320], [400, 320]
        ],
        'current': [
            [20, 20], [54, 20], [88, 20],
            [20, 54], [54, 54], [88, 54],
            [20, 88], [54, 88], [88, 88]
        ],
        'preview': [
            [20, 130], [54, 130], [88, 130],
            [20, 164], [54, 164], [88, 164],
            [20, 198], [54, 198], [88, 198]
        ],
        'left': [
            [50, 280], [94, 280], [138, 280],
            [50, 324], [94, 324], [138, 324],
            [50, 368], [94, 368], [138, 368]
        ],
        'front': [
            [188, 280], [232, 280], [276, 280],
            [188, 324], [232, 324], [276, 324],
            [188, 368], [232, 368], [276, 368]
        ],
        'right': [
            [326, 280], [370, 280], [414, 280],
            [326, 324], [370, 324], [414, 324],
            [326, 368], [370, 368], [414, 368]
        ],
        'up': [
            [188, 128], [232, 128], [276, 128],
            [188, 172], [232, 172], [276, 172],
            [188, 216], [232, 216], [276, 216]
        ],
        'down': [
            [188, 434], [232, 434], [276, 434],
            [188, 478], [232, 478], [276, 478],
            [188, 522], [232, 522], [276, 522]
        ], 
        'back': [
            [464, 280], [508, 280], [552, 280],
            [464, 324], [508, 324], [552, 324],
            [464, 368], [508, 368], [552, 368]
        ],
           }

font = cv2.FONT_HERSHEY_SIMPLEX  
textPoints=  {
            'up':[['U',242, 202],['W',(255,255,255),260,208]],
            'right':[['R',380, 354],['R',(0,0,255),398,360]],
            'front':[['F',242, 354],['G',(0,255,0),260,360]],
            'down':[['D',242, 508],['Y',(0,255,255),260,514]],
            'left':[['L',104,354],['O',(0,165,255),122,360]],
            'back':[['B',518, 354],['B',(255,0,0),536,360]],
        }

check_state=[]
solution=[]
solved=False
cap=0

def set_side(side,colors_str):
    main=state[side]
    main[0],main[1],main[2],main[3],main[4],main[5],main[6],main[7],main[8] = sign_conv_inv[colors_str[0]],sign_conv_inv[colors_str[1]],sign_conv_inv[colors_str[2]],sign_conv_inv[colors_str[3]],sign_conv_inv[colors_str[4]],sign_conv_inv[colors_str[5]],sign_conv_inv[colors_str[6]],sign_conv_inv[colors_str[7]],sign_conv_inv[colors_str[8]]

def color_detect(h,s,v,print_colors):

    all_colors = []
    
    for color in HSV_Colors.keys():
        deltah = h-HSV_Colors[color][0]
        deltas = s- HSV_Colors[color][1]
        deltav = v-HSV_Colors[color][2]

        offset = abs(h-HSV_Colors[color][0]) 
        if (print_colors):
            print ("ofsh" , offset)
        offset +=  abs(s-HSV_Colors[color][1])
        if (print_colors):
            print ("ofss" , offset)
        offset +=  abs(v-HSV_Colors[color][2]) 
        if (print_colors):
            print ("ofsv" , offset)
            print (offset)

        if (print_colors):
            print(color)
            print("myAbsH =" ,abs(h-HSV_Colors[color][0]), deltah)
            print("myAbsS =" ,abs(s-HSV_Colors[color][1]), deltas)
            print("myAbsV =" ,abs(v-HSV_Colors[color][2]), deltav)

        all_colors.append((color,offset))

    sorted_list = sorted(all_colors, key=lambda x: x[1])
    if (print_colors):
        print(str(h)+ " " + str(s) + " " + str(v))
        print("hsv colors" , HSV_Colors[sorted_list[0][0]])
        print ("all colors", all_colors)
        print ("sorted list" , sorted_list)
        print(HSV_Colors)
    return sorted_list[0][0]

def refresh_all_windows():
    ret,img=cap.read() 
    draw_stickers(img,stickers,'main')
    draw_stickers(img,stickers,'current')
    draw_color_nums(img)
    draw_preview_stickers(preview,stickers)
    draw_hsv(img,stickers)
    fill_stickers(preview,stickers,state)
    texton_preview_stickers(preview,stickers)
    handle_preview_window()
    cv2.imshow('preview',preview)
    cv2.imshow('frame',img[0:500,0:500])

def WaitForKey2(message):
     print(message)
     while True:
        refresh_all_windows()
        k = cv2.waitKey(5) & 0xFF
        if k == ord('a'):
            break

def WaitForKey(message):
     print(message)
     while True:
        refresh_all_windows()
        k = cv2.waitKey(5) & 0xFF
        if k == ord('a'):
            break

def draw_stickers(frame,stickers,name):
        for x,y in stickers[name]:
            cv2.rectangle(frame, (x,y), (x+30, y+30), (255,255,255), 2)

def draw_color_nums(frame):
     text ="blue:" + str( HSV_Colors['blue'][0])+ " " + str( HSV_Colors['blue'][1]) + " " + str( HSV_Colors['blue'][2])
     cv2.putText(frame, text,(20,200), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
     text ="red:" + str( HSV_Colors['red'][0])+ " " + str( HSV_Colors['red'][1]) + " " + str( HSV_Colors['red'][2])
     cv2.putText(frame, text,(20,220), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
     text ="orange:" + str( HSV_Colors['orange'][0])+ " " + str( HSV_Colors['orange'][1]) + " " + str( HSV_Colors['orange'][2])
     cv2.putText(frame, text,(20,240), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
     text ="green:" + str( HSV_Colors['green'][0])+ " " + str( HSV_Colors['green'][1]) + " " + str( HSV_Colors['green'][2])
     cv2.putText(frame, text,(20,260), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
     text ="white:" + str( HSV_Colors['white'][0])+ " " + str( HSV_Colors['white'][1]) + " " + str( HSV_Colors['white'][2])
     cv2.putText(frame, text,(20,280), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
     text ="yellow:" + str( HSV_Colors['yellow'][0])+ " " + str( HSV_Colors['yellow'][1]) + " " + str( HSV_Colors['yellow'][2])
     cv2.putText(frame, text,(20,300), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 

def draw_hsv(frame,stickers):
  
    for i in range(9):
        x = stickers['main'][i][0]
        y = stickers['main'][i][1]
        cv2.rectangle(frame, (x,y), (x+30, y+30), (255,255,255), 2) 
        x = stickers['main'][i][0]+10
        y = stickers['main'][i][1]+10
        hsv = frame[y][x]
        color_text = color_detect(hsv[0],hsv[1],hsv[2],False)
        text =str( hsv[0])+ " " + str(hsv[1]) + " " + str(hsv[2])
        cv2.putText(frame, text, (x,y-25), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA) 
        cv2.putText(frame, color_text, (x,y-15), cv2.FONT_HERSHEY_SIMPLEX,  0.3, (255,255,255), 1, cv2.LINE_AA)   
        #hsv.append(frame[x][y])

    #for x,y in stickers["main"]:
    #    org = (x, y-10)
    #    cv2.putText(frame, 'OpenCV', org, font,  fontScale, color, thickness, cv2.LINE_AA)

        #cv2.rectangle(frame, (x,y), (x+30, y+30), (255,255,255), 2)


def draw_preview_stickers(frame,stickers):
        stick=['front','back','left','right','up','down']
        for name in stick:
            for x,y in stickers[name]:
                cv2.rectangle(frame, (x,y), (x+40, y+40), (255,255,255), 2)

def texton_preview_stickers(frame,stickers):
        stick=['front','back','left','right','up','down']
        for name in stick:
            for x,y in stickers[name]:
                sym,x1,y1=textPoints[name][0][0],textPoints[name][0][1],textPoints[name][0][2]
                cv2.putText(preview, sym, (x1,y1), font,1,(0, 0, 0), 1, cv2.LINE_AA)  
                sym,col,x1,y1=textPoints[name][1][0],textPoints[name][1][1],textPoints[name][1][2],textPoints[name][1][3]             
                cv2.putText(preview, sym, (x1,y1), font,0.5,col, 1, cv2.LINE_AA)  

def fill_stickers(frame,stickers,sides):    
    for side,colors in sides.items():
        num=0
        for x,y in stickers[side]:
            cv2.rectangle(frame,(x,y),(x+40,y+40),color[colors[num]],-1)
            num+=1

def calibrate_color(color):
    print ("color " + color+ " identification started")
    hsv = identify_color()
    HSV_Colors[color] =hsv
    print ("color " + color+ " identification completed")

def ProceedCubeToNextColor(serialInst,go_string):
    serialInst.write(go_string.encode())

def calibrate_cube_colors(serialInst):
    calibrate_color("green")
    ProceedCubeToNextColor(serialInst,"Go")
    calibrate_color("yellow")
    ProceedCubeToNextColor(serialInst,"Go2")
    calibrate_color("blue")
    ProceedCubeToNextColor(serialInst,"Go3")
    calibrate_color("white")
    ProceedCubeToNextColor(serialInst,"Go4")
    calibrate_color("orange")
    ProceedCubeToNextColor(serialInst,"Go5")
    calibrate_color("red")
    ProceedCubeToNextColor(serialInst,"Go6")
    



def get_edge_colors(is_reversed):
    windowSize = 30 #dont increase more than 50
    curWindowPos = 0
    
    allCubicRawData = []
    for j in range(9):
        hsvRaw = []
        for i in range(windowSize):
            hsvRaw.append((0,0,0))
        allCubicRawData.append(hsvRaw)

    print_colors = False
    numOfRounds = 0
    start_time = time.time()
    while time.time() - start_time < time_to_calc_edge:
        exitWhile = False
        hsv=[]
        current_state=[]
        ret,img=cap.read()
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
        for k in range(9):
            if is_reversed == True:
                square_num = 8 -k
            else:
                square_num = k
            allCubicRawData[k][curWindowPos] = img[stickers['main'][square_num][1]+10][stickers['main'][square_num][0]+10]
                
            hsv.append(img[stickers['main'][square_num][1]+10][stickers['main'][square_num][0]+10])
            cv2.waitKey(5)

        curWindowPos +=1
        if (curWindowPos == windowSize):
            print ("completed round!")
            numOfRounds +=1
            curWindowPos = 0

        draw_stickers(img,stickers,'main')
        draw_stickers(img,stickers,'current')
        draw_color_nums(img)

        handle_preview_window()

        draw_hsv(img,stickers)
        
        a=0
        
        for x,y in stickers['current']:
            color_name=color_detect(hsv[a][0],hsv[a][1],hsv[a][2],print_colors)
            cv2.rectangle(img,(x,y),(x+30,y+30),color[color_name],-1)
            #if a==0:
            cv2.putText(img, str(hsv[a][0]) + " " + str(hsv[a][1]) + " " + str(hsv[a][2]), (x,y), cv2.FONT_HERSHEY_SIMPLEX,  0.2, (0,0,0), 1, cv2.LINE_AA)
            a+=1
            current_state.append(color_name)
    
        cv2.imshow('preview',preview)
        cv2.imshow('frame',img[0:500,0:500])

    edge = []
    for k in range(9):
        avarageHSVX = 0
        avarageHSVY = 0
        avarageHSVZ = 0 
        for j in range(windowSize):
            avarageHSVX += int(allCubicRawData[k][j][0])
            avarageHSVY += int(allCubicRawData[k][j][1])
            avarageHSVZ += int(allCubicRawData[k][j][2])
        avarageHSVX /= windowSize
        avarageHSVY /= windowSize
        avarageHSVZ /= windowSize

        avarageHSVX = int(avarageHSVX)
        avarageHSVY = int(avarageHSVY)
        avarageHSVZ = int(avarageHSVZ)       
        edge.append(color_detect(avarageHSVX,avarageHSVY,avarageHSVZ,False))
    print ("num of rounds:" , numOfRounds)
    return edge

def recalc_face(face):
    side_string =""
    for cell_color in state[face]:
        side_string += sign_conv[cell_color]
    return side_string

def recalc_all_faces():
    front_side = recalc_face("front")#green
    down_side = recalc_face("down")#yellow
    back_side = recalc_face("back")#blue
    up_side = recalc_face("up")#white
    left_side = recalc_face("left")#orange
    right_side = recalc_face("right")#red
    all_cube = up_side+right_side+front_side+down_side+left_side+back_side
    return all_cube

def read_edge_from_camera(edge,is_reversed=False):
    print ("starting starting reading edge " + edge)
    side_string = ""
    state[edge]= get_edge_colors(is_reversed)
    for cell_color in state[edge]:
        side_string += sign_conv[cell_color]
    print("completed reading edge " + edge)
    return side_string

def read_cube_colors(serialInst):
    front_side = read_edge_from_camera("front")#green
    ProceedCubeToNextColor(serialInst,"Go")
    down_side = read_edge_from_camera("down")#yellow
    ProceedCubeToNextColor(serialInst,"Go2")
    back_side = read_edge_from_camera("back",True)#blue
    ProceedCubeToNextColor(serialInst,"Go3")
    up_side = read_edge_from_camera("up")#white
    ProceedCubeToNextColor(serialInst,"Go4")
    left_side = read_edge_from_camera("left")#orange
    ProceedCubeToNextColor(serialInst,"Go5")
    right_side = read_edge_from_camera("right")#red
    ProceedCubeToNextColor(serialInst,"Go6")

    all_cube = up_side+right_side+front_side+down_side+left_side+back_side
    print ("all cube " + all_cube)
    return all_cube

def handle_preview_window():
    draw_preview_stickers(preview,stickers)
    fill_stickers(preview,stickers,state)
    texton_preview_stickers(preview,stickers)

def identify_color():
    
    windowSize = 100
    curWindowPos = 0
    hsvRaw = []
    numOfRounds = 0
    for i in range(windowSize):
        hsvRaw.append((0,0,0))
    in_calibration = True
    print_colors = False

    start_time = time.time()
    
    while (time.time() - start_time < time_to_identify) :
    #while True:
        hsv=[]
        exitWhile = False
        current_state=[]
        ret,img=cap.read()
        # img=cv2.flip(img,1)
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #mask = np.zeros(frame.shape, dtype=np.uint8)   
        for k in range(9):

            hsvRaw[curWindowPos] = img[stickers['main'][k][1]+10][stickers['main'][k][0]+10]
            #print(hsvRaw[curWindowPos])
            curWindowPos +=1
            if (curWindowPos == windowSize):
                numOfRounds+=1
                print ("completed round!")
                curWindowPos = 0
            
            #hsv.append((avarageHSVX,avarageHSVY,avarageHSVZ))
            hsv.append(img[stickers['main'][k][1]+10][stickers['main'][k][0]+10])
            cv2.waitKey(5)

        draw_stickers(img,stickers,'main')
        draw_stickers(img,stickers,'current')
        draw_color_nums(img)

        handle_preview_window()
        
        cv2.imshow('preview',preview)
        cv2.imshow('frame',img[0:500,0:500])

    avarageHSVX = 0
    avarageHSVY = 0
    avarageHSVZ = 0 
    
    for j in range(windowSize):
        avarageHSVX += int(hsvRaw[j][0])
        avarageHSVY += int(hsvRaw[j][1])
        avarageHSVZ += int(hsvRaw[j][2])
    
    avarageHSVX /= windowSize
    avarageHSVY /= windowSize
    avarageHSVZ /= windowSize

    avarageHSVX = int(avarageHSVX)
    avarageHSVY = int(avarageHSVY)
    avarageHSVZ = int(avarageHSVZ)       
    print ("num of rounds:" , numOfRounds)
    return (avarageHSVX,avarageHSVY,avarageHSVZ)


def point_inside_rect(point, rect):
    x, y = point
    rect_x, rect_y, rect_width, rect_height = rect
    if rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height:
        return True
    else:
        return False

def click_and_crop(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDOWN:
            for side in all_states:
                square_num = 0
                for square in stickers[side]:
                    square_num+=1
                    if point_inside_rect((x,y),(square[0],square[1],40,40)):
                        state[side][square_num-1] = all_colors[(all_colors.index(state[side][square_num-1])+1)%6]
                        print(side,square_num)


	


def init_camera():
    preview = np.zeros((700,800,3), np.uint8)  
    global cap
    cap =cv2.VideoCapture(0)
    cv2.namedWindow('preview')
    cv2.setMouseCallback("preview", click_and_crop)
    start_time = time.time()
    while time.time() - start_time < 4:
        refresh_all_windows()
        cv2.waitKey(2)

"""


def process(operation):
    replace={
                "F":[rotate,'front'],
                "F2":[rotate,'front','front'],
                "F'":[revrotate,'front'],
                "U":[rotate,'up'],
                "U2":[rotate,'up','up'],
                "U'":[revrotate,'up'],
                "L":[rotate,'left'],
                "L2":[rotate,'left','left'],
                "L'":[revrotate,'left'],
                "R":[rotate,'right'],
                "R2":[rotate,'right','right'],
                "R'":[revrotate,'right'],
                "D":[rotate,'down'],
                "D2":[rotate,'down','down'],
                "D'":[revrotate,'down'],
                "B":[rotate,'back'],
                "B2":[rotate,'back','back'],
                "B'":[revrotate,'back']           
    }    
    a=0
    for i in operation:
        for j in range(len(replace[i])-1):
            replace[i][0](replace[i][j+1])
        cv2.putText(preview, i, (700,a+50), font,1,(0,255,0), 1, cv2.LINE_AA)  
        fill_stickers(preview,stickers,state)
        solution.append(preview)
        cv2.imshow('solution',preview)
        cv2.waitKey()
        cv2.putText(preview, i, (700,50), font,1,(0,0,0), 1, cv2.LINE_AA)
        


def close_CV()
    cv2.destroyAllWindows()
"""

"""if __name__=='__main__':

    preview = np.zeros((700,800,3), np.uint8)

    windowSize = 100
    curWindowPos = 0
    hsvRaw = []

    for i in range(windowSize):
        hsvRaw.append((0,0,0))
    in_calibration = True
    print_colors = False
    while True:
        hsv=[]
        current_state=[]
        ret,img=cap.read()
        # img=cv2.flip(img,1)
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = np.zeros(frame.shape, dtype=np.uint8)   


        
        for i in range(9):
            hsvRaw[curWindowPos] = img[stickers['main'][i][1]+10][stickers['main'][i][0]+10]

            avarageHSVX = 0
            avarageHSVY = 0
            avarageHSVZ = 0
            for j in range(windowSize):
                avarageHSVX += hsvRaw[j][0]
                avarageHSVY += hsvRaw[j][1]
                avarageHSVZ += hsvRaw[j][2]
            avarageHSVX /= windowSize
            avarageHSVY /= windowSize
            avarageHSVZ /= windowSize

            avarageHSVX = int(avarageHSVX)
            avarageHSVY = int(avarageHSVY)
            avarageHSVZ = int(avarageHSVZ)
            

            #hsv.append((avarageHSVX,avarageHSVY,avarageHSVZ))
            hsv.append(img[stickers['main'][i][1]+10][stickers['main'][i][0]+10])
            #was[AB]: hsv.append(frame[stickers['main'][i][1]+10][stickers['main'][i][0]+10])
        
        draw_stickers(img,stickers,'main')
        draw_stickers(img,stickers,'current')
        draw_color_nums(img)
        draw_preview_stickers(preview,stickers)
        draw_hsv(img,stickers)
        fill_stickers(preview,stickers,state)
        texton_preview_stickers(preview,stickers)

        a=0
        if in_calibration == False:
            for x,y in stickers['current']:
                color_name=color_detect(hsv[a][0],hsv[a][1],hsv[a][2],print_colors)
                cv2.rectangle(img,(x,y),(x+30,y+30),color[color_name],-1)
                #if a==0:
                cv2.putText(img, str(hsv[a][0]) + " " + str(hsv[a][1]) + " " + str(hsv[a][2]), (x,y), cv2.FONT_HERSHEY_SIMPLEX,  0.2, (0,0,0), 1, cv2.LINE_AA)
                a+=1
                current_state.append(color_name)
        
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
        elif k ==ord('r'):
            HSV_Colors['red'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('g'):
            HSV_Colors['green'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('b'):
            HSV_Colors['blue'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('w'):
            HSV_Colors['white'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('o'):
            HSV_Colors['orange'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('y'):
            HSV_Colors['yellow'] = (int(hsv[a][0]),int(hsv[a][1]),int(hsv[a][2]))
        elif k ==ord('d'):
            in_calibration = False
        elif k ==ord('p'):
            print_colors = not print_colors


        elif k == ord('\r'):
            # process(["R","R'"])
            if len(set(check_state))==6:    
                try:
                    solved=solve(state)
                    if solved:
                        operation=solved.split(' ')
                        process(operation)
                except:
                    print("error in side detection ,you may do not follow sequence or some color not detected well.Try again")
            else:
                print("all side are not scanned check other window for finding which left to be scanned?")
                print("left to scan:",6-len(set(check_state)))
        cv2.imshow('preview',preview)
        cv2.imshow('frame',img[0:500,0:500])
        curWindowPos +=1
        if (curWindowPos == windowSize):
            curWindowPos = 0


    cv2.destroyAllWindows()
"""
"""
def revrotate(side):
    main=state[side]
    front=state['front']
    left=state['left']
    right=state['right']
    up=state['up']
    down=state['down']
    back=state['back']
    
    if side=='front':
        left[2],left[5],left[8],up[6],up[7],up[8],right[0],right[3],right[6],down[0],down[1],down[2]=up[8],up[7],up[6],right[0],right[3],right[6],down[2],down[1],down[0],left[2],left[5],left[8]
    elif side=='up':
        left[0],left[1],left[2],back[0],back[1],back[2],right[0],right[1],right[2],front[0],front[1],front[2]=back[0],back[1],back[2],right[0],right[1],right[2],front[0],front[1],front[2],left[0],left[1],left[2]
    elif side=='down':
        left[6],left[7],left[8],back[6],back[7],back[8],right[6],right[7],right[8],front[6],front[7],front[8]=front[6],front[7],front[8],left[6],left[7],left[8],back[6],back[7],back[8],right[6],right[7],right[8]
    elif side=='back':
        left[0],left[3],left[6],up[0],up[1],up[2],right[2],right[5],right[8],down[6],down[7],down[8]=down[6],down[7],down[8],left[6],left[3],left[0],up[0],up[1],up[2],right[8],right[5],right[2] 
    elif side=='left':
        front[0],front[3],front[6],down[0],down[3],down[6],back[2],back[5],back[8],up[0],up[3],up[6]=down[0],down[3],down[6],back[8],back[5],back[2],up[0],up[3],up[6],front[0],front[3],front[6]
    elif side=='right':
        front[2],front[5],front[8],down[2],down[5],down[8],back[0],back[3],back[6],up[2],up[5],up[8]=up[2],up[5],up[8],front[2],front[5],front[8],down[8],down[5],down[2],back[6],back[3],back[0]

    main[0],main[1],main[2],main[3],main[4],main[5],main[6],main[7],main[8]=main[2],main[5],main[8],main[1],main[4],main[7],main[0],main[3],main[6]
def rotate(side):
    main=state[side]
    front=state['front']
    left=state['left']
    right=state['right']
    up=state['up']
    down=state['down']
    back=state['back']
    
    if side=='front':
        left[2],left[5],left[8],up[6],up[7],up[8],right[0],right[3],right[6],down[0],down[1],down[2]=down[0],down[1],down[2],left[8],left[5],left[2],up[6],up[7],up[8],right[6],right[3],right[0] 
    elif side=='up':
        left[0],left[1],left[2],back[0],back[1],back[2],right[0],right[1],right[2],front[0],front[1],front[2]=front[0],front[1],front[2],left[0],left[1],left[2],back[0],back[1],back[2],right[0],right[1],right[2]
    elif side=='down':
        left[6],left[7],left[8],back[6],back[7],back[8],right[6],right[7],right[8],front[6],front[7],front[8]=back[6],back[7],back[8],right[6],right[7],right[8],front[6],front[7],front[8],left[6],left[7],left[8]
    elif side=='back':
        left[0],left[3],left[6],up[0],up[1],up[2],right[2],right[5],right[8],down[6],down[7],down[8]=up[2],up[1],up[0],right[2],right[5],right[8],down[8],down[7],down[6],left[0],left[3],left[6] 
    elif side=='left':
        front[0],front[3],front[6],down[0],down[3],down[6],back[2],back[5],back[8],up[0],up[3],up[6]=up[0],up[3],up[6],front[0],front[3],front[6],down[6],down[3],down[0],back[8],back[5],back[2]
    elif side=='right':
        front[2],front[5],front[8],down[2],down[5],down[8],back[0],back[3],back[6],up[2],up[5],up[8]=down[2],down[5],down[8],back[6],back[3],back[0],up[8],up[5],up[2],front[2],front[5],front[8]

    main[0],main[1],main[2],main[3],main[4],main[5],main[6],main[7],main[8]=main[6],main[3],main[0],main[7],main[4],main[1],main[8],main[5],main[2]

def solve(state):
    raw=''
    for i in state:
        for j in state[i]:
            raw+=sign_conv[j]
   	#print("answer:",Cube.solve(raw))
    #return Cube.solve(raw)

    """