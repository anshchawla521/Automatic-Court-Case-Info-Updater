# in cmd go and run the scripts/activate.bat file to activate environment
# to deactivate just type deactivate
# when python tries to run it automaticaaly tries to activate the environment using power shell
# in which we have to run activate.ps1 but it doesnt have permission
# Set-ExecutionPolicy RemoteSigned (type this in powershell as admin)
# Set-ExecutionPolicy Restricted

# known bugsf
# if u use multiple characters of the allowd then error may rise
# also the case types allowed list has been written manually so chnage that using bs4
import requests
import bs4
import os
import time
import concurrent.futures


characters_allowed = [" ", "/", "_"]
Case_types = ["CWP", "CRM-M", "CR", "RSA", "CRR", "CRA-S", "FAO", "CM", "CRM", "ARB", "ARB-DC", "ARB-ICA", "CA", "CA-CWP", "CA-MISC",
              "CACP", "CAPP", "CCEC", "CCES", "CEA", "CEC", "CEGC", "CESR", "CLAIM", "CMA", "CMM", "CO-COM", "COA", "COCP", "COMM-PET-M", "CP"]
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78'
}


def format_name(case_name):
    data = {"c_type": "",
            "number": "",
            "year": "",
            "name": ""}  # generates new dictionary for every instance
    case_name = case_name.upper()
    case_no = -1
    case_no_type = -1
    case_no_year = -1
    for characters in characters_allowed:
        if case_name.find(characters):
            if len(case_name.split(characters)) >= 3:
                case_name_list = case_name.split(characters)  # now its a list
                while '' in case_name_list:
                    case_name_list.remove('')
                if len(case_name_list) == 3:
                    case_no_type = case_name_list[0]
                    case_no_year = case_name_list[2]
                    case_no = case_name_list[1]
                    break
                    # no else here because error would be catched later

    if (case_no_type == -1 or case_no == -1 or case_no_year == -1):
        raise ValueError("{case_name} - not found".format(case_name=case_name))
    if len(case_no_year) == 2:
        case_no_year = '20'+case_no_year
    data.update({"c_type": case_no_type,
                 "number": case_no,
                 "year": case_no_year,
                "name": case_no_type + " "+case_no+" "+case_no_year})
    return data


def find_info(data):
    # print(data)
    case = {
        't_case_type': data["c_type"],
        't_case_no': data["number"],
        't_case_year': data["year"],
        'submit': 'Search Case'
    }
    with requests.session() as s:
        url = 'https://www.phhc.gov.in/home.php?search_param=case'
        try:
            # res = s.get(url, headers=headers, timeout=20)
            res = s.post(url, data=case, headers=headers, timeout=20)
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            res.close()
            # table is a bs4 set # have to do type casting
            table = soup.find_all(class_='alt')
            if len(table) == 0:
                table = soup.find_all(class_='alt_no_data')
                data.update({"status": table[0].text.strip()})
                # updating no case found as status
            else:
                soup = bs4.BeautifulSoup(str(table[0]), 'html.parser')
                # for i in range(0, 6):  # 6 paramters
                #     print(soup.find_all('td')[i].text.strip())
                link = soup.find('a')
                # access the href attribute of a tag
                link = 'https://www.phhc.gov.in/' + link['href']
                soup = soup.find_all('td')
                if len(soup) == 6:
                    data.update({"petiotioner": soup[1].text.strip(),
                                "respondent": soup[2].text.strip(),
                                 "advocate": soup[3].text.strip(),
                                 "status": soup[4].text.strip(),
                                 "nextdate": soup[5].text.strip(),
                                 "link": link
                                 })

        except Exception as error:
            # also introduce error handelling here
            print("error occured")
            print(repr(error))
            pass

    return data


def find_extrainfo(data):
    if 'status' in data.keys():
        if data['status'] == 'No Case Found':
            # no extra info can be found
            return data
    if 'link' not in data.keys():
        # find the link
        data = find_info(data)
        pass

    with requests.session() as s:
        try:
            # res = s.get(url, headers=headers, timeout=20)
            res = s.get(data['link'], headers=headers, timeout=20)
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            res.close()
            table = soup.find(text='Case Listing Details').find_all_next(
                class_='data_sub_item')
            # table = soup.find_all(class_='data_sub_item')
            # for x in table:
            #     print(x)
            data.update({"cause list date": table[0].text.strip(),
                        "judge": table[2].text.strip(),
                         "Order Link": table[3].text.strip(),
                         "list type": table[1].text.strip().split(":")[0],
                         "sr no": table[1].text.strip().split(":")[1]
                         })

        except Exception as error:
            print(repr(error))

    return data


cases_list = ['CM 6889-CWP 2020',
              'CWP 10274 2020',
              'FAO 6938 2015',
              'CWP 4639 2020',
              'FAO 4724 2015',
              'CR 7470 2018',
              'CR 9212 2018',
              'CWP 7301 2020',
              'CWP 7343 2020',
              'FAO 5145 2015',
              'CRM 10004 2015',
              'CWP 1642 2019',
              'CWP 1631 2019',
              'CWP 10900 2019',
              'CRR 2016 2009',
              'CWP 9072 2020',
              'CWP 19964 2019',
              'CWP 18227 2019',
              'CWP 25538 2016',
              'RSA 2694 2016',
              'CM 7804-CWP 2018',
              'RA-CW 135 2018',
              'CWP 14802 2017',
              'CWP 9030 2020',
              'CWP 9034 2020',
              'CWP 21411 2014',
              'RSA 301 2017',
              'RSA 3764 2017',
              'RSA 2211 2012',
              'CWP 15004 2018',
              'CWP 11890 2016',
              'CWP 33830 2019',
              'CWP 12506 2019',
              'CWP 4814 2020',
              'CWP 21392 2016',
              'CWP 17495 2016',
              'CWP 25417 2018',
              'CWP 5563 2019',
              'CWP 17193 2015',
              'RSA 354 2017',
              'FAO-M 286 2017',
              'CM 13469-C 2014',
              'COCP 2827 2019',
              'CR 8076 2019',
              'RSA 2043 2018',
              'RSA 3037 2018',
              'CRR 3790 2018',
              'CWP 33630 2019',
              'CWP 8239 2019',
              'CR 2608 2013',
              'CWP 31267 2019',
              'CWP 28142 2018',
              'CWP 1962 2020',
              'FAO-CARB 43 2018',
              'CWP 22642 2015',
              'CWP 12076 2019',
              'RSA 4933 2014',
              'CWP 24960 2016',
              'CWP 9369 2016',
              'CR 3649 2016',
              'CM 17428-CWP 2019',
              'CWP 1592 2020',
              'CR 3213 2019',
              'CWP 4665 2019'
              ]
cases_list_dict = []




if __name__ == '__main__':
    try:
        start = time.perf_counter()
        # data = format_name("")
        for x in cases_list:
            cases_list_dict.append(format_name(x))
        # #data = find_info(data)
        # data = find_extrainfo(data)
        with concurrent.futures.ThreadPoolExecutor() as executer:
            results = [executer.submit(find_extrainfo, x)
                       for x in cases_list_dict]
        # print(data)
        for x in results:
            print(x.result())
        finished = time.perf_counter()

        print(round(finished-start, 3))

    except Exception as error:
        print(repr(error))
