from selenium import webdriver
import pandas as pd


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
driver=webdriver.Chrome('C:\chromedriver.exe')#, options=options)
#driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)

def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://hatcreekburgers.com/')
    
    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath("//li[contains(@class,'menu-item menu-item-type-custom menu-item-object-custom current-menu-ancestor current-menu-parent menu-item-has-children menu-item')]//li[contains(@class,'menu-item menu-item-type-post_type menu-item-object-page menu-item-')]/a")]
    
    for url in location_data_urls:
        if 'airport' not in url:
            driver.get(url)
            data['page_url'].append(url)
            data['locator_domain'].append('https://hatcreekburgers.com/')
            data['country_code'].append('US')
            data['store_number'].append('<MISSING>')
            data['location_name'].append(driver.find_element_by_xpath('//div[@class="fl-rich-text"]/h1').text)
            sub_data=driver.find_element_by_xpath('//div[@class="fl-rich-text"]/h1/following-sibling::p').text.split('\n')
            data['street_address'].append(sub_data[0])
            data['city'].append(sub_data[1].split(',')[0])
            data['state'].append(sub_data[1].split(',')[1].split()[0])
            data['zip'].append(sub_data[1].split(',')[1].split()[1])
            data['phone'].append(sub_data[2])
            data['hours_of_operation'].append(driver.find_element_by_xpath('//div[@class="fl-rich-text"]/h2/following-sibling::p').text)
            data['location_type'].append(driver.find_element_by_xpath('//meta[@itemprop="name"]').get_attribute('content'))
            data['longitude'].append('<MISSING>')
            data['latitude'].append('<MISSING>')

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
