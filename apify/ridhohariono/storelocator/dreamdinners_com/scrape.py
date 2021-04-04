import csv
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "dreamdinners.com"
BASE_URL = "https://dreamdinners.com"
LOCATION_URL = "https://dreamdinners.com/main.php?page=locations"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
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
    soup = bs(session.get(url).content, "lxml")
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
                            "div", {"class": "col-lg-6 text-center text-md-left"}
                        )
                        locator_domain = DOMAIN
                        location_name = handle_missing(
                            content_info.find("h3").text
                        ).strip()
                        street_address = handle_missing(
                            content_info.find("p").contents[0].strip()
                        )

                        addr_content = content_info.find("p").contents
                        street_address = addr_content[0].strip()
                        if len(addr_content) == 3:
                            address = handle_missing(
                                content_info.find("p").contents[0].strip()
                                + ","
                                + content_info.find("p").contents[2].strip()
                            )
                        elif len(addr_content) > 3 and len(addr_content) <= 5:
                            address = handle_missing(
                                addr_content[0].strip() + "," + addr_content[4].strip()
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
                        log.info(
                            "Append {} => {}".format(location_name, street_address)
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
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
