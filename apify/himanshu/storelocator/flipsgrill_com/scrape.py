#!/usr/bin/env python
# coding: utf-8

# In[35]:


import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


# In[36]:



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


# In[ ]:





# In[ ]:





# In[37]:


base_url = 'https://flipsgrill.com' 
r = session.get(base_url + '/locations')
soup = BeautifulSoup(r.text, "lxml")
soup


# In[51]:


def fetch_data():
    data = []
    div = (soup.find("div", {"class": "et_pb_row et_pb_row_1"}))
    cards = div.findChildren("div", {"class": "et_pb_column"})
    for card in cards:
        row = []
        #locator_domain
        row.append(base_url)
        #location_name
        title = card.find("h5", {"class": "et_pb_toggle_title"})
        row.append('Flips Grill-' + title.text)
        card_content = card.find("div", {"class": "et_pb_toggle_content"})
        texts = card_content.findAll("p")
        helpful_texts = []
        for text in texts:
            if text.text.strip() != '':
                helpful_texts.append(text.text.strip())

        address = helpful_texts[0]
        durations_and_phoneNumber = helpful_texts[1].split('\n')
        duration = durations_and_phoneNumber[0]
        phoneNumber = helpful_texts[1].split('\n')[len(durations_and_phoneNumber) - 1]
        #street Address
        row.append(address.split('\n')[0])
        #city
        row.append(title.text)
        #state
        address_last_parts = address.split('\n')[1].split(' ');
        row.append(address_last_parts[len(address_last_parts)-2])
        #zip
        row.append(address_last_parts[len(address_last_parts)-1])
        #country_code
        row.append('US')
        #store number
        row.append('<MISSING>')
        #phone number
        row.append(phoneNumber)
        #location_type
        row.append(soup.find("div", {"class": "logo_container"}).findChildren('img')[0]['alt'])
        #longitute
        row.append('<INACCESSIBLE>')
        #latitude
        row.append('<INACCESSIBLE>')
        #hours_of_operation
        row.append(duration)        
        data.append(row)

    return data


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[52]:


def scrape():
    data = fetch_data()
    write_output(data)
scrape()


# In[ ]:




