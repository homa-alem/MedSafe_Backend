#imports from other research scripts
retrieve = __import__('1_retrieveMerge')
unique = __import__('2_uniqueReasons')
procodes = __import__('4_procodeCompare')

#standard module imports
import os

#markers for which sections to execute
pieces = {"Retrieve": False, "Unique": True, "Classify": False}

'''
    SCRIPT 1 --> Retrieve the data
'''
if(pieces["Retrieve"]):

    #set up the basepath
    basepath = './../../New_Data';
    os.chdir(basepath)

    #get data from 2005-2012
    for Year in range(2005, 2012):
        print 'Year '+str(Year);
        startYear = Year;
        endYear = Year;

        #full year at a time
        startMonth = 1;
        endMonth = 12;

        #get the data
        retrieve.getData(startYear, startMonth, endYear, endMonth)

'''
    SCRIPT 2 --> Make Data Unique
'''
if(pieces["Unique"]):
    files = []
    for Year in range(2001, 2014):
        filename = ''+str(Year)+'.xls'
        files.append(filename)
    print files
    #unique.elimCopyReasons('.././New_Data', files)

    #files = ["Unique_Computer_Recalls_2007_2011_copy.xls"]
    #elimCopyReasons('../../New_Data', files)

'''
    SCRIPT 3 --> Classify Recalls
'''
if(pieces["Classify"]):

    #set up the basepath
    path = "./../Research Data/"
    os.chdir(path)

    # Make a Hash of all Recalls_Procodes
    procodes = "All_Recalls_procodes.xls"
    probook = xlrd.open_workbook(procodes)

    if(not os.path.exists(procodes)):
        print 'Invalid procodes file given.'
    #grab the sheet (changed naming so index maybe more consistent)
    try:
        prosheet = probook.sheet_by_name('sheet1')
    except:
        prosheet = probook.sheet_by_index(0)

    #identify rows in the worksheet
    procode_rows = prosheet.nrows

    #establish hash
    Procodes_Hash = {'Number':('Medical_Specialty','Procode','Device_Name')}

    #read in all of the old data
    for k in range(1, procode_rows):

        #pull the old data
        Recall_Num = str(prosheet.cell_value(k, 0))
        Specialty = str(prosheet.cell_value(k, 5))
        Procode = str(prosheet.cell_value(k, 6))
        Device_Name = str(prosheet.cell_value(k, 7))

        #write it into the hash
        Procodes_Hash[Recall_Num] = (Specialty, Procode, Device_Name);

    #grab unique files (update this)
    datafiles = []
    for Year in range(2006, 2014):
        datafiles.append('unique'+str(Year)+'.xls')

    #perform the recall comparisons
    #procodes.compareRecall(path, procodes, Procodes_Hash, datafiles)
