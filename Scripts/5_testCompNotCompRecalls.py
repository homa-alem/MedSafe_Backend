# Reads the Computer_Related_Recalls_Categories and all the unique recalls 2006-2011
# Merges them into one file which includes both, with a new field indicating
# Computer and Non-Computer Related and Action Category
# Action Classes are converted to the categories mentioned in the IEEE S&P paper

import nltk
from nltk.probability import ConditionalFreqDist
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string
import xlrd
import xlwt
import csv
import os
import time
from zipfile import ZipFile

def testRecalls(*args):
    if len(args)==2:
        startYear = args[0]
        endYear = args[1]
    else:
        years = []
        files = os.listdir("./../Original_Data")
        for fl in files:
            years.append(int(fl.split(".")[0]))

        startYear = min(years)
        endYear = max(years)+1
    data_dir = './../Unique_Data/';
    datafiles = []
    for Year in range(startYear, endYear):
        datafiles.append('unique'+str(Year)+'.xls');

    comp_dir = './../Other_Data/'
    csv_rd1 = open(comp_dir+'Computer_Related_Recalls_Categories.csv', 'rb')
    comp_rd = csv.reader(csv_rd1, dialect='excel', delimiter=',')

    # Make a Hash of Computer_Related Recalls
    titles = comp_rd.next()
    Comp_Hash = {'Recall Num':('Fault Class','Failure Mode','Action Class')}
    for line in comp_rd:
        Recall_Num = line[0].strip();
        Fault_Class = line[7].strip();
        Failure_Mode = line[8].strip();
        Action_Class = line[10].strip()
        Comp_Hash[Recall_Num] = (Fault_Class, Failure_Mode, Action_Class);

    # Previously classified recalls - manually fixed some mistakes
    pre_file = comp_dir+'unique_Combined.xls'
    pre_book = xlrd.open_workbook(pre_file)
    pre_sheet = pre_book.sheet_by_name('Sheet1')
    nrows = pre_sheet.nrows
    ncols = pre_sheet.ncols
    Pre_Hash = {'Recall Num':('Fault Class','Failure Mode')}

    # Find the column numbers for Recall Number, Fault Class, and Failure Mode
    for i in range(0, ncols):
        col = pre_sheet.cell_value(0, i)
        if(col == 'Recall Number'):
            Number_Index = i
        elif(col == 'Fault Class'):
            Fault_Index = i
        elif(col == 'Failure Mode'):
            Failure_Index = i

    for i in range(0,nrows):
        Recall_Num = pre_sheet.cell_value(i, Number_Index).strip()
        Fault_Class = pre_sheet.cell_value(i, Fault_Index).strip()
        Failure_Mode = pre_sheet.cell_value(i, Failure_Index).strip()
        Pre_Hash[Recall_Num]= (Fault_Class, Failure_Mode);


    # Excel file to write
    excel_wr = data_dir+'Merged_Final_Unique_Recalls_2007_2011.xls'
    newbook = xlwt.Workbook('utf-8')
    newsheet = newbook.add_sheet('sheet1')

    # Write Titles
    databook = xlrd.open_workbook(data_dir+datafiles[0])
    datasheet = databook.sheet_by_index(0)
    data_cols = datasheet.ncols
    for i in range(0, data_cols):
        newsheet.write(0, i, datasheet.cell_value(0, i))
    newsheet.write(0, data_cols, "Fault Class")
    newsheet.write(0, data_cols+1, "Failure Mode")
    newsheet.write(0, data_cols+2, "Action Class")
    newsheet.write(0, data_cols+3, "Action Category")

    curr_row = 1;
    for dfile in datafiles:
        print 'Year = ' + dfile
        databook = xlrd.open_workbook(data_dir+dfile)
        datasheet = databook.sheet_by_name('sheet1')
        data_cols = datasheet.ncols
        data_rows = datasheet.nrows

        # Find the column numbers for Reason and Action
        for i in range(0, data_cols):
            col = datasheet.cell_value(0, i)
            if(col == 'Reason for Recall'):
                Reason_Index = i
            if(col == 'Action'):
                Action_Index = i

        # Write the records
        for i in range(1, data_rows):
            Recall_Num = str(datasheet.cell_value(i, 0))
            if Comp_Hash.has_key(Recall_Num):
                Fault_Class = Comp_Hash[Recall_Num][0]
                Failure_Mode = Comp_Hash[Recall_Num][1]
                Action_Class = Comp_Hash[Recall_Num][2]
                Action = Action_Class.lower()
                if(Action.find('sof') > -1 or Action.find('patch') > -1 or Action.find('version') > -1 or
                   Action.find('firmware') > -1 or Action.find('file') > -1):
                    Action_Category = "Software Update"
                elif(Action.find('correct') > -1 or Action.find('repair') > -1 or (Action.find('fix') > -1) or
                     Action.find('upgrade') > -1 or Action.find('rework') > -1 or Action.find('service') > -1):
                    Action_Category = "Repair"
                elif(Action.find('retrieve') > -1 or Action.find('replace') > -1 or
                     Action.find('remove') > -1 or Action.find('return') > -1 or
                     Action.find('discard') > -1 or Action.find('stop') > -1):
                    Action_Category = "Remove or Replace"
                elif(Action.find('instructions') > -1 or Action.find('notification') > -1 or
                     Action.find('letter') > -1 or Action.find('phone') > -1 or Action.find('advice') > -1):
                    Action_Category = "Safety Notice/Insructions"
                elif (Action == '' or Action == ' ' or Action.find('N/A') > -1):
                    Action_Category = "N/A";
                else:
                    Action_Category = "Other";
            else:
                Action_Class = "N/A"
                Action_Category = "N/A"
                Reason = datasheet.cell_value(i, Reason_Index).strip()
                Action = datasheet.cell_value(i, Action_Index).strip()
                if (Reason.lower().find('software') > -1 or Reason.lower().find('version') > -1 or
                    Action.lower().find('software') > -1):
                    Fault_Class = 'Computer'
                    Failure_Mode = 'N/A'
                else:
                    Fault_Class = 'Not_Computer'
                    Failure_Mode = 'N/A'
                # To consider ones that we manually reviewed and changed before:
                if Pre_Hash.has_key(Recall_Num):
                    Fault_Class = Pre_Hash[Recall_Num][0];
                    Failure_Mode = Pre_Hash[Recall_Num][1];

            for k in range(0, data_cols):
                newsheet.write(curr_row, k, datasheet.cell_value(i, k))
            newsheet.write(curr_row, data_cols, Fault_Class)
            newsheet.write(curr_row, data_cols+1, Failure_Mode)
            newsheet.write(curr_row, data_cols+2, Action_Class)
            newsheet.write(curr_row, data_cols+3, Action_Category)
            curr_row = curr_row + 1

    print str(curr_row-1)+' were written'
    newbook.save(excel_wr);
    csv_rd1.close()

if __name__ == "__main__":
    testRecalls(2007,2009)
    testRecalls()
