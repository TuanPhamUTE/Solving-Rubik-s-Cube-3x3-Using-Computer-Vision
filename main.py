# Import numpy as opencv library
import numpy as np
import cv2 as cv
# Import rubik solver library
from rubik_solver import utils
  
# Capturing video through webcam
cap = cv.VideoCapture(1,cv.CAP_DSHOW)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
    
hsv_color = {'yellow': ([30,47,172],[60,190,255]),
             'green':  ([62,83,109],[81,255,255]),
             'blue':   ([88,117,97],[112,255,255]),
             'red':    ([0, 156, 57],[10, 255, 136], [160, 182, 89],[179, 255, 255]),
             'white':  ([0,0,166],[179,59,255]),
             'orange': ([0,30,186],[25,255,255])}



bgr_color_box = {'y': (0,255,255),
                 'g': (0,255,0),
                 'b': (255,0,0), 
                 'r': (255,0,255),
                 'w': (255,255,255),
                 'o': (255,255,0)}

def hsv_processing(input_frame, color):
    gauss_filter = cv.GaussianBlur(input_frame, (3,3), 0)
    hsv_frame = cv.cvtColor(gauss_filter, cv.COLOR_BGR2HSV)
    
    if color == 'red':
        mask_red1 = cv.inRange(hsv_frame, np.array(hsv_color[color][0], np.uint8), np.array(hsv_color[color][1], np.uint8))
        mask_red2 = cv.inRange(hsv_frame, np.array(hsv_color[color][2], np.uint8), np.array(hsv_color[color][3], np.uint8))
        mask = mask_red1 | mask_red2
    else:
        mask = cv.inRange(hsv_frame, np.array(hsv_color[color][0], np.uint8), np.array(hsv_color[color][1], np.uint8))
    return mask

def morphology_processing(input_frame):
    # Create kernel for opening 
    kernel_opening = cv.getStructuringElement(cv.MORPH_RECT,(3,3))
    # Create kernel for closing
    kernel_closing = cv.getStructuringElement(cv.MORPH_RECT,(5,5))
    # Remove noise
    opening = cv.morphologyEx(input_frame, cv.MORPH_OPEN, kernel_opening, iterations=1)
    # Fill Small Hold Noise
    closing = cv.morphologyEx(opening, cv.MORPH_CLOSE, kernel_closing, iterations=5)
    # Bitwise And
    res = cv.bitwise_and(input_frame, input_frame,mask = closing)
    
    return res

def findContours_Processing(input_frame, bgr_color, color_lst):
    contours, hierarchy = cv.findContours(input_frame,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    min_area = 3800
    max_area = 20000
    for pic, contour in enumerate(contours):
        Area = cv.contourArea(contour)
        if(Area > min_area and Area < max_area):
            # Find Centroid
            (x,y),radius = cv.minEnclosingCircle(contour)
            center = (int(x),int(y))
            cv.circle(frame,center,1,(0,0,0),5)
            color_lst.append([bgr_color, int(x), int(y)])


            # Draw bounding box
            (x, y, w, h) = cv.boundingRect(contour)
            cv.rectangle(frame, (x,y), (x+w,y+h), bgr_color_box[bgr_color], 2)


def sort_cell(color_lst, color_str, save_color_lst):
    temp = 0
    # Sort Y
    for i in range(len(color_lst)):
        for j in range(i+1, len(color_lst)):
            if (color_lst[i][2] > color_lst[j][2]):
                temp = color_lst[i]
                color_lst[i] = color_lst[j] 
                color_lst[j] = temp   
    # Sort X
    n = 0
    for p in range(0,3):
        for i in range(n,n+3):
            for j in range(i+1, n+3):
                if (color_lst[i][1] > color_lst[j][1]):
                    temp = color_lst[i]
                    color_lst[i] = color_lst[j] 
                    color_lst[j] = temp
                
        n+=3
        
    for i in range(len(color_lst)):
        color_str += color_lst[i][0]
        save_color_lst.append(color_lst[i][0])
        
    return color_lst, color_str, save_color_lst

def help_to_scan_6Faces(input_frame,index): 
    text_point = (2,12)
    color = (255,255,255)
    if index == 1: 
        cv.putText(input_frame, "yellow center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    elif index == 2: 
        cv.putText(input_frame, "blue center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    elif index == 3: 
        cv.putText(input_frame, "red center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    elif index == 4: 
        cv.putText(input_frame, "green center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    elif index == 5: 
        cv.putText(input_frame, "orange center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    elif index == 6: 
        cv.putText(input_frame, "white center point", text_point, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color)
    else:
        pass
    
def rotation_arrow(input_frame, color_list, index_p1, index_p2, index_p3, index_p4):
    color = (0,255,0)
    tip_length = 0.1
    thicknesss = 5
    # Get point to draw
    p1 = (color_list[index_p1][1], color_list[index_p1][2])
    p2 = (color_list[index_p2][1], color_list[index_p2][2])
    p3 = (color_list[index_p3][1], color_list[index_p3][2])
    p4 = (color_list[index_p4][1], color_list[index_p4][2])
    # Draw arrow
    cv.arrowedLine(input_frame, p1, p2, color,thicknesss, tipLength= tip_length) 
    cv.arrowedLine(input_frame, p2, p3, color,thicknesss, tipLength= tip_length) 
    cv.arrowedLine(input_frame, p3, p4, color,thicknesss, tipLength= tip_length) 
    cv.arrowedLine(input_frame, p4, p1, color,thicknesss, tipLength= tip_length)

def one_arrow_line(input_frame, color_list, index_p1, index_p2):
    color = (0,255,0)
    tip_length = 0.1
    thicknesss = 5
    # set up 2 points
    p1 = (color_list[index_p1][1], color_list[index_p1][2])
    p2 = (color_list[index_p2][1], color_list[index_p2][2])
    # Draw arrow
    cv.arrowedLine(input_frame, p1, p2, color, thicknesss, tipLength = tip_length)

def three_arrow_line(input_frame, color_list, index_p1, index_p2, index_p3, index_p4, index_p5, index_p6):
    color = (0,255,0)
    tip_length = 0.1
    thicknesss = 5
    # Set up 6 points
    p1 = (color_list[index_p1][1], color_list[index_p1][2])
    p2 = (color_list[index_p2][1], color_list[index_p2][2])
    p3 = (color_list[index_p3][1], color_list[index_p3][2])
    p4 = (color_list[index_p4][1], color_list[index_p4][2])
    p5 = (color_list[index_p5][1], color_list[index_p5][2])
    p6 = (color_list[index_p6][1], color_list[index_p6][2])
    # Draw arrow
    cv.arrowedLine(input_frame, p1, p2, color, thicknesss, tipLength = tip_length)
    cv.arrowedLine(input_frame, p3, p4, color, thicknesss, tipLength = tip_length)
    cv.arrowedLine(input_frame, p5, p6, color, thicknesss, tipLength = tip_length)

def get_solving_steps(six_face_string):
    # Using kociemba algorithm to solve rubik
    rubik_step_lst = utils.solve(six_face_string, 'Kociemba')
    for rubik_step in rubik_step_lst:
        rubik_step = str(rubik_step)
        if rubik_step == "B":
            index = rubik_step_lst.index(rubik_step)
            rubik_step_lst.remove(rubik_step)
            rubik_step_lst.insert(index, "up")
            rubik_step_lst.insert(index, "U")
            rubik_step_lst.insert(index, "down") 
        elif len(rubik_step) > 1:
            if rubik_step[1] == '2':
                s = rubik_step[0]
                index = rubik_step_lst.index(rubik_step)
                rubik_step_lst.remove(rubik_step)
                rubik_step_lst.insert(index,s)
                rubik_step_lst.insert(index,s)
            elif rubik_step == "B'":
                index = rubik_step_lst.index(rubik_step)
                rubik_step_lst.remove(rubik_step)
                rubik_step_lst.insert(index, "up")
                rubik_step_lst.insert(index, "U'")
                rubik_step_lst.insert(index, "down")
        else:
            continue
    return rubik_step_lst
    
    

index = 1 
main = 150
solve_index = 0
six_face_string = ''
temp_list = []  
six_face_list = []   
check_duplicate = 'nothing here'
mode = 0
index_yellow = 0
index_blue = 1 
index_red = 2
index_green = 3
index_orange = 4 
index_white = 5
# Start a while loop
n = 0
while(True):
    # Reading the video from the
    # webcam in image by frames
    ret, frame = cap.read()
    if not cap.isOpened():
            print("Cannot open camera")
            exit()
            
    frame = cv.resize(frame, (500,500))
    
    color_lst = []
    color_str = ''
    save_color_lst = []
    ######### DETECT COLOR AND FIND CONNTOURS #########
    # Modify hsv range
    red_mask = hsv_processing(frame,   'red')
    green_mask = hsv_processing(frame, 'green')
    blue_mask = hsv_processing(frame,  'blue')
    yellow_mask = hsv_processing(frame,'yellow')
    orange_mask = hsv_processing(frame,'orange')
    white_mask = hsv_processing(frame, 'white')
    # Morphology 
    red = morphology_processing(red_mask)
    green = morphology_processing(green_mask)
    blue = morphology_processing(blue_mask)
    yellow = morphology_processing(yellow_mask)
    orange = morphology_processing(orange_mask)
    white = morphology_processing(white_mask)
    # Find contours
    findContours_Processing(red,   'r', color_lst)
    findContours_Processing(green, 'g', color_lst)
    findContours_Processing(blue,  'b', color_lst)
    findContours_Processing(yellow,'y', color_lst)
    findContours_Processing(orange,'o', color_lst)
    findContours_Processing(white, 'w', color_lst)

    # Scan 6 faces first if index <7 (<=6)
    if index < 7:
        # Scan 6 faces first
        help_to_scan_6Faces(frame, index)
        if len(color_lst) == 9:
            # Sort cells (left to right and up to bottom)
            _, one_face_str, one_face_lst = sort_cell(color_lst, color_str, save_color_lst)
            if check_duplicate != one_face_str:
                check_duplicate = one_face_str
                # Add each face to big string
                six_face_string += one_face_str
                six_face_list.append(one_face_lst)
                print(index)
                print(one_face_str)
                print(six_face_string)
                print(six_face_list)
                index += 1
    elif index == 7:
        rubik_step = get_solving_steps(six_face_string)
        print(rubik_step)
        index += 1
    else:
        if n == 0:
            temp_list = six_face_list
            n = 1
            
        if len(color_lst) == 9:
            # Sort cells (left to right and up to bottom)
            color_list, one_face_string, one_face_list  = sort_cell(color_lst, color_str, save_color_lst)
            
            # Instructions for turning rubik
            if rubik_step[solve_index] == 'U':
                if mode == 0:
                    if one_face_list[4] == 'r':
                        one_arrow_line(frame, color_list, 2, 0)
                        if n == 1:
                            # Update faces
                            main = index_yellow
                            temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                            temp_list[2][0],temp_list[2][1],temp_list[2][2],temp_list[1][0],temp_list[1][1],temp_list[1][2],temp_list[4][0],temp_list[4][1],temp_list[4][2],temp_list[3][0],temp_list[3][1],temp_list[3][2] = \
                            six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                            six_face_list[3][0],six_face_list[3][1],six_face_list[3][2],six_face_list[2][0],six_face_list[2][1],six_face_list[2][2],six_face_list[1][0],six_face_list[1][1],six_face_list[1][2],six_face_list[4][0],six_face_list[4][1],six_face_list[4][2]
                            n = 2
                            
                    if one_face_list == temp_list[2]:
                        solve_index += 1
                        six_face_list = temp_list
                        n = 1
                        print(solve_index)
                        print(temp_list)
                elif mode == 1:
                    if one_face_list[4] == 'y':
                        one_arrow_line(frame, color_list, 2, 0)
                        if n == 1:
                            # Update faces
                            main = index_orange
                            temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                            temp_list[0][0],temp_list[0][1],temp_list[0][2],temp_list[1][0],temp_list[1][3],temp_list[1][6],temp_list[5][6],temp_list[5][7],temp_list[5][8],temp_list[3][2],temp_list[3][5],temp_list[3][8] = \
                            six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                            six_face_list[3][2],six_face_list[3][5],six_face_list[3][8],six_face_list[0][2],six_face_list[0][1],six_face_list[0][0],six_face_list[1][0],six_face_list[1][3],six_face_list[1][6],six_face_list[5][8],six_face_list[5][7],six_face_list[5][6]
                            n = 2
                            
                    if one_face_list == temp_list[0]:
                        solve_index += 1
                        six_face_list = temp_list
                        n = 1
                        print(solve_index)
                        print(temp_list)
                    
                
            elif rubik_step[solve_index] == 'D':
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 6, 8)
                    if n == 1:
                        # Update faces
                        main = index_white
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][6],temp_list[2][7],temp_list[2][8],temp_list[3][6],temp_list[3][7],temp_list[3][8],temp_list[4][6],temp_list[4][7],temp_list[4][8],temp_list[1][6],temp_list[1][7],temp_list[1][8] = \
                        six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                        six_face_list[1][6],six_face_list[1][7],six_face_list[1][8],six_face_list[2][6],six_face_list[2][7],six_face_list[2][8],six_face_list[3][6],six_face_list[3][7],six_face_list[3][8],six_face_list[4][6],six_face_list[4][7],six_face_list[4][8]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == 'R':
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 8, 2)
                    if n == 1:
                        # Update faces
                        main = index_green
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][2],temp_list[2][5],temp_list[2][8],temp_list[0][2],temp_list[0][5],temp_list[0][8],temp_list[4][6],temp_list[4][3],temp_list[4][0],temp_list[5][2],temp_list[5][5],temp_list[5][8] = \
                        six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                        six_face_list[5][2],six_face_list[5][5],six_face_list[5][8],six_face_list[2][2],six_face_list[2][5],six_face_list[2][8],six_face_list[0][2],six_face_list[0][5],six_face_list[0][8],six_face_list[4][6],six_face_list[4][3],six_face_list[4][0]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == 'L':
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 0, 6)
                    if n == 1:
                        # Update faces
                        main = index_blue
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][0],temp_list[2][3],temp_list[2][6],temp_list[5][0],temp_list[5][3],temp_list[5][6],temp_list[4][8],temp_list[4][5],temp_list[4][2],temp_list[0][0],temp_list[0][3],temp_list[0][6] = \
                        six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                        six_face_list[0][0],six_face_list[0][3],six_face_list[0][6],six_face_list[2][0],six_face_list[2][3],six_face_list[2][6],six_face_list[5][0],six_face_list[5][3],six_face_list[5][6],six_face_list[4][8],six_face_list[4][5],six_face_list[4][2]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == 'F':
                if one_face_list[4] == 'r':
                    rotation_arrow(frame, color_list, 3, 1, 5, 7)
                    if n == 1:
                        # Update faces
                        main = index_red
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[0][6],temp_list[0][7],temp_list[0][8],temp_list[3][0],temp_list[3][3],temp_list[3][6],temp_list[5][0],temp_list[5][1],temp_list[5][2],temp_list[1][2],temp_list[1][5],temp_list[1][8] = \
                        six_face_list[main][6],six_face_list[main][3],six_face_list[main][0],six_face_list[main][7],six_face_list[main][4],six_face_list[main][1],six_face_list[main][8],six_face_list[main][5],six_face_list[main][2], \
                        six_face_list[1][8],six_face_list[1][5],six_face_list[1][2],six_face_list[0][6],six_face_list[0][7],six_face_list[0][8],six_face_list[3][6],six_face_list[3][3],six_face_list[3][0],six_face_list[5][0],six_face_list[5][1],six_face_list[5][2]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == "U'":
                if mode == 0:
                    if one_face_list[4] == 'r':
                        one_arrow_line(frame, color_list, 0, 2)
                        if n == 1:
                            # Update faces
                            main = index_yellow
                            temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                            temp_list[2][0],temp_list[2][1],temp_list[2][2],temp_list[3][0],temp_list[3][1],temp_list[3][2],temp_list[4][0],temp_list[4][1],temp_list[4][2],temp_list[1][0],temp_list[1][1],temp_list[1][2] = \
                            six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                            six_face_list[1][0],six_face_list[1][1],six_face_list[1][2],six_face_list[2][0],six_face_list[2][1],six_face_list[2][2],six_face_list[3][0],six_face_list[3][1],six_face_list[3][2],six_face_list[4][0],six_face_list[4][1],six_face_list[4][2]
                            n = 2
                            
                    if one_face_list == temp_list[2]:
                        solve_index += 1
                        six_face_list = temp_list
                        n = 1
                        print(solve_index)
                        print(temp_list)
                elif mode == 1:
                    if one_face_list[4] == 'y':
                        one_arrow_line(frame, color_list, 0, 2)
                        if n == 1:
                            # Update faces
                            main = index_orange
                            temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                            temp_list[0][0],temp_list[0][1],temp_list[0][2],temp_list[3][2],temp_list[3][5],temp_list[3][8],temp_list[5][6],temp_list[5][7],temp_list[5][8],temp_list[1][0],temp_list[1][3],temp_list[1][6] = \
                            six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                            six_face_list[1][6],six_face_list[1][3],six_face_list[1][0],six_face_list[0][0],six_face_list[0][1],six_face_list[0][2],six_face_list[3][8],six_face_list[3][5],six_face_list[3][2],six_face_list[5][6],six_face_list[5][7],six_face_list[5][8]
                            n = 2
                            
                    if one_face_list == temp_list[0]:
                        solve_index += 1
                        six_face_list = temp_list
                        n = 1
                        print(solve_index)
                        print(temp_list)
                
            elif rubik_step[solve_index] == "D'":
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 8, 6)
                    if n == 1:
                        # Update faces
                        main = index_white
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][6],temp_list[2][7],temp_list[2][8],temp_list[1][6],temp_list[1][7],temp_list[1][8],temp_list[4][6],temp_list[4][7],temp_list[4][8],temp_list[3][6],temp_list[3][7],temp_list[3][8] = \
                        six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                        six_face_list[3][6],six_face_list[3][7],six_face_list[3][8],six_face_list[2][6],six_face_list[2][7],six_face_list[2][8],six_face_list[1][6],six_face_list[1][7],six_face_list[1][8],six_face_list[4][6],six_face_list[4][7],six_face_list[4][8]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == "R'":
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 2, 8)
                    if n == 1:
                        # Update faces
                        main = index_green
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][2],temp_list[2][5],temp_list[2][8],temp_list[5][2],temp_list[5][5],temp_list[5][8],temp_list[4][6],temp_list[4][3],temp_list[4][0],temp_list[0][2],temp_list[0][5],temp_list[0][8] = \
                        six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                        six_face_list[0][2],six_face_list[0][5],six_face_list[0][8],six_face_list[2][2],six_face_list[2][5],six_face_list[2][8],six_face_list[5][2],six_face_list[5][5],six_face_list[5][8],six_face_list[4][6],six_face_list[4][3],six_face_list[4][0]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == "L'":
                if one_face_list[4] == 'r':
                    one_arrow_line(frame, color_list, 6, 0)
                    if n == 1:
                        # Update faces
                        main = index_blue
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[2][0],temp_list[2][3],temp_list[2][6],temp_list[0][0],temp_list[0][3],temp_list[0][6],temp_list[4][8],temp_list[4][5],temp_list[4][2],temp_list[5][0],temp_list[5][3],temp_list[5][6] = \
                        six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                        six_face_list[5][0],six_face_list[5][3],six_face_list[5][6],six_face_list[2][0],six_face_list[2][3],six_face_list[2][6],six_face_list[0][0],six_face_list[0][3],six_face_list[0][6],six_face_list[4][8],six_face_list[4][5],six_face_list[4][2]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
                
            elif rubik_step[solve_index] == "F'":
                if one_face_list[4] == 'r':
                    rotation_arrow(frame, color_list, 3, 7, 5, 1)
                    if n == 1:
                        # Update faces
                        main = index_red
                        temp_list[main][0],temp_list[main][1],temp_list[main][2],temp_list[main][3],temp_list[main][4],temp_list[main][5],temp_list[main][6],temp_list[main][7],temp_list[main][8], \
                        temp_list[0][6],temp_list[0][7],temp_list[0][8],temp_list[1][2],temp_list[1][5],temp_list[1][8],temp_list[5][0],temp_list[5][1],temp_list[5][2],temp_list[3][0],temp_list[3][3],temp_list[3][6] = \
                        six_face_list[main][2],six_face_list[main][5],six_face_list[main][8],six_face_list[main][1],six_face_list[main][4],six_face_list[main][7],six_face_list[main][0],six_face_list[main][3],six_face_list[main][6], \
                        six_face_list[3][0],six_face_list[3][3],six_face_list[3][6],six_face_list[0][8],six_face_list[0][7],six_face_list[0][6],six_face_list[1][2],six_face_list[1][5],six_face_list[1][8],six_face_list[5][2],six_face_list[5][1],six_face_list[5][0]
                        n = 2
                        
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    six_face_list = temp_list
                    n = 1
                    print(solve_index)
                    print(temp_list)
            
            elif rubik_step[solve_index] == "up":
                if one_face_list[4] == 'y':
                    three_arrow_line(frame, color_list, 6, 0, 7, 1, 8, 2)
                
                if one_face_list == temp_list[2]:
                    solve_index += 1
                    mode = 0
                    print(solve_index)
                    print(temp_list)
            
            elif rubik_step[solve_index] == "down":
                if one_face_list[4] == 'r':
                    three_arrow_line(frame, color_list, 0, 6, 1, 7, 2, 8)
                
                if one_face_list == temp_list[0]:
                    solve_index += 1
                    mode = 1
                    print(solve_index)
                    print(temp_list)
            
            elif rubik_step[solve_index] == "right":
                three_arrow_line(frame, color_list, 0, 2, 3, 5, 6, 8)
            
            elif rubik_step[solve_index] == "left":
                three_arrow_line(frame, color_list, 2, 0, 5, 3, 8, 6)
            
            if solve_index >= len(rubik_step):
                solve_index = len(rubik_step) - 1
                print('**********************CONGRATULATION! YOUR RUBIK IS COMPLETELY SOLVED**********************')
                break
        
    # Program Termination
    cv.imshow("Rubik Solver System", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv.destroyAllWindows()
        break 