
from bs4 import BeautifulSoup
import pandas as pd


URL ='https://www.onewestbank.com/handlers/StoreLocationsHandler.ashx?BranchLocationsId=23622321295'
df = pd.read_csv(URL,delimiter=",")
df['locator_domain']="https://www.onewestbank.com"
df['country_code']="US"
df['page_url']="<MISSING>"
df['HoursBiz']=df['HoursBiz'].str.split("Please note",n = 1,expand = True).replace("<p>","")
rows = []
for t in df['HoursBiz']:
    soup = BeautifulSoup(t,"lxml")
    rows.append(soup.get_text().replace("Sunset Park branch is closed",'').replace(";","").strip().lstrip())
df['HoursBiz'] = rows
df['HoursBiz']=df['HoursBiz'].replace("ATM Only","<MISSING>").str.encode('ascii', 'ignore').str.decode('ascii').replace("<p>",'').replace("\n"," ").replace(";","").replace("<p>Sunset Park branch is closed","")
df['Phone']=df['Phone'].replace("ATM Only","<MISSING>")
df['ATM']=df['ATM'].replace("yes","ATM").replace("no","branch")
df['BranchID']=df['BranchID'].str.replace("T","")
df=df.drop(['Safekeeping','DriveThru','Fax'], axis = 1) 
df = df.rename(columns={'BranchName': 'location_name', 'Street': 'street_address',"City":"city","State":"state","Zip":"zip","Xcoord":"latitude","Ycoord":"longitude","HoursBiz":"hours_of_operation","ATM":"location_type","Phone":"phone","BranchID":"store_number"})
df['street_address']=df['street_address'].str.replace("&amp;",'')
df = df[["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"]]
df.to_csv('data.csv',index=None)

