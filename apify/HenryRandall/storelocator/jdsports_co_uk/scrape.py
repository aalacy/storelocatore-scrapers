import csv
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    link = "https://www.jdsports.co.uk/store-locator/all-stores/"
    driver = get_driver(link, "storeName")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    locations = soup.find_all("li", {"data-e2e": "storeLocator-list-item"})
    base_url = "https://www.jdsports.co.uk"
    loclist = []

    for location in locations:
        name = location.find("h3", {"class": "storeName"}).text
        url = base_url + location.find("a", href=True)["href"]
        store_number = url.split("/")[-2]
        loc = [name, url, store_number]
        loclist.append(loc)

    data = []
    for location in loclist:
        loc_url = location[1]
        driver.get(loc_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        info = soup.find("div", {"class": "storeContentLeft"})
        address = info.find("div", {"id": "storeAddress"})
        address = address.find("p")
        address = address.text.replace("\n", "")
        address = address.split("\t")
        [street, zip_code] = [x for x in address if x]
        phone = info.find("div", {"id": "storeContact"})
        phone = phone.find("p").text
        phone = re.sub("[^0-9]", "", phone)
        if phone == "":
            phone = "<MISSING>"
        elif int(phone) == 0:
            phone = "<MISSING>"
        hours = info.find("div", {"id": "storeTimes"})
        days = hours.find_all("span", {"class": "day"})
        hours = hours.find_all("span", {"class": "time"})
        length = len(days)
        hoo = ""
        for x in range(length):
            hoo = hoo + days[x].text + " " + hours[x].text + ", "
        hoo = hoo[:-2]
        coor = soup.find("div", {"class": "storeContentRight"})
        coor = coor.find("div", {"id": "staticMap"})
        coor = coor.attrs["data-staticmapmarkers"].split("|", 1)[1].split('"', 1)[0]
        [lat, long] = coor.split(",")
        location_data = [
            base_url,
            loc_url,
            location[0],
            street,
            "<MISSING>",
            "<MISSING>",
            zip_code,
            "UK",
            location[2],
            phone,
            "<MISSING>",
            lat,
            long,
            hoo,
        ]
        data.append(location_data)
    return data


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )

        for row in data:
            writer.writerow(row)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
