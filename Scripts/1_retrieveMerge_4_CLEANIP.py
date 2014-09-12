#For months in years, accesses FDA database
#Extract html and feed into BeautifulSoup
#Analyze and pull recall data
#Dump data to output excel files

#standard imports
import mechanize
import xlwt
from BeautifulSoup import BeautifulSoup
import os
from time import sleep
from removeUnits_2_CLEANIP import remUnits
import calendar
import re
from datetime import datetime
from dateutil import parser

#global definition for browser and its settings
mech = mechanize.Browser()
mech.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')]
mech.set_handle_robots(False)

#strip table row for data
def dataStrip(row):
        #define regular expression
        regex = re.compile(r'[\n\r\t]')

        #find cells, split and apply regex
        strong = row.findAll('td')
        strong = str(strong[0]).split('>')[1];
        strong = str(''.join(strong.split('<')[0])).strip();
        strong = regex.sub('',strong);

        return strong

#code for initialization
def initProg(startDate, endDate):

        #establish fields we want to pull
        fields = ["Recall Number", "Recall_Event_ID",
                  "Device_Type", "Product_Code", "Regulation", "Specialty", "Panel", "Approval",
                  "Product", "Main_Name", "Recall_Class", "Date Posted", "Recall_Year", "Recalling Firm",
                  "Reason", "FDA Determined", "Action", "Instructions",
                  "Cleaned_Quantity", "Quantity in Commerce", "Distribution",
                  "Recall Status", "Termination_Date", "Time_to_Terminate"]
        varis_TOT = [[] for i in range(len(fields))];

        #initialize browser and create credentials, head to initial website
        query = 'start_search=1&postdatefrom='+startDate+'&postdateto='+endDate+'&PAGENUM=500&sortcolumn=cda';

        #create soup of html to look over
        url = "http://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfRES/res.cfm?"+query
        mech.open(url)
        checkSoup = BeautifulSoup(mech.response().read())

        #find the table
        line = checkSoup.find('td',id='res-results-number')
        try:
                #get the text
                text = unicode(line.text).strip()

                #check if string indicates too large of a dataset ( > 500 will be rejected anyway)
                if('500' in text):
                        return 'too big'
        except:
                print 'err'
                return 'err'

        #locate all the recall links on the page
        #recall_links = mech.links(url=>'/res.cfm?id')
        #initialize new excel workbook and add a sheet
        for link in mech.links():
                if (link.url.find('/res.cfm?id')>-1):
                        #necessary delay to avoid being blocked
                        sleep(0.25);

                        #click on the link and follow where it goes
                        mech.click_link(link)
                        response = mech.follow_link(link)
                        html =  response.read()

                        #grab the html using beautiful soup
                        soup = BeautifulSoup(html)

                        #make all fields blank
                        number=''
                        event_id = ''
                        device_type = ''
                        procode = ''
                        regulation = ''
                        specialty = ''
                        panel = ''
                        approval = ''
                        name=''
                        main_name = ''
                        rclass=''
                        date=''
                        year=''
                        firm=''
                        reason=''
                        fda_cause = ''
                        action = ''
                        instruct = ''
                        clean_quant = ''
                        quant = ''
                        dist = ''
                        status = ''
                        term_date = ''
                        TTterm = ''

                        # Recall Class and Main Name
                        #find the td containing the information needed (in this case unique identifier is that font is bold and 11pt)
                        td = soup.find("td", style="font-family: arial; color: #23238e; font-weight:bold; font-size:11pt;")
                        if("Class" in str(td)):
                                # Getting the recall class
                                if len(td.contents) > 1:
                                        rclass = str(td.contents[0]).split(' ')[1]
                                        #print rclass
                                 # Getting the main_name
                                if len(td.contents) > 2:
                                        main_name = str(td.contents[2])
                                        #print main_name

                        varis = [number,event_id,device_type,procode,regulation,specialty,panel,approval,
                                 name,main_name,rclass,date,year,firm,reason,fda_cause,action,instruct,
                                 clean_quant,quant,dist, status, term_date, TTterm]

                        # Get the classification information
                        type_indx = fields.index('Device_Type')
                        procode_indx = fields.index('Product_Code')
                        regulation_indx = fields.index('Regulation')
                        specialty_indx = fields.index('Specialty')
                        panel_indx = fields.index('Panel')
                        approval_indx = fields.index('Approval')
                        for link in mech.links():

                            #check if this is the link we want, if so follow it
                            if (link.url.find('/classification.cfm?ID=')>-1):
                                mech.click_link(link)
                                response = mech.follow_link(link)

                                #create soup from this html
                                soup2 = BeautifulSoup(mech.response().read())
                                table2 = soup2.find("table", border="0", cellpadding="0", cellspacing=5, width="500")
                                for table2_tr in table2.findAll('tr'):
                                    col2 = table2_tr.findAll('th');

                                    #set all the vars
                                    if ("Device" in str(col2)) and not(("Class" in str(col2))):
                                        varis[type_indx] = dataStrip(table2_tr)
                                    if ("Product Code" in str(col2)):
                                        varis[procode_indx] = dataStrip(table2_tr)
                                    if ("Regulation Description" in str(col2)):
                                        varis[regulation_indx] = dataStrip(table2_tr)
                                    if ("Medical Specialty" in str(col2)):
                                        varis[specialty_indx] = dataStrip(table2_tr)
                                    if ("Review Panel" in str(col2)):
                                        varis[panel_indx] = dataStrip(table2_tr)
                                    if ("Submission Type" in str(col2)):
                                        varis[approval_indx] = dataStrip(table2_tr)
                                break;

                        #find the table containing the information needed (in this case unique identifier is that cellpadding is 2)
                        table = soup.find("table", cellpadding = 2)
                        if(table == None):
                                continue
                        for row in table.findAll('tr'):
                                #look for the field identifier
                                col = row.findAll('th')

                                # Recall ID
                                event_indx = fields.index('Recall_Event_ID')
                                text = [];
                                if ("Recall Event ID" in str(col)):
                                    a_link = row.find('a')
                                    varis[event_indx] = str(a_link.contents[0]).rstrip();

                                # Other Fields
                                for i in range(0, len(fields)):
                                        field = fields[i]
                                        if(field in str(col)):
                                                if (field == 'Product'):
                                                    if not('Classification' in str(col) or 'Life Cycle' in str(col)):
                                                        indx = fields.index(field)
                                                        varis[indx] = dataStrip(row)
                                                else:
                                                    indx = fields.index(field)
                                                    varis[indx] = dataStrip(row)

                        # Fields that are extracted based on other fields
                        # Year
                        date_indx = fields.index('Date Posted')
                        year_indx = fields.index('Recall_Year')
                        varis[year_indx] = str(varis[date_indx]).split(',')[1]

                        # Clean Quantity
                        clean_indx = fields.index('Cleaned_Quantity')
                        quant_indx = fields.index('Quantity in Commerce')
                        varis[clean_indx] = str(remUnits(varis[quant_indx]))

                        # Termination Date
                        status_indx = fields.index('Recall Status')
                        tdate_indx = fields.index('Termination_Date')
                        if ('Terminated' in varis[status_indx]):
                            varis[tdate_indx] = str(varis[status_indx]).split('on ')[1].rstrip();
                            varis[status_indx] = 'Terminated'

                            # Time to Terminate: Difference between Post Date and Terminate Date
                            date1_string = varis[date_indx].strip()
                            date1 = datetime.strptime(date1_string,"%B %d, %Y");
                            date2_string = varis[tdate_indx].strip()
                            date2 = datetime.strptime(date2_string,"%B %d, %Y");
                            TTterm_indx = fields.index('Time_to_Terminate')
                            varis[TTterm_indx] = (date2 - date1).days

                        # Replace N/A for empty fields
                        for var in varis:
                                if(var == ' ' or var == '' or var == '0'):
                                        varis[varis.index(var)] = 'N/A'

                        # Write the data to corresponding columns in spreadsheet
                        for i in range(0, len(varis)):
                                varis_TOT[i].append(varis[i])
        return varis_TOT



# Get Recalls Data from FDA Database for the dates specified.
def getData(startYear, startMonth, endYear, endMonth):
#go through required years
        curr_row = 1
        workbook = xlwt.Workbook("iso-8859-2")
        worksheet = workbook.add_sheet('sheet1')
        column_titles = ['Recall Number','Recall Event ID', 'Device Type', 'Product Code',
                         'Regulation Description','Medical Specialty', 'Review Panel','Submission Type',
                         'Trade Name/Product', 'Main Name','Recall Class','Date Posted','Year Posted',
                         'Recalling Manufacturer','Reason for Recall', 'FDA Determined Cause',
                         'Action','Consumer Instructions',
                         'Clean Quantity','Quantity in Commerce','Distribution',
                         'Recall Status', 'Termination Date', 'Time to Terminate']
        column = 0
        for c in column_titles:
                worksheet.write(0, column, c)
                column = column+1;
        for year in range(int(startYear), int(endYear)+1):
                for month in range(int(startMonth), int(endMonth)+1):

                        #search start
                        startDate = str(month).zfill(2)+'/01/'+str(year)

                        #search end
                        if(month == 12):
                                endDate = '01/01/'+str(year+1)
                        else:
                                endDate = str(month+1).zfill(2)+'/01/'+str(year)

                        #check if dataset small enough
                        response = initProg(startDate, endDate)

                        #if dataset too big, split month in half and then go
                        if (response == 'too big'):
                                startDate1 = startDate
                                endDate1 = str(month).zfill(2)+'/'+'18'+'/'+str(year)
                                startDate2 = str(month).zfill(2)+'/'+'18'+'/'+str(year)
                                endDate2 = endDate

                                response = initProg(startDate1, endDate1)
                                response2 = initProg(startDate2, endDate2)
                                # Merge two responses
                                for k in range(0, len(response2)):
                                        for i in range(0, len(response2[0])):
                                                response[k].append(response2[k][i]);
                        for i in range(0, len(response[0])):
                                for k in range(0, len(response)):
                                        worksheet.write(curr_row, k, response[k][i])
                                curr_row+=1
                        #print 'Month '+str(month)+'='+str(curr_row-1)
        workbook.save(str(startYear)+'.xls')
        print str(curr_row-1)+' recalls saved for '+str(startYear);

#only run this code if running this standalone
if __name__ == "__main__":
    basepath = './../Original_Data';
    os.chdir(basepath)
    for Year in range(2007, 2013):
        #print 'Year '+str(Year);
        startYear = Year;
        endYear = Year;
        startMonth = 1;
        endMonth = 12;
        getData(startYear, startMonth, endYear, endMonth)
