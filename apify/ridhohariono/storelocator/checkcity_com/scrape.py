import csv
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

DOMAIN = "checkcity.com"
BASE_URL = "https://www.checkcity.com/"
LOCATION_URL = "https://www.checkcity.com/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
session = SgRequests()


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


def pull_content(url):
    soup = bs(session.get(url, headers=HEADERS).content, "html.parser")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_link(link_url, tag, div_class, tag_link, tag_p):
    soup = pull_content(link_url)
    links = []
    table = soup.find(tag, div_class)
    trs = table.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        for td in tds:
            if tag_p:
                link_lists = td.find_all(tag_link)
                for link in link_lists:
                    links.append(link["href"])
            else:
                link = td.find(tag_link)
                if link:
                    links.append(link["href"])
    return links


def fetch_store_urls():
    store_urls = []
    state_links = fetch_link(
        LOCATION_URL, "table", {"class": "servicesTable"}, "a", False
    )
    for state_link in state_links:
        store_links = fetch_link(
            state_link, "table", {"class": "locationlink"}, "a", True
        )
        for store_link in store_links:
            if state_link not in store_link:
                store_link = state_link + store_link
            store_urls.append(store_link)

    return store_urls


def fetch_data():
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        content = (
            soup.find("div", {"class", "span8"})
            .find("div")
            .find("table")
            .find_all("tr")
        )
        closed_store = content[0].find_all(
            "td", string=" This Location is Permanently Closed "
        )
        if not closed_store:
            address = content[0].find_all("td")[1].text
            parse_addr = usaddress.tag(address)
            locator_domain = DOMAIN
            location_name = handle_missing(
                soup.find("div", {"class", "span8"}).find("div").find("h1").text
            )
            street_address = handle_missing(address.split(",")[0])
            city = handle_missing(parse_addr[0]["PlaceName"])
            state = handle_missing(parse_addr[0]["StateName"])
            zip_code = handle_missing(parse_addr[0]["ZipCode"])
            country_code = "US"
            store_number = "<MISSING>"
            phone = handle_missing(content[2].find_all("td")[1].text)
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_content = content[1].find_all("td")[1]
            hours_of_operation = handle_missing(
                hours_content.get_text(strip=True, separator=",")
            )
            locations.append(
                [
                    locator_domain,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )
    return locations


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
