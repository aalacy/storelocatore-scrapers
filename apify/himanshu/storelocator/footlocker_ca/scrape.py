import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("footlocker_ca")

session = SgRequests()


def parser(location_soup, page_url):
    street_address = " ".join(
        list(
            location_soup.find("span", {"class": "c-address-street-1"}).stripped_strings
        )
    )
    if location_soup.find("span", {"class": "c-address-street-2"}) is not None:
        street_address = (
            street_address
            + " "
            + " ".join(
                list(
                    location_soup.find(
                        "span", {"class": "c-address-street-2"}
                    ).stripped_strings
                )
            )
        )
    name = (
        location_soup.find("div", {"class": "LocationName-brand"}).text.strip()
        + " "
        + location_soup.find("span", {"class": "LocationName-geo"}).text.strip()
    )
    if location_soup.find("span", {"class": "c-address-city"}):
        city = location_soup.find("span", {"class": "c-address-city"}).text
    else:
        city = "<MISSING>"
    if location_soup.find("abbr", {"class": "c-address-state"}):
        state = location_soup.find("abbr", {"class": "c-address-state"}).text
    else:
        state = "<MISSING>"
    if location_soup.find("span", {"class": "c-address-postal-code"}):
        store_zip = location_soup.find("span", {"class": "c-address-postal-code"}).text
    else:
        store_zip = "<MISSING>"
    if location_soup.find("div", {"itemprop": "telephone"}):
        phone = location_soup.find("div", {"itemprop": "telephone"}).text
    else:
        phone = "<MISSING>"
    hours = " ".join(
        list(location_soup.find("table", {"class": "c-hours-details"}).stripped_strings)
    )
    lat = location_soup.find("meta", {"itemprop": "latitude"})["content"]
    lng = location_soup.find("meta", {"itemprop": "longitude"})["content"]
    store = []
    store.append("https://www.footlocker.ca")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    if len(store[-1]) == 6:
        store[-1] = store[-1][:3] + " " + store[-1][3:]
    store.append("CA")
    store.append("<MISSING>")
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours.replace("Day of the Week Hours ", ""))
    store.append(page_url)
    return store


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    r = session.get("https://stores.footlocker.ca/index.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for states in soup.find_all("a", {"class": "Directory-listLink"}):
        if states["href"].count("/") == 3:
            page_url = "https://stores.footlocker.ca/" + states["href"].replace(
                "../", ""
            )
            logger.info(page_url)
            location_request = session.get(
                "https://stores.footlocker.ca/" + states["href"].replace("../", ""),
                headers=headers,
            )
            location_soup = BeautifulSoup(location_request.text, "lxml")
            store_data = parser(location_soup, page_url)
            yield store_data
        else:
            state_request = session.get(
                "https://stores.footlocker.ca/" + states["href"], headers=headers
            )
            state_soup = BeautifulSoup(state_request.text, "lxml")
            for city in state_soup.find_all("a", {"class": "Directory-listLink"}):
                if city["href"].count("/") == 4:
                    page_url = "https://stores.footlocker.ca/" + city["href"].replace(
                        "../", ""
                    )
                    logger.info(page_url)
                    location_request = session.get(
                        "https://stores.footlocker.ca/"
                        + city["href"].replace("../", ""),
                        headers=headers,
                    )
                    location_soup = BeautifulSoup(location_request.text, "lxml")
                    store_data = parser(location_soup, page_url)
                    yield store_data
                else:
                    city_request = session.get(
                        "https://stores.footlocker.ca/"
                        + city["href"].replace("../", "")
                    )
                    city_soup = BeautifulSoup(city_request.text, "lxml")
                    for location in city_soup.find_all(
                        "a", {"class": "Teaser-titleLink"}
                    ):
                        page_url = "https://stores.footlocker.ca/" + location[
                            "href"
                        ].replace("../", "")
                        logger.info(page_url)
                        location_request = session.get(
                            "https://stores.footlocker.ca/"
                            + location["href"].replace("../", ""),
                            headers=headers,
                        )
                        location_soup = BeautifulSoup(location_request.text, "lxml")
                        store_data = parser(location_soup, page_url)
                        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
