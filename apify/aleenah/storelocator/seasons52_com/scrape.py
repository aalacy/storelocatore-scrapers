import csv
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import re
import os


def get_chromedriver(use_proxy=False, user_agent=None):

    chrome_options = webdriver.ChromeOptions()
    seleniumwire_options = {}

    if use_proxy and 'PROXY_PASSWORD' in os.environ:
        DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
        proxy_password = os.environ["PROXY_PASSWORD"]
        url = os.environ["PROXY_URL"] if 'PROXY_URL' in os.environ else DEFAULT_PROXY_URL
        proxy_url = url.format(proxy_password)
        # print('proxy_url', proxy_url)
        seleniumwire_options = {
            'proxy': {
                'https': proxy_url
            }
        }

    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # driver = webdriver.Chrome('C:\chromedriver.exe', chrome_options=chrome_options, seleniumwire_options=seleniumwire_options)
    driver = webdriver.Chrome(
        'chromedriver', chrome_options=chrome_options, seleniumwire_options=seleniumwire_options)

    driver.implicitly_wait(10)

    return driver


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'

driver = get_chromedriver(use_proxy=True, user_agent=user_agent)

wait = WebDriverWait(driver, 30)

# to check that the proxy is working ..
# driver.get("https://jsonip.com/")
# print(driver.page_source)
# raise SystemExit


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "operating_info", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    # print('user agent: ', driver.execute_script("return navigator.userAgent;"))
    abv = {'alabama': 'AL', 'arizona': 'AZ', 'california': 'CA', 'colorado': 'CO', 'florida': 'FL', 'georgia': 'GA', 'illinois': 'IL', 'indiana': 'IN', 'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI',
           'missouri': 'MO', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'ohio': 'OH', 'pennsylvania': 'PA', 'tennessee': 'TN', 'texas': 'TX', 'virginia': 'VA', }
    locs = []
    street = []
    states = []
    cities = []
    countries = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ulinks = []
    gms = []
    urls = []

    starting_url - "https://www.seasons52.com/locations/all-locations"
    driver.get(starting_url)

    try:
      # div = driver.find_element_by_class_name("fin_all_location_sec")
      div = wait.until(presence_of_element_located((By.CSS_SELECTOR, ".fin_all_location_sec")))
    except:
      body = wait.until(presence_of_element_located((By.TAG_NAME, "body")))
      print(starting_url)
      print(body.text[0:1000])
      raise SystemExit

    uls = div.find_elements_by_css_selector("ul")
    for ul in uls:
        lis = ul.find_elements_by_css_selector("li")
        s = ""
        for li in lis:
            h = li.get_attribute("class")
            if h == "heading_li":
               s = li.text
               continue
            elif h == "subheading_li":
                l = li.text
            states.append(s)
            locs.append(l)
    ast = driver.find_elements_by_tag_name("a")
    for a in ast:
        if a.get_attribute("id") == "locDetailsId":
            urls.append(a.get_attribute("href"))
    i = 0

    for url in urls:
        """
        loc=loc.lower()
        if "-" in loc:
            lo = loc.split("-")
            loc1=lo[0].strip().replace(" ","-")
            loc2=loc.replace("- ","").replace(" ","-")
        else:
            if " " in loc:
                loc1=loc.replace(" ","-")
                loc2=loc1
            else:
                loc1=loc2=loc
        url="https://www.seasons52.com/locations/"+abv[states[i].lower()]+"/"+loc1+"/"+loc2
        """
        driver.get(url)

        try:
          div = wait.until(presence_of_element_located((By.CSS_SELECTOR, ".left-bar")))
          # div = driver.find_element_by_class_name("left-bar")
        except:
          body = wait.until(presence_of_element_located((By.TAG_NAME, "body")))
          print(url)
          print(body.text[0:1000])
          raise SystemExit

        try:
            gm = driver.find_element_by_id("globalMessage").text.replace(
                "\r\n", " ").replace("\n", " ").strip()
        except:
            gm = "<MISSING>"
        # print(gm)
        gms.append(gm)
        p = div.find_element_by_tag_name("p")
        t = p.text.split("\n")
        street.append(t[0])
        phones.append(t[2])
        t = t[1].split(",")
        cities.append(t[0])
        zips.append(t[1].split(" ")[-1])
        i += 1
        lis = driver.find_elements_by_css_selector("li")
        tim = ""
        for lin in lis:
            id = lin.get_attribute("class")
            if id == "weekday-active rolling-width" or id == "time rolling-hours-start"or id == "weekday rolling-width":
                tim += lin.text
        timing.append(tim.replace("FRI SEP 20", "").replace("EDT 2019", ""))
        latlong = driver.find_element_by_id(
            "restLatLong").get_attribute("value").split(",")
        lat.append(latlong[0])
        long.append(latlong[1])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.seasons52.com")
        row.append(gms[i])
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])

        all.append(row)
    return(all)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
