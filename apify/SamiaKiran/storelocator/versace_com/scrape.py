import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "versace_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[8],
                row[10],
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        log.info(f"No of records being processed: {len(temp_list)}")


def get_store_data(soup, link):
    address = soup.find("address", {"class": "c-address"})
    street = address.find("meta", {"itemprop": "streetAddress"})["content"]
    address = address.findAll("div", {"class": "c-AddressRow"})
    city = address[-2].find("span", {"class": "c-address-city"}).text
    try:
        state = address[-2].find("abbr", {"itemprop": "addressRegion"}).text
    except:
        state = "<MISSING>"
    pcode = address[-2].find("span", {"class": "c-address-postal-code"}).text
    ccode = address[-1].text
    lat = soup.find("meta", {"itemprop": "latitude"})["content"]
    longt = soup.find("meta", {"itemprop": "longitude"})["content"]
    phone = soup.find("span", {"itemprop": "telephone"}).text
    title = soup.find("h1", {"class": "Hero-title"}).findAll("span")
    title = title[0].text + " " + title[1].text
    hourlist = (
        soup.find("table", {"class": "c-hours-details"}).find("tbody").findAll("tr")
    )
    hours = ""
    for hour in hourlist:
        hours = hours + " " + hour["content"]
    data = [
        "https://versace.com/",
        link,
        title,
        street,
        city,
        state,
        pcode,
        ccode,
        "<MISSING>",
        phone,
        "<MISSING>",
        lat,
        longt,
        hours,
    ]

    return data


def fetch_data():
    # Your scraper here
    final_data = []
    country_list = [
        "https://boutiques.versace.com/us/en-us/united-states",
        "https://boutiques.versace.com/us/en-us/canada",
        "https://boutiques.versace.com/us/en-us/puerto-rico",
        "https://boutiques.versace.com/us/en-us/united-kingdom",
    ]
    if True:
        for country in country_list:
            r = session.get(country, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            linklist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
                "a", {"class": "Directory-listLink"}
            )
            for link in linklist:
                loc_link = link["href"]
                loc_link = loc_link.split("en-us/")[1]
                loc_link = "https://boutiques.versace.com/us/en-us/" + loc_link
                count = link["data-count"]
                count = int(count.replace(")", "").replace("(", ""))
                r = session.get(loc_link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                if count > 1:
                    loclist = soup.find(
                        "ul", {"class": "Directory-listTeasers Directory-row"}
                    ).findAll("li")
                    for loc in loclist:
                        loc_link = loc.find("a", {"class": "Teaser-link"})["href"]
                        loc_link = loc_link.split("en-us/")[1]
                        loc_link = "https://boutiques.versace.com/us/en-us/" + loc_link
                        r = session.get(loc_link, headers=headers, verify=False)
                        soup = BeautifulSoup(r.text, "html.parser")
                        store_list = get_store_data(soup, loc_link)
                        final_data.append(store_list)
                else:
                    store_list = get_store_data(soup, loc_link)
                    final_data.append(store_list)
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
