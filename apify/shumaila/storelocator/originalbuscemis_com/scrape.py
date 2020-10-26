from selenium import webdriver
import re, time, csv
import requests
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('originalbuscemis_com')




def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path, chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    driver = get_driver()
    # data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    data = []
    driver.get('https://originalbuscemis.com/locations/')
    repo_list = driver.find_elements_by_class_name('color_11')
    logger.info(len(repo_list))
    for i in driver.find_elements_by_xpath('//div[@class="results_wrapper"]'):
        title = i.find_element_by_css_selector('span[class="location_name"]').text

        street = i.find_element_by_css_selector('span[class="slp_result_address slp_result_street"]').text
        city= i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[
                0]
        state=  i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[
                1].split()[0]
        pcode=i.find_element_by_css_selector('span[class="slp_result_address slp_result_citystatezip"]').text.split(',')[
                1].split()[1]
        if i.find_element_by_css_selector('span[class="slp_result_address slp_result_phone"]').text == '':
            phone = '<MISSING>'
        else:
            phone = i.find_element_by_css_selector('span[class="slp_result_address slp_result_phone"]').text

        ccode = "US"
        hours = '<MISSING>'
        ltype = '<MISSING>'
        link = 'https://originalbuscemis.com/locations/'
        url = 'https://originalbuscemis.com'
        title = i.find_element_by_css_selector('span[class="location_name"]').text

        store = i.get_attribute('id')
        start = store.find("wrapper")
        start = store.find("_", start) + 1
        store = store[start:len(store)]
        #logger.info(store)
        geo_data = i.find_element_by_xpath('//*[@id="slp_right_cell_32"]/span[3]/a')
        geo_data = geo_data.get_attribute('href')
        driver1 = get_driver()
        driver1.get(geo_data)
        time.sleep(5)
        lat, longt = parse_geo(driver1.current_url)
        driver1.quit()
        data.append([
            url,
            link,
            title,
            street,
            city,
            state,
            pcode,
            ccode,
            store,
            phone,
            ltype,
            lat,
            longt,
            "<MISSING>"
        ])

    for i in range(0, len(repo_list)):
        detail = repo_list[i].text
        if detail.find("OPENING SOON!") > -1:
            break

        # logger.info(detail)
        start = 0
        end = detail.find("\n", start)
        title = detail[start:end]
        #logger.info(title)
        # data['location_name'].append(title)
        start = end + 1
        end = detail.find("\n", start)
        if end == -1:
            end =len(detail)
        street = detail[start:end]
        if street.find("-") > -1:
            phone = street
            street = title
            title = "<MISSING>"
        if end != len(detail):
            start = end + 1
            end = len(detail)
            phone = detail[start:end]


        #logger.info(title)
        #logger.info(street)
        #logger.info(phone)

        city = "<MISSING>"
        state = "<MISSING>"
        pcode = "<MISSING>"
        ccode = "US"

        store = "<MISSING>"
        flag = True
        for m in range(0,len(data)):

            if data[m][3].lower().find(street.lower()) > -1 :
                flag = False
                break
        if flag and title != "OPENING SOON":
            data.append([
                'https://originalbuscemis.com/',
                'https://originalbuscemis.com/locations/',
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>"
            ])
        #logger.info(data)
        # logger.info(data)

        # logger.info("...............")
    #for i in range(0, len(data)):
     #   logger.info(data[i])
    logger.info(len(data))


    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()