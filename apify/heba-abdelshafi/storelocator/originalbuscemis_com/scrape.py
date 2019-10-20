from selenium import webdriver
import pandas as pd
import re


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver=webdriver.Chrome('C:\chromedriver.exe')#, options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False,encoding='utf-8')

def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://originalbuscemis.com/locations/')

    for i in driver.find_elements_by_xpath('//div[@class="results_wrapper"]'):
        data['location_name'].append(i.find_element_by_css_selector('span[class="location_name"]').text)
        data['street_address'].append(i.find_element_by_css_selector('span[class="slp_result_address slp_result_street"]').text)
        data['city'].append(i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[0])
        data['state'].append(i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[1].split()[0])
        data['zip'].append(i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[1].split()[1])
        if i.find_element_by_css_selector('span[class="slp_result_address slp_result_phone"]').text=='':
            data['phone'].append('<MISSING>')
        else:
            data['phone'].append(i.find_element_by_css_selector('span[class="slp_result_address slp_result_phone"]').text)
        data['country_code'].append('US')
        data['longitude'].append('<MISSING>')
        data['latitude'].append('<MISSING>')
        data['hours_of_operation'].append('<MISSING>')
        data['store_number'].append('<MISSING>')
        data['location_type'].append(driver.find_element_by_xpath('//a[@class="custom-logo-link"]/img').get_attribute('alt'))
        data['page_url'].append('https://originalbuscemis.com/locations/')
        data['locator_domain'].append('https://originalbuscemis.com')

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
