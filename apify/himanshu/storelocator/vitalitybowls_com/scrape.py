import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser
import lxml.html

logger = SgLogSetup().get_logger("vitalitybowls_com")
session = SgRequests()


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
    base_url = "https://vitalitybowls.com"
    r = session.get("https://vitalitybowls.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    location_links = []
    for states in soup.find_all("div", {"class": "et_pb_text_inner"}):
        for link in states.find_all("a"):
            loc_name = link.text
            if "Coming Soon" in loc_name:
                continue
            page_url = link["href"]
            if page_url in location_links:
                continue
            location_links.append(page_url)
            logger.info(page_url)
            location_request = session.get(page_url, headers=headers)
            location_soup = BeautifulSoup(location_request.text, "lxml")
            location_sel = lxml.html.fromstring(location_request.text)

            name = location_soup.find("h2", {"class": "et_pb_slide_title"}).text
            address = location_sel.xpath(
                '//div[@class="et_pb_column et_pb_column_1_4 et_pb_column_inner et_pb_column_inner_0"]//div[@class="et_pb_text_inner"]//text()'
            )
            add_list = []
            for add in address:
                if (
                    len("".join(add).strip()) > 0
                    and "STORE INFO" not in "".join(add).strip()
                ):
                    if "\n" in "".join(add).strip():
                        temp_add_list = "".join(add).strip().split("\n")
                        for temp in temp_add_list:
                            if len("".join(temp).strip()) > 0:
                                add_list.append("".join(temp).strip())
                    else:
                        add_list.append("".join(add).strip())

            raw_address = ", ".join(add_list)
            try:
                raw_address = raw_address.split("Phone")[0].strip()
            except:
                pass

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zipp = formatted_addr.postcode
            phone = "".join(
                location_sel.xpath(
                    '//div[@class="et_pb_text_inner"]//a[contains(@href,"tel:")]/text()'
                )
            ).strip()
            if page_url == "https://vitalitybowls.com/locations/colorado-springs/":
                street_address = "13492 Bass Pro Drive  Suite 120"
                city = "Colorado  Springs"
                state = "CO"
                zipp = "80921"

            if phone == "":
                info_section = location_sel.xpath('//div[@class="et_pb_text_inner"]/p')
                for info in info_section:
                    if "phone" in "".join(info.xpath("text()")).strip().lower():
                        phone = (
                            "".join(info.xpath(".//text()"))
                            .strip()
                            .lower()
                            .replace("phone", "")
                            .replace(":", "")
                            .strip()
                        )

            try:
                hours = (
                    " ".join(
                        list(
                            location_soup.find(
                                "h2", text="HOURS"
                            ).parent.stripped_strings
                        )
                    )
                    .replace("HOURS", "")
                    .strip()
                )
            except:
                hours = (
                    " ".join(
                        list(
                            location_soup.find(
                                "h2", text="Hours"
                            ).parent.stripped_strings
                        )
                    )
                    .replace("Hours", "")
                    .strip()
                )
            geo_location = location_soup.find("iframe")["data-src"]
            store = []
            store.append("https://vitalitybowls.com")
            store.append(loc_name)
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            if "!3d" in geo_location and "!2d" in geo_location:
                store.append(geo_location.split("!3d")[1].split("!")[0])
                store.append(geo_location.split("!2d")[1].split("!")[0])
            else:
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
            store.append(
                hours.replace("Re-opening April 28th!", "")
                .replace("\n", "")
                .replace("\r", "")
                .replace("\t", "")
                if hours.strip()
                else "<MISSING>"
            )
            store.append(page_url)
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
