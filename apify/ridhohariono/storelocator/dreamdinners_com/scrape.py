import csv
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests


DOMAIN = "dreamdinners.com"
BASE_URL = "https://dreamdinners.com"
LOCATION_URL = "https://dreamdinners.com/main.php?page=locations"
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
    soup = bs(session.get(url).content, "html.parser")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    soup = pull_content(LOCATION_URL)
    locations = []
    for x in soup.find_all("div", {"class": "row"}):
        links = x.find_all(
            "a", {"class": "text-uppercase text-gray-dark location_state"}
        )
        if links:
            for link in links:
                store_url_list = BASE_URL + link["href"]
                store_content = pull_content(store_url_list)
                store_list = store_content.find(
                    "div", {"id": "store_search_results"}
                ).find_all("div", {"class": "location"})
                for row in store_list:
                    # check coming soon page
                    coming_soon = row.find("span", string="Coming Soon!")
                    if coming_soon is None:
                        individual_store_link = row.find(
                            "a", string="Store Info & Calendar"
                        )

                        page_url = BASE_URL + individual_store_link["href"]
                        store_page_content = pull_content(page_url)

                        section = store_page_content.find_all("section")[1]
                        content_info = section.find("div", {"class": "container"}).find(
                            "div", {"class": "row mt-5"}
                        )
                        locator_domain = DOMAIN
                        location_name = handle_missing(
                            content_info.find("h3").text
                        ).strip()
                        street_address = handle_missing(
                            content_info.find("p").contents[0].strip()
                        )
                        address = (
                            content_info.find("p")
                            .text.replace("\n", "")
                            .rstrip()
                            .strip()
                        )
                        parse_addr = usaddress.tag(address)
                        city = handle_missing(parse_addr[0]["PlaceName"])
                        state = handle_missing(parse_addr[0]["StateName"])
                        zip_code = handle_missing(parse_addr[0]["ZipCode"])
                        country_code = "US"
                        store_number = page_url.split("=")[2]
                        phone = handle_missing(
                            content_info.find(
                                "div", {"class": "d-none d-md-block"}
                            ).text
                        )
                        location_type = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = "<MISSING>"
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