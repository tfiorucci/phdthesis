import csv 
import os
import sys 
import matplotlib.pyplot as plt 
import networkx as nx
import numpy as np
import json
from tqdm import tqdm
from time import sleep

#PATH TO THE LOGFILE FOLDER
PATHi="/work/adtexplore/users/dj13/MBSA/I2C_AHB/i2c/fault_db_SEU_rw/logs"

#PATH TO THE GOLDEN SIMULATION LOG
PATH = "/work/adtexplore/users/dj13/MBSA/I2C_AHB/i2c/fault_db_SEU_rw/xmsim.goodrun.log"

#RETRIEVING NUMBER OF LOGS
print("Retrieving Number of LOGS . . . . . ", end ='')
dirListing = os.listdir(PATHi)
MAX_LOG = len(dirListing)
#MAX_LOG = 1500
print("DONE")

#SETTING ENVIRONMENT FOR THE ANALISYS RESULTS
print("Setting up Environment for results . . . . . ", end ='')
TEST_FOLDER = "./NEW_AHB_RW_ALONE/"
if not os.path.exists(TEST_FOLDER):
    os.makedirs(TEST_FOLDER)
#   print("Directory " , TEST_FOLDER ,  " Created ")
#else:    
#   print("Directory " , TEST_FOLDER ,  " already exists")  

print("DONE")


LINE_IDENTIFIER="out-i2c:"

## CREATE GRAPH
G = nx.DiGraph()
LG = nx.DiGraph()
## CREATE COLOR MAP
node_color_map = []
edge_color_map = []    

#CREATE GOLDEN DICTIONARY
occurrencies_dict_gold = {}
transitions_dict_gold = {}
previous_raw_output = ""
counter = 0 


propagating_state = []
unique_prop_L = []
unique_prop_I = []
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



with open (PATH, "r") as file_handler:
    num_lines = sum(1 for line in open(PATH))
    barindex=0
    #printProgressBar(0, num_lines + 1, prefix = 'Progress:', suffix = 'Complete', length= 50)

    for line in tqdm(file_handler, total= num_lines, desc = "Golden_Analisys", leave=True, unit="lines"):
        if LINE_IDENTIFIER in line:
            raw_output = line.split(":")[1].strip() # Identify desired rows and isolate output

  # Occurrencies
            if raw_output in occurrencies_dict_gold:
                occurrencies_dict_gold[raw_output] += 1
            else:
                occurrencies_dict_gold[raw_output] = 1

            # Transitions
            if counter > 0:
                transition_key = previous_raw_output + ";" + raw_output
                if transition_key in transitions_dict_gold:
                    transitions_dict_gold[transition_key] += 1
                else:
                    transitions_dict_gold[transition_key] = 1
            previous_raw_output = raw_output
            counter += 1
            barindex +=1
        #printProgressBar(barindex, num_lines +1, prefix = 'Progress:', suffix = 'Complete', length= 50)
    print ("LEGAL STATES: {}, LEGAL TRANSITION: {}".format(len(occurrencies_dict_gold), len(transitions_dict_gold)))

#PATH = "/work/adtdesign/fiorucct/testchip/i2c_test/fsv/xrun.log"
#FAULT_NUM = sys.argv[1]
occurrencies_dict = {}
transitions_dict = {}

########### OPENING PARSING LOG FILE #################
pars_log = open(TEST_FOLDER + "parsing_log.txt", "w")
pars_log.write("FID,INJECTION_POINT,ACTIVATED_PROBES,INJT,DETCT,DELAY,OTHER_PROBES_ACTIVATED")
pars_log.write("\n")

timeout_log = open(TEST_FOLDER + "timeout_log.txt", "w")
timeout_log.write("FID,INJECTION_POINT,INJECTION_TIME,OUTPUT")
timeout_log.write("\n")


#printProgressBar(0, MAX_LOG + 1, prefix = 'Progress:', suffix = 'Complete', length= 50)
for i in tqdm(range(MAX_LOG), desc="Faultrun_Analysis", unit="logs"): #FLOP NUMBER
    if i == 0:
        continue
  ###CREATE DICTIONARY
    PATH = PATHi + "/faultrun_" + str(i) + ".log"
    previous_raw_output = ""
    counter = 0
    barindex = i 
    fault_id = ''
    tmp_state_path = []
    fault_stop = ''
    inj_time = ''
    inj_point = ''
    dect_point = ''
    dect_list = []
    possible_dect_point = ''
    possible_dect_list = []
    fault_time_out = ''
    # Opening LogFile
    with open (PATH, "r") as file_handler:
        tmp_state_path.clear()
        dect_flag = 0
        for line in file_handler:
            if LINE_IDENTIFIER  in line:
                raw_output = line.split(":")[1].strip() # Identify desired rows and isolate output
                tmp_state_path.append(raw_output)
    
          # Occurrencies
                if raw_output in occurrencies_dict:
                    occurrencies_dict[raw_output] += 1
                else:
                    occurrencies_dict[raw_output] = 1


                    if raw_output in occurrencies_dict_gold:
                        G.add_node(raw_output, color = '#03fc94')
                        node_color_map.append('green')
                        ## TRY
                        if dect_flag != 0:
                            LG.add_node(raw_output, color = 'g')
                    else:
                        G.add_node(raw_output, color = '#fc0303')
                        #print('RED STATE : ', raw_output)
                        node_color_map.append('red')
                        ## TRY
                        if dect_flag != 0:
                            LG.add_node(raw_output, color = "#ed33ff")
              # Transitions
                if counter > 0:
                    transition_key = previous_raw_output + ";" + raw_output
                    if transition_key in transitions_dict:
                        transitions_dict[transition_key] += 1
                    else:
                        transitions_dict[transition_key] = 1
                        if transition_key in transitions_dict_gold:
                            G.add_edge(previous_raw_output, raw_output, label = 'g')
                            if dect_flag != 0:
                                LG.add_edge(previous_raw_output, raw_output)
                        else:
                            G.add_edge(previous_raw_output, raw_output, label = 'ILLEGAL')
                            if dect_flag != 0:
                                LG.add_edge(previous_raw_output, raw_output, color = '#ed33ff', lable = "ILLEGAL")
                    #edge_color_map.append("black")
                previous_raw_output = raw_output
                counter += 1


            if "FLTSF" in line:
                fault_id = line.split(' ')[6].strip()

            if "FLTSPT" in line:
                #fault_stop = line.split(' ')[5:].strip()
                fault_stop = 'STOP'
            #    if " " in line:
            if "FLTSTO" in line:
                fault_time_out = 'TIMEOUT'

            if "FLTINJ" in line:
                inj_point = line.split(' ')[7].strip()
                inj_time  = line.split(' ')[10].strip()
                dect_flag = 1
            if "FLTDT"  in line:
                dect_point = line.split(' ')[8].strip()
                dect_time  = line.split(' ')[11].strip()
                dect_list.append(dect_point)
                dect_flag = 3
            
            if "FLTPDT" in line:
                possible_dect_point = line.split(' ')[9].strip()
                possible_dect_time  = line.split(' ')[12].strip()
                possible_dect_list.append(possible_dect_point)
        
        if dect_point != '' or possible_dect_point!= '':
            dect_list_str = ' '.join(dect_list)
            possible_dect_list_str = '-'.join(possible_dect_list)
            pars_log.write(fault_id + inj_point + ','  +dect_list_str + ',' + inj_time +','+ dect_time
            + ','+ str(int(dect_time)-int(inj_time)) + ',' + possible_dect_list_str)
            pars_log.write("\n")

        if fault_time_out != '':
            timeout_log.write(fault_id + inj_point +','+inj_time +','+ fault_time_out)
            timeout_log.write("\n")
        if dect_flag == 1 and len(tmp_state_path)>0:
            if tmp_state_path[len(tmp_state_path)-1] in propagating_state:
                propagating_state.append(tmp_state_path[len(tmp_state_path)-1])
            else:
                if tmp_state_path[len(tmp_state_path)-1] in occurrencies_dict_gold:
                    propagating_state.append(tmp_state_path[len(tmp_state_path)-1])
                    unique_prop_L.append(tmp_state_path[len(tmp_state_path)-1])
                else:
                    propagating_state.append(tmp_state_path[len(tmp_state_path)-1])
                    unique_prop_I.append(tmp_state_path[len(tmp_state_path)-1])



    #printProgressBar(barindex + 1, MAX_LOG + 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
print ("STATES: {}, TRANSITION: {}".format(len(occurrencies_dict), len(transitions_dict)))
print ("TOT_PROPAGATIN STATES: {}, DIFFERENT_PROPAGATING STATES:{}, ILLEGAL_PROP: {}, LEGAL_PROP: {}".format(len(propagating_state), len(unique_prop_I)+(len(unique_prop_L)), len(unique_prop_I), len(unique_prop_L)) )
## GENERATE THE ADJ MATRIX ##

adjacency_matrix = [ [0]*len(occurrencies_dict) for _ in range(len(occurrencies_dict)) ]
occurrencies_list = list(occurrencies_dict)

for occ_key in tqdm(occurrencies_dict, desc="Adjacency_matrix", unit="entries"):
    for tran_key in transitions_dict:
        transition = tran_key.split(";")
        if occ_key == transition[0]:
            adjacency_matrix[occurrencies_list.index(occ_key)][occurrencies_list.index(transition[1])] = 1
#ADJ_FILE = TEST_FOLDER + "adj/adjacency_matrix" + str(i)
with open("new_adj.txt", "w+") as fw:
    for row in adjacency_matrix:
        fw.write(",".join(str(i) for i in row).lstrip(",") + "\n")


nodesAt5 = [x for x,y in G.nodes(data=True) if y['color']=='g']



sink_node = [node for node in LG.nodes if LG.out_degree(node) == 0]
print(sink_node)

#r = nx.degree_assortativity_coefficient(G)
#print(r)
#print(nodesAt5)

nx.write_graphml(G, "random.graphml", prettyprint = True, named_key_ids
        = True)

nx.write_gml(G, "test.gml")
nx.draw(LG)
plt.show()
