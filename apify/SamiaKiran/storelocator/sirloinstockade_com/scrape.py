from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sirloinstockade_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    final_data = []
    url = "https://sirloinstockade.com/store-locator/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=location]")
    linklist = [temp.get("href") for temp in linklist]
    linklist = list(set(linklist))
    for link in linklist:
        url = link
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        store = soup.find("div", {"class": "wpseo-location"})
        store = store.get("id")
        store = store.split("location-", 1)[1]
        title = soup.find("span", {"class": "wpseo-business-name"}).text
        street = soup.find("div", {"class": "street-address"}).text
        state = soup.find("span", {"class": "region"}).text
        city = soup.find("span", {"class": "locality"}).text
        pcode = soup.find("span", {"class": "postal-code"}).text
        phone = soup.find("span", {"class": "wpseo-phone"}).find("a").get("href")
        phone = phone.split("tel:", 1)[1]
        hours_list = soup.find("div", {"class": "wpseo-opening-hours-wrapper"})
        temp = soup.find("meta", {"name": "geo.position"})
        temp = temp["content"]
        lat = temp.split(";", 1)[0]
        long = temp.split(";", 1)[1]
        hours_list = hours_list.findAll("tr")
        hours = ""
        for temp in hours_list:
            try:
                day = temp.find("td").text
                temp_hour = temp.find("span").text
                hours = hours + day + " " + temp_hour + " "
            except:
                day = temp.find("td").text
                temp_hour = temp.find("td").text
                hours = hours + day + " " + temp_hour + " "
        final_data.append(
            [
                "https://sirloinstockade.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                long,
                hours,
            ]
        )
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
