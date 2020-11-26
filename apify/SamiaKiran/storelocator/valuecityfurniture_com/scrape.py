from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("valuecityfurniture_com")

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
    url = "https://www.valuecityfurniture.com/store-locator/show-all-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "store-locator-stores-result-list-item"})
    for loc in loclist:
        title = loc.find("strong", {"class": "sl-storename"}).text
        phone = loc.find("span", {"class": "sl-phone"}).text
        phone = phone.strip()
        street = loc.find("span", {"itemprop": "streetAddress"}).text
        city = loc.find("span", {"itemprop": "addressLocality"}).text
        state = loc.find("span", {"itemprop": "addressRegion"}).text
        pcode = loc.find("span", {"itemprop": "postalCode"}).text
        hour_list = loc.find("div", {"class": "store-hours-table"})
        hour_list = hour_list.findAll("ul")
        hours = ""
        for temp in hour_list:
            day = temp.find("li").text
            time = temp.find("time", {"itemprop": "openingHours"}).text
            hours = hours + day + " " + time + " "
        final_data.append(
            [
                "https://www.valuecityfurniture.com/",
                "https://www.valuecityfurniture.com/store-locator/show-all-locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                hours,
            ]
        )
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
