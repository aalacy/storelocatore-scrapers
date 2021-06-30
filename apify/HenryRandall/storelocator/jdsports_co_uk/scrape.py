import csv
import re
from sgselenium import SgSelenium
from bs4 import BeautifulSoup


def fetch_data():
    driver = SgSelenium().chrome()
    link = "https://www.jdsports.co.uk/store-locator/all-stores/"
    driver.get(link)
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
        driver = SgSelenium().chrome()
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
        city = coor.find("img", {"id": "staticMapImage"})
        city = city.attrs["src"].split("&zoom=15", 1)[0]
        city = city.split(",")[-1]
        coor = coor.find("div", {"id": "staticMap"})
        coor = coor.attrs["data-staticmapmarkers"].split("|", 1)[1].split('"', 1)[0]
        [lat, long] = coor.split(",")
        location_data = [
            base_url,
            loc_url,
            location[0],
            street,
            city,
            "<MISSING>",
            zip_code,
            "<MISSING>",
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
