import csv
from bs4 import BeautifulSoup as bs
import re
import time
from sgrequests import SgRequests
from sgselenium import SgSelenium

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgSelenium().chrome()
    base_url = "http://crosbysmarkets.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
    }
    r = session.get("http://crosbysmarkets.com/locations", headers=headers)
    soup = bs(r.text, "lxml")
    url = soup.find("iframe")["data-src"]
    driver.get(url)
    time.sleep(5)
    driver.find_element_by_xpath(
        "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]"
    ).click()
    time.sleep(5)
    soup = bs(driver.page_source, "lxml")
    names = []
    for dt in soup.find_all(
        "div", {"class": "HzV7m-pbTTYe-ibnC6b pbTTYe-ibnC6b-d6wfac"}
    ):
        names.append(dt.text)
    for index, i in enumerate(names, start=2):
        location_name = i
        driver.find_element_by_xpath(
            '//*[@id="legendPanel"]/div/div/div[2]/div/div/div[2]/div/div/div[3]/div['
            + str(index)
            + "]/div[2]/div"
        ).click()
        time.sleep(5)
        soup = bs(driver.page_source, "lxml")
        latitude = soup.find("a", {"dir": "ltr"})["href"].split("@")[1].split(",")[0]
        longitude = soup.find("a", {"dir": "ltr"})["href"].split("@")[1].split(",")[1]
        adr = list(
            soup.find("div", {"class": "fO2voc-jRmmHf-MZArnb-Q7Zjwb"}).stripped_strings
        )[0].split(",")
        street_address = " ".join(adr[:-2])
        city = adr[-2]
        state = adr[-1].split()[0]
        zip1 = adr[-1].split()[-1]
        Source = soup.find("div", {"class": "qqvbed-VTkLkc"})
        for ph in re.findall(r"\+[-()\s\d]+?(?=\s*[+<])", str(Source)):
            phone = ph
        time.sleep(5)
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip1)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
        driver.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[3]/div[1]/div'
        ).click()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
