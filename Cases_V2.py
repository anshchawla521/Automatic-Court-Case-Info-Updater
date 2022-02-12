# %%
'''This program is responsible for doing webscraping and getting information about different cases. 
'''

import requests
import bs4

# %%
class Cases :
    '''this is a class for all the cases and contains all the neccesary methods required '''
    seperating_characters = [" ", "/", "_"] # repetition allowed but not mix and match
    url = 'https://www.phhc.gov.in/home.php?search_param=case'

    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78'
    }
    

    def __init__(self,**kwargs) -> None:
        '''class constructor which accepts the case name and then divides it into different pieces of info and standardizes it or it can also accept a data base with the properties of cases
        
        Arguments:
        case_name : str

        Returns:
        None

        '''
        if 'case_name' in kwargs: #object to be created using case name
            
            case_name = kwargs['case_name'].upper()


            # if seperating character found then will apply tests if failed then raises error and dosnt check for other characters
            for seperating_character in Cases.seperating_characters:
                if seperating_character in case_name: # check if the name contains the allowed characters
                    case_name_list = case_name.split(seperating_character) 
                    if len(case_name_list) >= 3: # more than 3 segments could be possible because of repeated alowed characters
                        while '' in case_name_list: # to account for repeated allowed characters if any
                            case_name_list.remove('') 
                        if len(case_name_list) == 3: # now only 3 elemts should be possible
                            case_no_type = case_name_list[0] # now assign first part as type
                            case_no_year = case_name_list[2] # now assign second part as year
                            case_no = case_name_list[1] # now assign third part as number
                            if case_no_year.isdigit():
                                raise ValueError('year was entered in wrong format or formatting was wrong')   
                            break # don check for other seperating characters
                        else:
                            raise NameError("case name doesn't contain 3 parts of info (maybe seperating characters were not used)")
                    else:
                        raise NameError("cannot break the name into 3 parts(maybe seperating characters were not used)")
            else:
                # if for loop executed succesfully it means there were no seperating characters 
                # in all other cases the loop would either end in break or name error 
                raise NameError("No seperating Character found")
            
            self.type = case_no_type # initialise object attributes
            self.year = case_no_year # initialise object attributes
            self.number = case_no # initialise object attributes

            if len(self.year) == 2: # to handel the entering of years like 01 which is actually 2001
                
                if 50 >=int(self.year) >= 0  :
                    self.year = '20'+self.year
                elif 99 >=int(self.year) > 50  :
                    self.year = '19'+self.year
                
                    
                

            self.name = self.type + " "+self.number+" "+self.year # initialise object attributes 
        else:
            # someother method of constructor 
            raise NotImplementedError('This constructor method doesnt exits')    
    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)
    def __getitem__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise KeyError('The key Doesnt exist for the object')
        
    def find_info(self) -> None:
        case = {
        't_case_type': self.type,
        't_case_no': self.number,
        't_case_year': self.year,
        'submit': 'Search Case'
        }
        with requests.session() as s:
            try:
                # res = s.get(url, headers=headers, timeout=20)
                res = s.post(Cases.url, data=case, headers=Cases.headers, timeout=20)
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                res.close()
                # table is a bs4 set # have to do type casting
                table = soup.find_all(class_='alt')  


                if len(table) == 0: # no case found 
                    
                    table = soup.find_all(class_='alt_no_data')
                    if len(table) != 0:
                        self.status = table[0].text.strip()
                    else:
                        raise Exception("unknown Response code 1")
                    
                else:
                    # if case found pick the top one
                    soup = bs4.BeautifulSoup(str(table[0]), 'html.parser')
                    # for i in range(0, 6):  # 6 paramters
                    #     print(soup.find_all('td')[i].text.strip())
                    link = soup.find('a')
                    # access the href attribute of a tag
                    link = 'https://www.phhc.gov.in/' + link['href']
                    soup = soup.find_all('td')
                    if len(soup) == 6:
                        self.petiotioner = soup[1].text.strip()
                        self.respondent = soup[2].text.strip()
                        self.advocate = soup[3].text.strip()
                        self.status = soup[4].text.strip()
                        self.nextdate = soup[5].text.strip()
                        self.link = link
                                    

            except Exception as error:
                # also introduce error handelling here
                print("error occured")
                print(repr(error))

    def find_extrainfo(self) -> None:
        # what if the status doesnt exist ????
        if 'status' in self.__dict__ and self.status == 'No Case Found':
                # no extra info can be found
            return 
        if 'link' not in self.__dict__:
            # find the link
            self.find_info()
            

        with requests.session() as s:
            try:
                # res = s.get(url, headers=headers, timeout=20)
                res = s.get(self.link, headers=Cases.headers, timeout=20)
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                res.close()


                table = soup.find(text='Case Listing Details').find_all_next(
                    class_='data_sub_item')
                # table = soup.find_all(class_='data_sub_item')
                # for x in table:
                #     print(x)
                self.cause_list_date = table[0].text.strip()
                self.judge = table[2].text.strip()
                self.order_link = table[3].text.strip()
                self.list_type = table[1].text.strip().split(":")[0]
                self.sr_no = table[1].text.strip().split(":")[1]
                

            except Exception as error:
                print(repr(error))

    def __iter__(self):
        return iter(self.__dict__.items())


# %%
case1 = Cases(case_name = 'cm 6889-CWP 2020')
case1.find_extrainfo()

# %%
print(case1)
# %%
case1.__iter__()
# %%
for x ,y in case1:
    print(f'{x} : {y}')
# %%
