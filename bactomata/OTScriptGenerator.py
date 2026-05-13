import sys, os, random, time, shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import ipywidgets as widgets
from IPython.display import display

from DataLoader import *


################

    


            
def save_matrix_to_file(matrix, file_path):
    with open(file_path, 'w') as file:
        for row in matrix:
            line = ' '.join(row)  # Join the elements of the row into a single string
            file.write(line + '\n')  # Write the line to the file


def create_inoculation_layout_input(default_matrix=None):
    input_fields = []
    nrows = 8
    ncols = 12

    for i in range(nrows):
        row = []
        for j in range(ncols):
            # Get value from default_matrix if available, else set to empty string
            default_value = default_matrix[i][j] if default_matrix and i < len(default_matrix) and j < len(default_matrix[i]) else ''
            text = widgets.Text(value=default_value, placeholder='0', description='', disabled=False, layout=widgets.Layout(width='60px'))
            row.append(text)
        input_fields.append(row)

    # Create a grid layout
    grid_layout = widgets.GridspecLayout(nrows, ncols)
    for i in range(nrows):
        for j in range(ncols):
            grid_layout[i, j] = input_fields[i][j]

    display(grid_layout)
    return input_fields

def get_inoculation_layout_data(inoculation_layout_inputs):
    layout_data = []
    for row in inoculation_layout_inputs:
        row_data = [field.value if field.value != '' else '0' for field in row]
        layout_data.append(row_data)
    return layout_data




def get_M_data(matrix_inputs):
    matrix_data = []
    for row in matrix_inputs:
        # Replace empty values with '0'
        row_data = [field.value if field.value != '' else '0' for field in row]
        matrix_data.append(row_data)
    return matrix_data

def get_unique_keys(matrix_inputs):
    # Retrieve the matrix data
    matrix_data = get_M_data(matrix_inputs)

    # Flatten the matrix into a single list
    all_keys = [key for row in matrix_data for key in row]

    # Get the set of unique keys
    unique_keys = set(all_keys)

    return unique_keys



def load_trough_layout_from_file(file_path):
    layout_data = []
    with open(file_path, 'r') as file:
        for line in file:
            row_data = line.strip().split()
            layout_data.append(row_data)
    return layout_data

def get_trough_layout_data(trough_layout_inputs):
    layout_data = []
    for row in trough_layout_inputs:
        row_data = [widget.value if widget.value != '' else '0' for widget in row]
        row_string = ' '.join(row_data)
        layout_data.append(row_string)

    layout_string = '\n'.join(layout_data)
    return layout_string


def save_trough_layout_to_file(layout_string, file_path):
    with open(file_path, 'w') as file:
        file.write(layout_string)


def load_trough_layout_from_file(file_path):
    layout_data = []
    with open(file_path, 'r') as file:
        for line in file:
            row_data = line.strip().split()
            layout_data.append(row_data)
    return layout_data


def create_trough_layout_input(predefined_data=None):
    input_fields = []
    trough_layout_structure = [4, 4, 2]  # Number of columns in each row
    well_labels = {
        (0, 0): 'A1', (0, 1): 'A2', (0, 2): 'A3', (0, 3): 'A4',
        (1, 0): 'B1', (1, 1): 'B2', (1, 2): 'B3', (1, 3): 'B4',
        (2, 0): 'C1', (2, 1): 'C2'
    }

    for r, row_count in enumerate(trough_layout_structure):
        row = []
        for c in range(row_count):
            label = well_labels.get((r, c), '')
            value = predefined_data[r][c] if predefined_data and r < len(predefined_data) and c < len(predefined_data[r]) else ''
            text = widgets.Text(value=value, placeholder='0', description=label, disabled=False, layout=widgets.Layout(width='200px'))
            row.append(text)
        input_fields.append(row)

    # Create a layout for the input fields
    grid_layout = widgets.VBox([widgets.HBox(r) for r in input_fields])
    display(grid_layout)
    return input_fields


############
def find_commands_by_plates_and_wells(instructions, plates, wells):
    matching_commands = []

    for instruction in instructions:
        if instruction['dispense_to_plate'] in plates and instruction['dispense_to_well'] in wells:
            matching_commands.append(instruction)

    return matching_commands



def get_previous_well_and_plate(current_well_index, current_plate, num_rows, num_cols, num_plates):
    # Total number of wells per plate
    wells_per_plate = num_rows * num_cols

    # If the current well is at the top of a column
    if current_well_index % num_rows == 0:
        # If it's the first well of the first plate, there is no previous well
        if current_well_index == 0 and current_plate == 1:
            return None, None

        # Calculate the column of the current well
        current_col = current_well_index // num_rows

        # If it's the first column, go to the last column of the previous plate
        if current_col == 0 and current_plate > 1:
            previous_plate = current_plate - 1
            previous_plate_col = num_cols - 1
            previous_plate_index = previous_plate_col * num_rows + (num_rows - 1)
            return previous_plate_index, previous_plate
        else:
            # Previous well is the last well of the previous column
            previous_plate_index = current_well_index - num_rows
            return previous_plate_index, current_plate

    # Otherwise, the previous well is just one index before the current one in the same column
    previous_plate_index = current_well_index - 1
    return previous_plate_index, current_plate

def calculate_row(well_index, num_cols):
    # Calculate the column number based on the well index
    # Assuming the numbering starts at 0 and goes row by row
    row = well_index // num_cols
    return row

def calculate_row_wells(row, num_cols, num_rows):
    # Calculate well indices incrementally over rows
    return [row + i*num_rows for i in range(num_cols)]

def calculate_previous_row_index(current_index, num_rows, num_cols):
    # Calculate the current row and column
    current_row = current_index % num_rows
    current_col = current_index // num_rows

    # Check if there is a previous row
    if current_row == 0:
        return None  # There is no previous row in the first row

    # Calculate the index of the well in the previous row
    previous_row_index = current_index - 1
    return previous_row_index




def toString(arr2d):
    """Return rows of matrix (of strings) as space-separated rows."""
    return ("\n".join("\t".join(row) for row in arr2d))

def submatsum(data,n,m):
    # return a matrix of shape (n,m)
    bs = data.shape[0]//n,data.shape[1]//m  # blocksize averaged over
    return np.reshape(np.array([np.sum(data[k1*bs[0]:(k1+1)*bs[0],k2*bs[1]:(k2+1)*bs[1]]) for k1 in range(n) for k2 in range(m)]),(n,m))


######################################
#I/O Functions 
def toFile(fileName, strOut):
    file_ = open(fileName, "w")
    file_.write(strOut)
    file_.close()
  

######################################
# Plate layout loader
#LOADS TREATMENT DICTIONARY FROM FILE
def loadTreatmentDict(params):

    fileDict = open(params['fileDictName'], 'r')
    treatment_dict=[]
    treatment_sources=[]

    dataDict = fileDict.readlines()
    for line in dataDict:

        line_dict = line.split()
        if len(treatment_sources)==0:
            for this_treatment in line_dict:
                if this_treatment!="KEY":
                    treatment_sources.append(this_treatment)
        else:
            thisKey=line_dict[0]
            thisVols=line_dict[1:len(treatment_sources)+1]
            
            this_dict=dict(zip(treatment_sources, thisVols))
            this_dict["KEY"]=thisKey

            treatment_dict.append(this_dict)
            
    return treatment_dict


#LOADS TROUGH LAYOUT FROM FILE
def loadTroughLayout(params):
    fileTroughLayout = open(params['fileTroughName'], 'r')

    num_wells=params['rows']*params['cols']
    trough_well = [x for x in range(num_wells)]  
    trough_key = ['0' for x in range(num_wells)] 
    trough_vol = [0 for x in range(num_wells)]  
    params_trough=dict()
    dataTroughLayout = fileTroughLayout.readlines()
    r=1; c=1;
    for line in dataTroughLayout:
        line_cols = line.split()
        for this_key in line_cols:
            well=r+(c-1)*8-1
            
            if r==1 or params['pipette_channels']==1:  #
                trough_key[well]=this_key
                if this_key!="0":
                    #For 15 and 50 mL tubes
                    if params['trough_type']=="tube-rack-15_50ml":
                        this_label=getLabelWell(well, params, trough=1)
                        if this_label=="A3" or this_label=="A4" or this_label=="B3" or this_label=="B4":
                            vol_trough=params['max_vol_trough'][1]
                        else:
                            vol_trough=params['max_vol_trough'][0]
                    #print("%s=%s"%(this_label,vol_trough))
                    trough_vol[well]=vol_trough
                c=c+1
        r=r+1
        c=1
    trough_layout=dict(zip(trough_well, trough_key))
    trough_layout_vol=dict(zip(trough_well, trough_vol))
    
    return (trough_layout,trough_layout_vol)

def getLabelWell(i, params, trough=0):
    if trough==1:
        plate_type=params['trough_type']
    else:
        plate_type=params['plate_type']

    label=""
    if plate_type=='tube-rack-15_50ml':
        if i==0:
            label="A1"
        elif i==1:
            label="B1" 
        elif i==2:
            label="C1"
        elif i==8:
            label="A2" 
        elif i==9:
            label="B2"
        elif i==10:
            label="C2" 
        elif i==16:
            label="A3"
        elif i==17:
            label="B3"
        elif i==24:
            label="A4"
        elif i==25:
            label="B4" 
    elif plate_type=="384-plate":
        
        rows=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
        cols=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']

        ic=int(i/16)
        ir=int(i%16)
        #print (i, ic, ir)
        label="%s%s"%(rows[ir],cols[ic])
        #print(label)
    else:         #96-well 
        rows=['A','B','C','D','E','F','G','H']
        cols=['1','2','3','4','5','6','7','8','9','10','11','12']

        ic=int(i/8)
        ir=int(i%8)

        label="%s%s"%(rows[ir],cols[ic])
    
    return label


#LOADS PLATE LAYOUT FROM FILE
def loadPlateLayout(thisFileLayoutName, params):
    
    #READ TROUGH LAYOUT
    (trough_layout,trough_layout_vol)=loadTroughLayout(params)
    
    treatment_dict=loadTreatmentDict(params)
    
    fileLayout = open(thisFileLayoutName, 'r')

    robot_instructions=[]

    dataLayout = fileLayout.readlines()
    p=1; r=1; c=1;
    numDispenses=0

    class Found(Exception): pass
    try:
        for line in dataLayout:
            if(len(line.split())==0):
                p=p+1
                r=0
                c=1

            line_cols = line.split()
            for this_key in line_cols:
                well=r+(c-1)*params['rows']-1
                if params['verbose']:
                  print("*** plate:%s pos:(%s,%s)\t [%s]"%(p,c, r,this_key))
                
                if r==1 or params['pipette_channels']==1:  #IF CHANNELS=8

                    #FIND KEY IN treatment_dict
                    for val in treatment_dict:
                        if this_key==val["KEY"]:

                            #FIND VOL>0
                            for source, vol in val.items():
                                if source!="KEY":
                                    if int(vol)>0:

                                        
                                        #If volume to aspirate is larger than tip volume do it N times <------
                                        aspirate_from=list(trough_layout.keys())[list(trough_layout.values()).index(source)]
                                        #trough_layout_vol[aspirate_from]=int(trough_layout_vol[aspirate_from])-int(vol)
                                        
                                        #if trough_layout_vol[aspirate_from]<float(params['max_vol_tip']):  #empty well in trough
                                        if trough_layout_vol[aspirate_from]<(float(params['min_vol_trough']) + float(params['max_vol_tip'])):  #empty well in trough
                                        
                                            trough_layout[aspirate_from]="0"
                                            if source in trough_layout.values():

                                                aspirate_from=list(trough_layout.keys())[list(trough_layout.values()).index(source)]
                                                #trough_layout_vol[aspirate_from]=int(trough_layout_vol[aspirate_from])-int(vol)
                                            else:
                                                raise ValueError("ERROR: NOT ENOUGH %s IN TROUGH!"%(source))

                                        
                                        num=divmod(float(vol),float(params['max_vol_tip']))
                                        num=int(num[0]+1.)  #Number of times this command should be repeated
                                        
                                        va=0
                                        #print("___ n=%s"%num)
                                        for n in range(0,num):
                                            nvol=min(int(vol)-va, params['max_vol_tip'])
                                            if nvol>0:
                                                trough_layout_vol[aspirate_from]=int(trough_layout_vol[aspirate_from])-nvol
                                                if params['verbose']:
                                                    print("aspirate %suL from trough well %s (Remaining: %suL)"%(nvol, aspirate_from,trough_layout_vol[aspirate_from]))
                                                
                                                numDispenses+=1
                                                if params['verbose']:
                                                    print("dispense %suL to plate %s well %s (%s) \n"%(nvol, p, well, numDispenses))
                                                
                                                va+=nvol


                                                this_instructions={"source":source,"aspirate_from_well":aspirate_from,"aspirate_vol":int(nvol),"dispense_to_plate":p,"dispense_to_well":well,"dispense_vol":int(nvol)}

                                                robot_instructions.append(this_instructions)
                                        
                c=c+1
            r=r+1
            c=1
    except Found:
        print(Found)
        
    #Prints volume used
    if params['verbose']:
        print("\nVolume remaining in trough:")
        for i, tube_vol in enumerate(trough_layout_vol):
            label=getLabelWell(i, params, trough=1)
            if label!="":
                print("\t%s: %s uL"%(label,trough_layout_vol[i]))
    
    return robot_instructions
        
def randomizePlate(fileLayoutName, fileRandLayoutName):
    fileLayout = open(fileLayoutName, 'r')
    dataLayout = fileLayout.readlines()
    p=1; r=1; c=1;
    
    w = params['rows'] 
    h = params['cols']
    M = [['x' for x in range(w)] for y in range(h)] 
    strM=''

    class Found(Exception): pass
    try:
        for line in dataLayout:
            if(len(line.split())==0):
                p=p+1
                r=0
                c=1
                
                print("\n------- Plate %s\n"%(p-1))
                show(M)
                print("\n------- Randomized Plate %s\n"%(p-1))
                Mr=shuffle2d(M)
                show(Mr)

                strM+='%s\n\n'%toString(Mr)
                

            line_cols = line.split()
            for this_key in line_cols:
                well=r+(c-1)*params['rows']-1
                
                #print("*** plate:%s pos:(%s,%s)\t [%s]"%(p,c, r,this_key))
                M[r-1][c-1]=this_key
                
                c=c+1
            r=r+1
            c=1
            
        print("\n------- Plate Layout %s:\n"%p)
        show(M)
        print("\n------- Randomized Plate Layout %s:\n"%p)
        Mr=shuffle2d(M)
        show(Mr)

        strM+='%s\n\n'%toString(Mr)
    
        file_ = open(fileRandLayoutName, "w")
        file_.write(strM)
        file_.close()
        
    except Found:
        print(Found)
    return ''
    
#RETURN ROBOT INSTRUCTIONS
def getRobotHeader(params):
    
    ret="from opentrons import Robot"
    ret+="\nfrom opentrons import containers, instruments"
    ret+="\nfrom itertools import chain"
    ret+="\n\nrobot = Robot()"
    ret+=("\n\np200rack = containers.load('tiprack-200ul', '%s', 'tiprack')"%(params['pos_tiprack']))
    ret+=("\ntrough = containers.load('%s','%s','trough')"%(params['trough_type'],params['pos_trough']))
    
    if params['trough_type']=="tube-rack-15_50ml":
        ret+="\nfor tube in trough:"
        ret+="\n\ttube.properties['height']+=50"
    
    for i, this_pos_plate in enumerate(params['pos_plates']):
        ret+=("\nplate%s = containers.load('%s','%s','plate-%s')"%((i+1), params['plate_type'],this_pos_plate, (i+1)))
    #ret+=("\ntrash = containers.load('point','%s','trash')"%(params['pos_trash']))
    ret+=("\np200 = instruments.Pipette(name='p200',trash_container=trash,tip_racks=[p200rack],min_volume=%s,axis='%s',channels=%s)"%(params['min_vol_tip'], params['pipette_axis'], params['pipette_channels']))
    ret+=("\n\np200.set_max_volume(%s)\n"%(params['max_vol_tip']))
    ret+"\n\n#robot.simulate()"
    
    return ret


#GENERATE AND RETURN ROBOT INSTRUCTIONS
def optimizeRobotInstructions(robot_instructions, params):
    ret=""
    (trough_layout,trough_layout_vol)=loadTroughLayout(params)

    #sorted_robot_instructions = sorted(robot_instructions, key=lambda k: (k['aspirate_from_well'],k['dispense_vol']))
    #sorted_robot_instructions = sorted(robot_instructions, key=lambda k: (k['source'],k['dispense_vol']))
    sorted_robot_instructions = sorted(robot_instructions, key=lambda k: (k['source'],k['dispense_to_plate'],k['dispense_vol']))
    
    
    numActions=1
    numTips=0
    
    tip_vol=0
    ret_dispense=""
    prev_source=""
    prev_source_type=""
    prev_aspirate_pos=0
    all_pos_plates=params['pos_plates']
    for inst in sorted_robot_instructions:
        
        this_source=getLabelWell(inst["aspirate_from_well"], params, trough=1)
        
        this_source_type=trough_layout[inst["aspirate_from_well"]]
        
        #DEFINE ASPIRATE POSITION IN TROUGH
        trough_layout_vol[inst["aspirate_from_well"]]=int(trough_layout_vol[inst["aspirate_from_well"]])-int(inst["aspirate_vol"])
        if params['trough_type']=="tube-rack-15_50ml":
            
            if this_source=="A3" or this_source=="A4" or this_source=="B3" or this_source=="B4":
                this_tube_vol=params['max_vol_trough'][1]
                ml2mm=(90.0*float(params['max_vol_trough'][1]))/50000.0
            else:
                this_tube_vol=params['max_vol_trough'][0]
                ml2mm=(90.0*float(params['max_vol_trough'][0]))/15000.0
                
            tube_pos=round(trough_layout_vol[inst["aspirate_from_well"]]*ml2mm/this_tube_vol)
            if params['verbose']:
                print("%s (%s) %s uL: %s mm"%(this_source, this_tube_vol, trough_layout_vol[inst["aspirate_from_well"]],tube_pos))
            aspirate_pos=(".bottom(%s)"%tube_pos)
        else:
            aspirate_pos=".bottom()"
               
                

        #IF ASPIRATING SAME MEDIA AS PREVIOUS STEP        
        if prev_source_type==this_source_type and prev_source_type!="":
            if (inst["aspirate_vol"]+tip_vol)<=params['max_vol_tip']:   #CONSOLIDATE ASPIRATIONS...
                
                aspirate_from_well=getLabelWell(inst["aspirate_from_well"], params,trough=1)
        
                #print(inst)
                #Put in queue
                tip_vol+=inst["aspirate_vol"]
                ret_dispense+="\np200.dispense(%s, plate%s[%s].top(%s)).touch_tip() #%s: <Slot %s><Well %s>"%(inst["dispense_vol"],inst["dispense_to_plate"], inst["dispense_to_well"], params['dispense_top'], numActions,all_pos_plates[int(inst["dispense_to_plate"])-1], getLabelWell(inst["dispense_to_well"], params))
            
                #ret_dispense+="\nw%s = plate%s[%s]"%(numActions,inst["dispense_to_plate"], inst["dispense_to_well"])
                #ret_dispense+="\np200.dispense(%s, w%s.top(%s)) # <Slot %s><Well %s>"%(inst["dispense_vol"],numActions, dispense_top,pos_plates[int(inst["dispense_to_plate"])-1], getLabelWell(inst["dispense_to_well"], '96-PCR-flat'))
                numActions+=1
                
            else:   #... UNTIL PIPETTE TIP FULL  
                
                #First dispense what we alrady have in queue
                aspirate_from_well=getLabelWell(inst["aspirate_from_well"], params,trough=1)
                ret+="\n\np200.aspirate(%s, trough['%s']%s)"%(tip_vol, aspirate_from_well, aspirate_pos)
                ret+=ret_dispense
                
                #Now queue this aspiration
                tip_vol=inst["aspirate_vol"]
                ret_dispense="\np200.dispense(%s, plate%s[%s].top(%s)).touch_tip() #%s: <Slot %s><Well %s>"%(inst["dispense_vol"],inst["dispense_to_plate"], inst["dispense_to_well"], params['dispense_top'], numActions,all_pos_plates[int(inst["dispense_to_plate"])-1], getLabelWell(inst["dispense_to_well"], params))
                numActions+=1
                
            prev_aspirate_pos=aspirate_pos
           
                
        else:  #Change of source
            
            #First dispense what we alrady have in queue
            if tip_vol>0: #and 
            
                if 'aspirate_from_well' not in locals():
                    prev_aspirate_pos=aspirate_pos
                   
                ret+="\n\np200.aspirate(%s, trough['%s']%s)"%(tip_vol, prev_source, prev_aspirate_pos)
                ret+=ret_dispense
            
            #Drop tip if loaded
            if prev_source!="":  
                ret+="\n\n#p200.drop_tip()"
                
            #Pick up tip
            ret+=("\n#p200.pick_up_tip(p200rack['%s'])"%numTips)  
            numTips+=1
            if numTips==96:  #Out of tips
                numTips=0
            
            #Callibration round (First time)
            if numTips==1: 
                for p0 in range(0,len(params['pos_plates'])):
                    ret+="\np200.move_to(plate%s[0].bottom(), 'arc')"%(p0+1)
                    ret+="\np200.move_to(plate%s[%s].bottom(), 'arc')"%(p0+1,params['rows']*params['cols']-1)
            
            #Now queue this
            ret+="\n\n# *********** Dispense %s"%this_source_type  
            
            tip_vol=inst["aspirate_vol"]
            ret_dispense="\np200.dispense(%s, plate%s[%s].top(%s)).touch_tip() #%s <Slot %s><Well %s>"%(inst["dispense_vol"],inst["dispense_to_plate"], inst["dispense_to_well"], params['dispense_top'],  numActions, all_pos_plates[int(inst["dispense_to_plate"])-1], getLabelWell(inst["dispense_to_well"], params))
            
            numActions+=1    
        
        
        prev_source=this_source
        prev_source_type=this_source_type
        
        
    #NOW CLEAR QUEUE
    aspirate_from_well=getLabelWell(inst["aspirate_from_well"], params,trough=1)
    ret+="\n\np200.aspirate(%s, trough['%s']%s)"%(tip_vol, aspirate_from_well, aspirate_pos)
    ret+=ret_dispense
    
    #ret+="\n\np200.drop_tip()"
    
    return ret

def generateOTScript(params):

    treatment_dict=loadTreatmentDict(params) #READ DICTIONARY
    (trough_layout,trough_layout_vol)=loadTroughLayout(params) #READ TROUGH LAYOUT

    thisTS=time.strftime("%Y%m%d%H%M%S")
    baseLayoutName=os.path.basename(params['fileLayoutName'])
    baseFileRobotName=os.path.basename(params['fileRobotName'])
    

    if params['randomize']==True:
        fileLayoutNameTS='%s/%s_%s.txt'%(os.path.dirname(params['fileLayoutName']),os.path.splitext(baseLayoutName)[0],thisTS)
        fileRobotNameTS='%s/%s_%s.py'%(os.path.dirname(params['fileRobotName']),os.path.splitext(baseFileRobotName)[0],thisTS)
        randomizePlate(fileLayoutName, fileLayoutNameTS)
    else:
        #fileLayoutNameTS='%s/%s_%s.txt'%(os.path.dirname(fileLayoutName),os.path.splitext(baseLayoutName)[0],thisTS)
        fileLayoutNameTS=params['fileLayoutName']
        #fileRobotNameTS='%s/%s_%s.py'%(os.path.dirname(params['fileRobotName']),os.path.splitext(baseFileRobotName)[0],thisTS)
        fileRobotNameTS='%s/%s.py'%(os.path.dirname(params['fileRobotName']),os.path.splitext(baseFileRobotName)[0])
        
        #shutil.copy2(params['fileLayoutName'], fileLayoutNameTS)

    robot_instructions=loadPlateLayout(fileLayoutNameTS, params) #READ RANDOMIZED PLATE LAYOUT

    robot_header=getRobotHeader(params)  
    robot_instructions=optimizeRobotInstructions(robot_instructions, params)  

    robot_comments='\n\n###################################################################################\n#'
    robot_comments+='\n# SCRIPT GENERATED ON %s FROM THE FOLLOWING LAYOUT FILES:'%time.strftime("%d/%m/%Y")
    robot_comments+='\n#  fileDictName=%s'%params['fileDictName']
    robot_comments+='\n#  fileTroughName=%s'%params['fileTroughName']
    robot_comments+='\n#  fileLayoutName=%s'%fileLayoutNameTS
    robot_comments+='\n#\n###################################################################################\n'

    strOut='%s%s%s\n##'%(robot_comments,robot_header,robot_instructions)


    if params['exportOTScript']:
        print("\n> Exporting %s"%fileRobotNameTS)
        toFile(fileRobotNameTS, strOut)


        if params['verbose']:
            print(strOut)
        
    return strOut