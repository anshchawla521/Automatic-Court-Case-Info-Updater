from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from datetime import datetime , date ,time , timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import os
import pickle
import requests 
import time
import gspread

debug = 0
#0 --> debug mode off
#1 --> debug mode on , excelfile =casestest but event creation off
#2 --> debug mode on , excelfile =casestest but event creation on
# if debug == 1 :
#     print("CheckPoint 1")
#solve next date error
print('''
 __        __         _                                   
 \ \      / /   ___  | |   ___    ___    _ __ ___     ___ 
  \ \ /\ / /   / _ \ | |  / __|  / _ \  | '_ ` _ \   / _ \ 
   \ V  V /   |  __/ | | | (__  | (_) | | | | | | | |  __/
    \_/\_/     \___| |_|  \___|  \___/  |_| |_| |_|  \___|''')
time.sleep(2)

print(''' 
  _   _   _           _        ____                          _                ____                            
 | | | | (_)   __ _  | |__    / ___|   ___    _   _   _ __  | |_             / ___|   __ _   ___    ___   ___ 
 | |_| | | |  / _` | | '_ \  | |      / _ \  | | | | | '__| | __|    _____  | |      / _` | / __|  / _ \ / __|
 |  _  | | | | (_| | | | | | | |___  | (_) | | |_| | | |    | |_    |_____| | |___  | (_| | \__ \ |  __/ \__ \ 
 |_| |_| |_|  \__, | |_| |_|  \____|  \___/   \__,_| |_|     \__|            \____|  \__,_| |___/  \___| |___/
              |___/                                                                                           ''')
                                                          

scopes_calander = ['https://www.googleapis.com/auth/calendar']
scopes_drive =  ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds_drive = ServiceAccountCredentials.from_json_keyfile_name("creds.json" , scopes_drive)
client = gspread.authorize(creds_drive)
creds_calander = None
eventupdated = True
category_dict = {
    'URGENT':'U',
    'ORDINARY':'O',
    'TAKENUP':'T',
    'SPECIAL':'S',
    'PRE LOK ADALAT':'A',
    'LOK ADALAT':'K',
    'ELECTION':'E',
    'LIQUIDATION (URGENT)':'Q',
    'LIQUIDATION (ORDINARY)':'L',
    'COMMERCIAL (URGENT)':'F',
    'COMMERCIAL (ORDINARY)':'G',
    'FOR-ORDER':'Y',
    'OLD-CASES':'V'

}

month = {
    'JAN' : '01',
    'FEB' : '02',
    'MAR' : '03',
    'APR' : '04',
    'MAY' : '05',
    'JUN' : '06',
    'JUL' : '07',
    'AUG' : '08',
    'SEP' : '09',
    'OCT' : '10',
    'NOV' : '11',
    'DEC' : '12'


}
list_date_current = (datetime.date(datetime.now() ))
list_date_current =   list_date_current.strftime("%Y") + "_" +list_date_current.strftime("%m") + "_" +list_date_current.strftime("%d")
list_date_next = (datetime.date(datetime.now() + timedelta(days = 1)))
list_date_next =   list_date_next.strftime("%Y") + "_" +list_date_next.strftime("%m") + "_" +list_date_next.strftime("%d")
list_date_previous = (datetime.date(datetime.now() - timedelta(days = 1)))
list_date_previous =   list_date_previous.strftime("%Y") + "_" +list_date_previous.strftime("%m") + "_" +list_date_previous.strftime("%d")
#print(list_url)
def checkname_error(index , next_index , judge_index , link_index , vs_index , category_index , cr_index , error):
    if vs_index != 'NONE':
        if data[index-1][vs_index-1] != "":
            sheet.update_cell( index,vs_index ,"")
    if  next_index != 'NONE':
        if data[index-1][next_index-1] != error:
            sheet.update_cell( index,next_index ,error)
    if link_index != 'NONE':
        if data[index-1][link_index-1] != "":
            sheet.update_cell( index,link_index ,"")
    if judge_index != 'NONE':
        if data[index-1][judge_index-1] != "":
            sheet.update_cell( index,judge_index ,"")
    if category_index != 'NONE':
        if data[index-1][category_index-1] != "":
            sheet.update_cell( index,category_index ,"")
    if il_index != 'NONE':           
        if data[index-1][il_index-1] != "":
            sheet.update_cell( index,il_index ,"")
    if cr_index != 'NONE':
        if data[index-1][cr_index-1] != "":
            sheet.update_cell( index,cr_index ,"")

if debug == 0 or debug == 2:    
    if os.path.exists('token.pkl'):
        creds_calander = pickle.load(open("token.pkl" ,'rb'))

    if not creds_calander or not creds_calander.valid:
            if creds_calander and creds_calander.expired and creds_calander.refresh_token:
                creds_calander.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json" , scopes = scopes_calander)
                creds_calander = flow.run_console()
                pickle.dump(creds_calander, open("token.pkl" ,'wb'))
    service = build("calendar" , "v3" ,credentials = creds_calander)
    calendar_list = service.calendarList().list().execute()
    for y in calendar_list['items']:
        if y['summary'] == 'Cases':
            calendarid = y['id']
repeated_cases = []
repeated_case_found = 0

headers = { 
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40'
}
if debug == 0 :
    sheet = client.open("cases").sheet1
    print("NORMAL MODE")
else :
    sheet = client.open("casestest").sheet1
    print("DEBUG MODE {0} ENABLED".format(debug))




temp = sheet.row_values(1)
data = sheet.get_all_values()

for element in temp:
    temp[temp.index(element)] = element.upper()
#convert the text to upper


if 'CASE' in temp:  # this indexes start from one also g spread accepts these indexes
    case_index = temp.index('CASE') + 1
else:
    case_index = 'NONE'
if 'LINK' in temp:
    link_index = temp.index('LINK') + 1
else:
    link_index = 'NONE'
if 'JUDGE' in temp:
    judge_index = temp.index('JUDGE') + 1
else:
    judge_index = 'NONE'
if 'NEXT DATE' in temp:
    next_index = temp.index('NEXT DATE') + 1
else:
    next_index = 'NONE'
if 'VS' in temp:
    vs_index = temp.index('VS') + 1
else:
    vs_index = 'NONE'
if 'CR NO' in temp:
    cr_index = temp.index('CR NO') + 1
else:
    cr_index = 'NONE'
if 'PERSONAL COMMENTS' in temp:
    pc_index = temp.index('PERSONAL COMMENTS') + 1
else:
    pc_index = 'NONE'
if 'CATEGORY' in temp:
    category_index = temp.index('CATEGORY') + 1
else:
    category_index = 'NONE'
if 'INTERIM' in temp:
    il_index = temp.index('INTERIM') + 1
else:
    il_index = 'NONE'
excelfile = sheet.col_values(case_index)
file1 = excelfile[-1:0:-1] # for reversal # reversing the column so that news cases get updated first
# now you can pass any subset of excel file and it will handel and update changes to main file so you can prioritize via date maybe


caseschecked  = 0
for line in file1 :
    caseschecked+=1
    try:
        index = excelfile.index(line) + 1
        
        if index == case_index:
            continue
        
        
        
        if excelfile.count(line) >1 :
            #print ("case repeated")
            repeated_case_found =1
            try:
                repeated_cases.index(line)
                
            except ValueError:
                repeated_cases.append(line)
        line = line.upper()
        time.sleep(1)
        idfound = 0
        update = 0
      
        try:
            if line[0] == ' ' or line == '\n':
                print("empty space passing on")
                continue
        except IndexError:
            print ("index error")
            continue
    
        if line != '\n' and line != '':   
            array = line
            personal_comments = "NONE"
            if line.find('"') != -1 :
                personal_comments = line.split('"')[1]
                if personal_comments.find('"') :
                    personal_comments = personal_comments.split('"')[0]
                    array = line.split('"')[0]
            if array.find(' ') != -1:
                array =  array.split(' ')
                try:
                    while '' in array:
                        array.pop(array.index(''))
                except ValueError:
                    pass
            else :
                checkname_error(index , next_index , judge_index , link_index , vs_index , category_index , cr_index , "CHECK NAME")
            
            try:    
                if array[2] == '\n':
                    print('check name')  
                    if data[index-1][next_index-1] != "CHECK NAME":
                        sheet.update_cell( index,next_index ,"CHECK NAME")
                if '\n' in array[2] :
                    array[2] = (array[2])[:(len(array[2]) - 1)]
                if len(array[2]) == 2 :
                    #print("year length error correcting automatically")
                    array[2] = '20' + array[2]
                    
                elif len(array[2]) != 4:
                    checkname_error(index , next_index , judge_index , link_index , vs_index , category_index , cr_index , "CHECK NAME")
                    continue
            except IndexError:
                checkname_error(index , next_index , judge_index , link_index , vs_index , category_index , cr_index , "CHECK NAME")
                continue
                
            
            case = {
                't_case_type': array[0],
                't_case_no': array[1],
                't_case_year': array[2],
                'submit': 'Search Case'
                    }


            with requests.Session() as s:
                url = 'https://www.phhc.gov.in/home.php?search_param=case'
                try:
                    res = s.get(url , headers = headers , timeout = 20)
                    res = s.post(url,data = case,headers=headers , timeout = 20 )
                    
                except requests.exceptions.RequestException :
                    print('request error occured')
                    continue
                except requests.exceptions.Timeout :
                    print ("timeout occured")
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                except requests.exceptions.HTTPError:
                    continue
                
                
                #print(res.text)
        
                id1 = case['t_case_type'] + '-' + case['t_case_no'] + '-' + case['t_case_year'] 
                id2 = case['t_case_type'] + ' ' + case['t_case_no'] + ' ' + case['t_case_year']
                
                #print(id1)
                if "<tr class='alt_no_data'><td colspan=8 align=center>No Case Found</td></tr>" in res.text or "no case found" in res.text.lower():
                    print( id1 + ' no case found')
                    checkname_error(index , next_index , judge_index , link_index , vs_index , category_index , cr_index , "CASE NOT FOUND")
                        
                    
                    continue
                else :
                    try:
                        
                        print(id1 + " ---> " + "{:.2f}".format(caseschecked/(len(file1)) *100) +"%")
                        link = (((res.text.split('<td  style=text-align:left>'))[1]).split('</td>'))[0]
                        link = "https://www.phhc.gov.in/" + (link.split("<a href='")[1]).split("' target='_blank'>")[0]
                        if data[index-1][case_index-1] != id2:
                            sheet.update_cell( index,case_index ,id2)
                        if pc_index !='NONE' and personal_comments != 'NONE':
                            if data[index-1][pc_index-1] != personal_comments:
                                sheet.update_cell( index,pc_index ,personal_comments)
                        
                        petitionname = (((res.text.split('<td  style=text-align:left>'))[2]).split('</td>'))[0]
                        respondentname = (((res.text.split('<td  style=text-align:left>'))[3]).split('</td>'))[0]
                        next_date = (((res.text.split('<td  style=text-align:left>'))[6]).split('</td>'))[0]
                        
                        if vs_index != 'NONE':
                            if data[index-1][vs_index-1] != petitionname + " VS " + respondentname:
                                sheet.update_cell( index,vs_index ,petitionname + " VS " + respondentname)
                        if  next_index != 'NONE':
                            if data[index-1][next_index-1] != next_date:
                                sheet.update_cell( index,next_index ,next_date)
                            if next_date =='NOT REQUIRED' or next_date == 'NOT AVAILABLE' :
                                if judge_index != 'NONE':
                                    if data[index-1][judge_index-1] != '':
                                        sheet.update_cell( index,judge_index ,'')
                                if category_index != 'NONE':
                                    if data[index-1][category_index-1] != '':
                                        sheet.update_cell( index,category_index ,'')
                                if cr_index != 'NONE':
                                    if data[index-1][cr_index-1] != '':
                                        sheet.update_cell( index,cr_index ,'')
                                if il_index != 'NONE':           
                                    if data[index-1][il_index-1] != '':
                                        sheet.update_cell( index,il_index ,'')

                       
                        if link_index != 'NONE':
                            
                            if data[index-1][link_index-1] != link:
                                
                                sheet.update_cell( index,link_index ,link)
                        
                        #next_date = 'NOT REQUIRED'
                        



                            

                                
                    except IndexError :
                        print('Index error')
                        continue
                    
                    if next_date != 'NOT REQUIRED' and next_date != 'NOT AVAILABLE' :
                        page_token = None
                        if debug == 0 or debug == 2 :
                            while idfound == 0:
                                
                                events = service.events().list(calendarId=calendarid ,pageToken=page_token).execute()
                                # eventupdated is variable name and think of something about pagetoken 
                                #print(events)
                                for x in events['items']:
                                    if x['summary'].upper() == id1 :
                                        events = x
                                        idfound = 1
                                        break    
                                                        
                                page_token = events.get('nextPageToken')
                                if not page_token:
                                    break                      
                        
                        #print(x['description'])
                        array = next_date.split("-")
                        array[2] = '20' + array[2]
                        next_date_char = array[0]+"-"+array[1]+"-"+array[2]
                        array[1] = month[array[1].upper()] 
                    
                        next_date = array[2] +'-' + array[1] + '-' + array[0]
                        next_date2 = array[2] +'_' + array[1] + '_' + array[0]
                        next_date3 = array[0] +'/' + array[1] + '/' + array[2]
                        
                        events = {
                            'summary': id1,
                            'description': "'" + petitionname + "'" + ' VS ' + "'" + respondentname + "' " +'\n' + "link : " + link ,
                                'start': {
                            'dateTime': next_date+'T'+'09:00:00+05:30'},
                                'end': {
                            'dateTime': next_date+'T'+'13:00:00+05:30'},
                                #'attendees': [
                                #{'email': 'chawlaadvocate@gmail.com','displayname' : 'Anil Chawla'},
                                #{'email': 'monica44a@gmail.com','displayname' : 'Monica Chawla'}
                                #],
                            'reminders': {
                            'useDefault': False,
                            'overrides': [
                            #{'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 60}
                            ],
                                        },
                                'sendUpdates' : 'none'
                                }
                        if personal_comments != 'NONE':
                            events['description'] += "\nPersonal Comments : " + personal_comments
                            update = 1


                        if  list_date_current == next_date2 or list_date_next == next_date2 or list_date_previous == next_date2:   
                            
                            try:
                                list_pdf = s.get(link , headers = headers  , timeout = 20)
                                print ('case tommorow')
                                
                                #print('<td align=left width="12%" class="data_sub_item" >' + next_date_char.upper())
                                #print(list_pdf.content)
                                #print(next_date_char.upper())
                                #list_pdf = ((list_pdf.text.split('<td align=left width="12%" class="data_sub_item" >' + next_date_char.upper()+'</td>')[1]).split('</tr>')[0])
                                
                                category = (((list_pdf.text.split('<td align=left width="12%" class="data_sub_item" >' + next_date_char.upper()+'</td>')[1]).split('</tr>')[0]).split('<td align=left width="11%" class="data_sub_item" >')[1]).split('</td>')[0]
                                
                                judgename =(list_pdf.text.split('<td colspan=2 align=left width="77%" class="data_sub_item" >')[1]).split('</td>')[0]
                                
                                if judgename.find(";"):
                                    judgenameSearch = judgename.split(";")[0]
                                
                                
                                if judge_index != 'NONE':
                                    if data[index-1][judge_index-1] != judgename:
                                        sheet.update_cell( index,judge_index ,judgename)
                                
                                if category_index != 'NONE':
                                    if data[index-1][category_index-1] != category:
                                        sheet.update_cell( index,category_index ,category)
                                                  
                                
                                try:
                                    
                                    interim_link = "https://www.phhc.gov.in/" + ((((list_pdf.text.split('<td style="text-align:left">' + next_date_char.upper()+'</td>')[1]).split('</tr>')[0]).split('<a href="javascript:;" onclick="window.open(')[1]).split('''')">''')[0]).split("'")[1]
                                    
                                    events['description'] +=  '\n' + "Category : " + category + "\n" +"Judge : " + judgename + '\n' + "view interim at " + interim_link
                                    if il_index != 'NONE':           
                                        if data[index-1][il_index-1] != interim_link:
                                            sheet.update_cell( index,il_index ,interim_link)

                                            
                                except IndexError:
                                    events['description'] +=  '\n' + "Category : " + category + "\n" +"Judge : " + judgename + '\n' 
                                #events = service.events().update(calendarId=calendarid, eventId=x['id'], body=events).execute()
                                #print(interim_link)
                                
                                #cause_list={
                                #    'cl_date':array[0]+'/'+array[1]+'/'+array[2],


                                #}
                                #print(list_pdf)
                                
                            
                                #print("here3")
                                obj = s.get('https://www.phhc.gov.in/home.php?search_param=jud_cl' , headers = headers , timeout = 20)
                                #print("here4")
                                
                                judgenameactual = judgenameSearch[8:]
                                if judgenameactual in obj.text:
                                    judgenameactual = obj.text.find(judgenameactual)
                                try :
                                       # check this
                                    judgenameactual = obj.text[judgenameactual -11 : judgenameactual + 1].split('=')[1].split('>')[0]
                                    category = category_dict[category.split(':')[0]]
                                
                                    judge_search = {
                                    'cl_date' : next_date3,
                                    't_jud_code' : judgenameactual,
                                    't_list_type' : category,
                                    'submit':'Search Case'
                                            }
                                    #print(judge_search)
                                    obj = s.post('https://www.phhc.gov.in/home.php?search_param=jud_cl' , data = judge_search , headers = headers , timeout = 20)
                                    #print(obj.content)
                                    if obj.text.find(id1) != -1 :
                                        #print("here")
                                        court_no = obj.text.split('<u>CR NO ')[1].split('</u>')[0]
                                          
                                        if cr_index != 'NONE':
                                            if data[index-1][cr_index-1] != ("CR NO = " + court_no):
                                                sheet.update_cell( index,cr_index ,"CR NO = " + court_no)
                                        events['description'] += "Court number : " + court_no 
                                except IndexError:
                                    print("couldn't find court number")
                                    pass
                                update = 1
                                #events = service.events().update(calendarId=calendarid, eventId=x['id'], body=events).execute()
                                #print(id1 + ' caseupdated')

                            except IndexError:
                                print('nextdate error')
                                
                            except requests.exceptions.Timeout:
                                print ("timeout occured")
                                pass
                            except requests.exceptions.RequestException:
                                print("request error ocuured")
                                pass
                            except requests.exceptions.ConnectionError:
                                continue
                            except requests.exceptions.HTTPError:
                                continue
                        else:
                            
                            if judge_index != 'NONE':
                                if data[index-1][judge_index-1] != '':
                                    sheet.update_cell( index,judge_index ,'')
                            if category_index != 'NONE':
                                if data[index-1][category_index-1] != '':
                                    sheet.update_cell( index,category_index ,'')
                            if cr_index != 'NONE':
                                if data[index-1][cr_index-1] != '':
                                    sheet.update_cell( index,cr_index ,'')
                            if il_index != 'NONE':           
                                if data[index-1][il_index-1] != '':
                                    sheet.update_cell( index,il_index ,'')
                    
                        if idfound == 0 and (debug == 0 or debug == 2):
                            events = service.events().insert(calendarId=calendarid, body=events).execute()
                            eventupdated = True
                            print ('Event created: %s' % (events.get('htmlLink')))
                        elif ( idfound == 1 and next_date !=(x['start']['dateTime'][:10]) ) or update == 1 and(debug == 0 or debug == 2) :
                            update = 0
                            events = service.events().update(calendarId=calendarid, eventId=x['id'], body=events).execute()
                            eventupdated = True
                            print(id1 + ' caseupdated')# %(events.get('htmlLink')))
                            #print (events['updated'])
                    
                    
                    
                    
                    
                    
                    elif next_date == 'NOT REQUIRED' and (debug == 0 or debug == 2):
                        
                        #print ("date not required delete case") 
                        page_token = None
                        while True:
                            events = service.events().list(calendarId=calendarid , pageToken=page_token).execute()
                            for x in events['items']:
                                if x['summary'].upper() == id1 :
                                    events = x
                                    if x['description'].find("Date not Required") == -1:
                                        x['description'] += "\nDate not Required"
                                        events = service.events().update(calendarId=calendarid, eventId=x['id'], body=events).execute()
                                    #service.events().delete(calendarId=calendarid, eventId=x['id']).execute()    
                                    #print('event deleted')
                                    break
                            page_token = events.get('nextPageToken')
                            if not page_token:
                                break
                        
                        
                                
                        
                            

                    #print("{0} {1} {2}".format(id1 , petitionname , next_date))
                
    except gspread.exceptions.APIError:
        print("api error")
        continue       
    except gspread.exceptions.GSpreadException:
        print("some gspread error")
        continue    
    except requests.exceptions.RequestException:
        print("some requests error")
        continue
    # except:
    #     print("some unknown error")
    #     continue
if repeated_case_found == 1:              
     
    for element in repeated_cases:
        occurence = 0
        excelfile = sheet.col_values(case_index)
        data = sheet.get_all_values()
        time.sleep(2)
        for i in range(len(excelfile)):
            if excelfile[i] == element :
                occurence = occurence +1
                if occurence > 1:
                    print (data[i][case_index-1])
                    sheet.delete_rows(i+1 -occurence +2)
                    print('repeated case deleted')
                
            
# print('''
#   _____   _   _   _____     _____   _   _   _____   _   _   ____    _____     ____     ____   ___   _____   _   _   _____   ___   ____    _____
#  |_   _| | | | | | ____|   |  ___| | | | | |_   _| | | | | |  _ \  | ____|   / ___|   / ___| |_ _| | ____| | \ | | |_   _| |_ _| / ___|  |_   _|
#    | |   | |_| | |  _|     | |_    | | | |   | |   | | | | | |_) | |  _|     \___ \  | |      | |  |  _|   |  \| |   | |    | |  \___ \    | | 
#    | |   |  _  | | |___    |  _|   | |_| |   | |   | |_| | |  _ <  | |___     ___) | | |___   | |  | |___  | |\  |   | |    | |   ___) |   | | 
#    |_|   |_| |_| |_____|   |_|      \___/    |_|    \___/  |_| \_\ |_____|   |____/   \____| |___| |_____| |_| \_|   |_|   |___| |____/    |_| 
#                                                                                                                                                 ''')



  
os.system("pause")
