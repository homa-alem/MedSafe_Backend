from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import xlrd
import xlwt
import os
from Levenshtein import *
from fuzzywuzzy import fuzz

tfidf_vectorizer = TfidfVectorizer()

def getBestLev(word, possib):
    min = 10000
    ratid = 0.65
    loc = 100
    for i in range(0, len(possib)):
        if(abs(len(possib[i])-len(word))>3):
            continue
        dist = distance(word, possib[i])
        rati = fuzz.token_set_ratio(word, possib[i])
        if(rati > ratid):
            min = dist
            ratid = rati
            loc = i
    if(min == 10000 or loc == 100 or ratid == 0.65):
        return -1
    return loc

def doCos(possib):
    tfidf_matrix = tfidf_vectorizer.fit_transform(possib)
    possib = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix).tolist()[0]
    return possib

def getMaxNotHead(possib):
    possib = doCos(possib)
    max = -99999999
    ind = -1
    for i in range(1, len(possib)):
        if(possib[i] >= max):
            max = possib[i]
            ind = i
    return ind

def compareRecall(path, procodes, Procodes_Hash, datafiles):
    curr_path = os.getcwd()
    newbook = xlwt.Workbook('utf-8')
    newsheet = newbook.add_sheet('sheet1', cell_overwrite_ok = True)
    os.chdir(path)
    #dest = open("procCheck.txt")
    probook = xlrd.open_workbook(procodes)
    if(not os.path.exists(procodes)):
        return 'Invalid procodes file given.'
    try:
        prosheet = probook.sheet_by_name('sheet1')
    except:
        prosheet = probook.sheet_by_index(0)
    procode_rows = prosheet.nrows
    curr_row = 1
    for file in datafiles:
        count = 0
        if(not os.path.exists(file)):
            continue
        databook = xlrd.open_workbook(file)
        try:
            datasheet = databook.sheet_by_name('sheet1')
        except:
            datasheet = databook.sheet_by_index(0)
        data_cols = datasheet.ncols
                # Write Titles
        for i in range(0, data_cols):
            newsheet.write(0, i, datasheet.cell_value(0, i))
        newsheet.write(0, data_cols, "Medical Specialty")
        newsheet.write(0, data_cols+1, "Product Code")
        newsheet.write(0, data_cols+2, "Device Name")
        newsheet.write(0, data_cols+3, "Recall Number Used")
        newsheet.write(0, data_cols+4, "Recall Name Used")
        newsheet.write(0, data_cols+5, "Recall Company Used")
        found_record = 0;
        fixed_record = 0;
        medical_specialty = 'N/A';
        product_code = 'N/A';
        device_name = 'N/A';
        recall_used = 'N/A';
        recall_name_used = 'N/A';
        recall_company_used = 'N/A';
        data_rows = datasheet.nrows
        for i in range(1, data_rows):
            data_Manu = str(datasheet.cell_value(i, 6)).split(';')[0]
            data_Main = str(datasheet.cell_value(i, 2))
            data_Recall = str(datasheet.cell_value(i, 0))
            if Procodes_Hash.has_key(data_Recall):
                (medical_specialty, product_code, device_name) = Procodes_Hash[data_Recall];
                recall_used = data_Recall;
                recall_company_used = 'hash'
                recall_name_used = 'hash'
                found_record = found_record + 1;
            else:
                possib_best = []
                possib_loc = []
                for k in range(1, procode_rows):
                    procode_Recall = str(prosheet.cell_value(k, 0))
                    procode_Manu = str(prosheet.cell_value(k, 4)).split(';')[0]
                    if(ratio(data_Manu, procode_Manu) > .80):
                        procode_Main = str(prosheet.cell_value(k, 3))
                        possib_best.append(procode_Main)
                        possib_loc.append(k)
                if(possib_best == []):
                    best = 'N/A'
                else:
                    possib_best.insert(0, data_Main)
                    possib_loc.insert(0, i)
                    best = getMaxNotHead(possib_best)
                    if (best == -1 or ratio(possib_best[best], data_Main) < .8):
                        best = 'N/A'
                    else:
                        fixed_record+=1
                        print 'Data: ' + data_Main
                        print 'Procode: ' + possib_best[best]
                        recall_name_used = prosheet.cell_value(best, 2)
                        recall_company_used = prosheet.cell_value(best, 4)
                        medical_specialty = prosheet.cell_value(best, 5)
                        product_code = prosheet.cell_value(best, 6)
                        device_name= prosheet.cell_value(best, 7)
                        recall_used = str(prosheet.cell_value(best, 0))
            # Write the recall and product code
            for k in range(0, data_cols):
                newsheet.write(curr_row, k, datasheet.cell_value(i, k))
            newsheet.write(curr_row, data_cols, medical_specialty)
            newsheet.write(curr_row, data_cols+1, product_code)
            newsheet.write(curr_row, data_cols+2, device_name)
            newsheet.write(curr_row, data_cols+3, recall_used)
            newsheet.write(curr_row, data_cols+4, recall_name_used)
            newsheet.write(curr_row, data_cols+5, recall_company_used)
            medical_specialty = 'N/A';
            product_code = 'N/A';
            device_name = 'N/A';
            recall_used = 'N/A';
            recall_name_used = 'N/A';
            recall_company_used = 'N/A';
            curr_row = curr_row + 1
        print str(found_record)+' of '+str(data_rows)+' recalls were already classified.';
        print 'An additional ' + str(fixed_record)+' recalls were classified';
    newbook.save(path+'Recalls_Procodes_Added.xls')
    os.chdir(curr_path)

path = "./../Research Data/"
procodes = "All_Recalls_procodes.xls"

# Make a Hash of all Recalls_Procodes
os.chdir(path)
probook = xlrd.open_workbook(procodes)
if(not os.path.exists(procodes)):
    print 'Invalid procodes file given.'
try:
    prosheet = probook.sheet_by_name('sheet1')
except:
    prosheet = probook.sheet_by_index(0)
procode_rows = prosheet.nrows
Procodes_Hash = {'Number':('Medical_Specialty','Procode','Device_Name')}
for k in range(1, procode_rows):
    Recall_Num = str(prosheet.cell_value(k, 0))
    Specialty = str(prosheet.cell_value(k, 5))
    Procode = str(prosheet.cell_value(k, 6))
    Device_Name = str(prosheet.cell_value(k, 7))
    Procodes_Hash[Recall_Num] = (Specialty, Procode, Device_Name);

datafiles = ["2006.xls","2007.xls","2008.xls","2009.xls","2010.xls","2011.xls","2012.xls","2013.xls"]
for i in xrange(len(datafiles)):
    datafiles[i] = 'unique'+datafiles[i]
compareRecall(path, procodes, Procodes_Hash, datafiles)
