#Look through files for unique recalls
#If unique, add data to output worksheet and running hash
#If copy found, modify output worksheet and hash
#Save data in output worksheets

import xlrd
import xlwt
import os
from Levenshtein import *
import codecs

remUnit = __import__('3_removeUnits')
remUnits = remUnit.remUnits

#define locations
REASON = 14
ACTION = 16
TTT = 23
QUANT = 19
MERGE = 24

def elimCopyReasons(basepath, filenames, destpath=''):
        num_records = 0;

        # curr_dir = os.getcwd()
        # os.chdir(basepath)

        #loop through files
        for filename in filenames:
        #get the working directory and set basepath
                curr_dir = os.getcwd()
                os.chdir(basepath)

                #initialize vars
                remCount = 0
                mergeEvents = []
                quants = []

                #open old data and set new data
                oldbook = xlrd.open_workbook(filename)
                newbook = xlwt.Workbook('utf-8')
                newsheet = newbook.add_sheet('sheet1', cell_overwrite_ok = True)
                oldsheet = oldbook.sheet_by_index(0)
                num_cols = oldsheet.ncols
                indexEvent = -1

                #loop through columns and identify
                for curr_col in range(0, num_cols):
                        col = oldsheet.cell_value(0, curr_col)
                        if(col == 'Recall Event ID'):
                                indexEvent = curr_col
                        newsheet.write(0, curr_col, col)
                newsheet.write(0, MERGE, "Merged Quantities")

                #err if couldn't find it
                if(indexEvent == -1):
                        print 'Could not find merge event category'
                        return
                num_rows = oldsheet.nrows-1
                curr_row = 0
                write_row = 1

                #go through the rows
                while curr_row < num_rows:
                        curr_row+=1

                        #pull out the data
                        recallEvent = oldsheet.cell_value(curr_row, indexEvent)
                        flag = False

                        #if haven't found this one already, add it
                        if(not recallEvent in mergeEvents):
                                mergeEvents.append(recallEvent)

                                #copy over all relevant data
                                for i in range(0, num_cols):
                                        newsheet.write(write_row, i, oldsheet.cell_value(curr_row, i))

                                #write in the quantity
                                newsheet.write(write_row, MERGE, str(remUnits(oldsheet.cell_value(curr_row, QUANT))))
                                quants.append([recallEvent, oldsheet.cell_value(curr_row, QUANT), write_row])
                                write_row+=1

                        #modify quantity instead
                        else:
                                remCount += 1
                                for i in range(0, len(quants)):

                                        #find the one to modify in list of saved recalls
                                        if(recallEvent == quants[i][0]):
                                                old_quant = quants[i][1]
                                                new_quant = oldsheet.cell_value(curr_row, QUANT)

                                                #special rules to attempt to not double-count and not err
                                                if('N/A' in new_quant or 'N/A' in old_quant or 'total' in new_quant or 'all' in new_quant):
                                                        continue
                                                else:
                                                        if('N/A' in str(remUnits(new_quant))):
                                                                continue

                                                        #add in the new quantity
                                                        else:
                                                                try:
                                                                        a = int(remUnits(old_quant))
                                                                        b = int(remUnits(new_quant))
                                                                        if(a==b):
                                                                                continue
                                                                        mod_quant = a+b

                                                                        #save back to array, write it to the file
                                                                        quants[i][1] = str(mod_quant)
                                                                        newsheet.write(quants[i][2], MERGE, str(mod_quant))

                                                                #ignore any errors, don't want to bother with it
                                                                except:
                                                                        continue

                #save the new file and print results
                if(destpath != ''):
                    os.chdir(destpath)
                newbook.save('unique'+filename)
                print '------------------'+filename+'------------------'
                print 'Total number of recall records read = ' + str(num_rows);
                print 'Total number of recall records written = ' + str(len(mergeEvents));
                print("There should be " + str(num_rows-remCount) + " recalls left")
                num_records = num_records + num_rows;
        os.chdir(curr_dir)

def countUnique(srcfiles, destfile, index):
    uniqueSeen = []
    write_row = 1
    hashUnique = {'Recall Event ID':('Reasons', 'Actions', 'Time to Terminate')}
    copies = 0
    destbook = xlwt.Workbook('utf-8')
    destsheet = destbook.add_sheet('sheet1')
    destsheet.write(0, 0, 'Recall Event Id')
    destsheet.write(0, 1, 'Reasons')
    destsheet.write(0, 2, 'Actions')
    destsheet.write(0, 3, 'Time to Terminate')
    for file in srcfiles:
        oldbook = xlrd.open_workbook(file)
        oldsheet = oldbook.sheet_by_index(0)
        for i in range(1, oldsheet.nrows):
            eventId = oldsheet.cell_value(i, index)
            if(not hashUnique.has_key(eventId)):
                hashUnique[eventId] = (oldsheet.cell_value(i, REASON), oldsheet.cell_value(i, ACTION), oldsheet.cell_value(i, TTT))
            else:
                copies += 1
                if(ratio(hashUnique[eventId][0], oldsheet.cell_value(i, REASON)) < .8):
                    if(not eventId in uniqueSeen):
                        destsheet.write(write_row, 0,  eventId)
                        destsheet.write(write_row, 1,  hashUnique[eventId][0])
                        destsheet.write(write_row, 2,  hashUnique[eventId][1])
                        destsheet.write(write_row, 3,  hashUnique[eventId][2])
                        write_row+=1
                        uniqueSeen.append(eventId);
                    destsheet.write(write_row, 0,  eventId)
                    destsheet.write(write_row, 1,  oldsheet.cell_value(i, 14))
                    destsheet.write(write_row, 2,  oldsheet.cell_value(i, 16))
                    destsheet.write(write_row, 3,  oldsheet.cell_value(i, 23))
                    write_row+=1
    destbook.save(destfile)

def countUnique2(srcfiles, destfile, index):
    uniqueSeen = []
    write_row = 1
    hashUnique = {'Recall Event ID':('Reasons', 'Actions', 'Time to Terminate')}
    copies = 0
    destbook = xlwt.Workbook('utf-8')
    destsheet = destbook.add_sheet('sheet1')
    destsheet.write(0, 0, 'Recall Event Id')
    destsheet.write(0, 1, 'Reasons')
    for file in srcfiles:
        oldbook = xlrd.open_workbook(file)
        oldsheet = oldbook.sheet_by_index(0)
        for i in range(1, oldsheet.nrows):
            found = 0;
            eventId_i = oldsheet.cell_value(i, index)
            reason_i = oldsheet.cell_value(i, REASON)
            for j in range(1, oldsheet.nrows):
                eventId_j = oldsheet.cell_value(j, index)
                reason_j = oldsheet.cell_value(j, REASON)
                if not(eventId_i == eventId_j) and (ratio(reason_i, reason_j) > .9):
                    found = 1;
                    destsheet.write(write_row, 0,  eventId_j)
                    destsheet.write(write_row, 1,  reason_j)
                    write_row+=1
            if (found == 1):
                destsheet.write(write_row, 0,  eventId_i)
                destsheet.write(write_row, 1,  reason_i)
                write_row+=1
                destsheet.write(write_row, 0,  ' ')
                destsheet.write(write_row, 1,  ' ')
                write_row+=1
    destbook.save(destfile)

#only run this code if this is the main file
if __name__ == "__main__":
    files = os.listdir("./../Original_Data")#, '2008.xls']#"Unique_Computer_Recalls_2007_2011_copy.xls"]
    # for fl in files:
    #     print fl
    elimCopyReasons('./../Original_Data', files, './../Unique_Data')
