from sgrequests import SgRequests
from sglogging import SgLogSetup
from lxml import html
import csv
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("chronictacos_com")


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


session = SgRequests()
locator_domain_url = "https://www.chronictacos.com"


def get_urls_from_page_src():
    us_locations_url = "https://www.chronictacos.com/us-locations"
    ca_locations_url = "https://www.chronictacos.com/canada-locations"
    list_of_countries_urls = [us_locations_url, ca_locations_url]
    all_location_urls = []
    for url in list_of_countries_urls:
        if "us" in url:
            us_r = session.get(url)
            us_tree = html.fromstring(us_r.text)
            us_location_detail_url = us_tree.xpath(
                '//h3[contains(@class, "l-location")]/a/@href'
            )
            for url_location in us_location_detail_url:
                all_location_urls.append(url_location)
        elif "canada" in url:
            ca_r = session.get(url)
            ca_tree = html.fromstring(ca_r.text)
            ca_location_detail_url = ca_tree.xpath(
                '//section[contains(@class, "menu-section")]//a/@href'
            )
            for url_location in ca_location_detail_url:
                full_url = locator_domain_url + "/" + url_location
                all_location_urls.append(full_url)
        else:
            all_location_urls = ""
    return all_location_urls


def get_data_from_page_src():
    page_urls_from_page_src = get_urls_from_page_src()
    items_psrc = []
    for page_url_from_page_src in page_urls_from_page_src:
        r_location = session.get(page_url_from_page_src)
        tree_obj = html.fromstring(r_location.text)
        json_raw_data = tree_obj.xpath('//script[@type="application/ld+json"]/text()')
        json_raw_data = json_raw_data[1]
        json_data = json.loads(json_raw_data, strict=False)
        locator_domain = locator_domain_url
        page_url = json_data["url"]
        location_name = json_data["name"]
        street_address_data = json_data["address"]["streetAddress"].strip()
        if street_address_data:
            street_address = street_address_data
        else:
            street_address = "<MISSING>"

        city_data = json_data["address"]["addressLocality"].strip()
        if city_data:
            city = city_data
        else:
            city = "<MISSING>"
        state_data = json_data["address"]["addressRegion"].strip()

        if state_data:
            state = state_data
        else:
            state = "<MISSING>"

        country_code_data = json_data["address"]["addressCountry"]
        if country_code_data:
            country_code = country_code_data.strip()
        else:
            country_code = "<MISSING>"

        zip_data = json_data["address"]["postalCode"].strip()
        if zip_data:
            zip = zip_data
        else:
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone_data = json_data["telephone"]
        if phone_data:
            phone = phone_data
        else:
            phone = "<MISSING>"

        location_type = json_data["@type"]
        latitude = json_data["geo"]["latitude"]
        longitude = json_data["geo"]["longitude"]

        hoo = json_data["openingHours"]
        hoo1 = [i.strip() for i in hoo.split("\n")]
        hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
        hoo3 = "; ".join(hoo2)
        if hoo3:
            hoo1 = [i.strip() for i in hoo.split("\n")]
            hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
            hoo3 = "; ".join(hoo2)
            hours_of_operation = hoo3
        else:
            hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items_psrc.append(row)
    return items_psrc


def get_urls_from_api_res():
    payload = {
        "latitude": 33.9127807,
        "longitude": -118.3520389,
        "range": 10000,
        "city_zip": 90250,
        "city_state": "",
        "search_by_state": "",
    }
    url_api_endpoint = "https://www.chronictacos.com/locations/storelist"
    json_data_api = session.post(url_api_endpoint, data=payload).json()
    page_urls = []
    for json_data in json_data_api["data"][0:51]:
        page_url = json_data["catering_url"].strip()
        page_urls.append(page_url)
    return page_urls


def fetch_data():
    # Your scraper here
    page_urls_from_api_res = get_urls_from_api_res()
    supporting_data = get_data_from_page_src()
    items = []
    for page_url_from_api_res in page_urls_from_api_res:
        r_location = session.get(page_url_from_api_res)
        tree_obj = html.fromstring(r_location.text)
        json_raw_data = tree_obj.xpath('//script[@type="application/ld+json"]/text()')
        json_raw_data = json_raw_data[1]
        json_data = json.loads(json_raw_data, strict=False)
        locator_domain = locator_domain_url
        page_url = json_data["url"]
        location_name = json_data["name"]

        street_address_data = json_data["address"]["streetAddress"].strip()

        if street_address_data:
            street_address = street_address_data
        else:
            street_address = "<MISSING>"

        city_data = json_data["address"]["addressLocality"].strip()
        if city_data:
            city = city_data
        else:
            city = "<MISSING>"

        state_data = json_data["address"]["addressRegion"].strip()
        if state_data:
            state = state_data
        else:
            state = "<MISSING>"

        country_code_data = json_data["address"]["addressCountry"]
        if country_code_data:
            country_code = country_code_data.strip()
        else:
            country_code = "<MISSING>"

        zip_data = json_data["address"]["postalCode"].strip()
        if zip_data:
            zip = zip_data
        else:
            zip = "<MISSING>"
        if country_code == "CA":
            raw_address = "{} {} {} {}".format(
                street_address, city, state, zip
            ).replace("<MISSING>", "")
            parsed_raw_address = parse_address_intl(raw_address)
            street_address = parsed_raw_address.street_address_1 or "<MISSING>"
            city = parsed_raw_address.city or "<MISSING>"
            state = parsed_raw_address.state or "<MISSING>"
            zip = parsed_raw_address.postcode or "<MISSING>"

        else:
            pass

        store_number = "<MISSING>"
        phone_data = json_data["telephone"]
        if phone_data:
            phone = phone_data
        else:
            phone = "<MISSING>"
        location_type = json_data["@type"]
        latitude = json_data["geo"]["latitude"].strip() or "<MISSING>"
        longitude = json_data["geo"]["longitude"].strip() or "<MISSING>"

        hoo = json_data["openingHours"]
        hoo1 = [i.strip() for i in hoo.split("\n")]
        hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
        hoo3 = "; ".join(hoo2)
        if hoo3:
            hoo1 = [i.strip() for i in hoo.split("\n")]
            hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
            hoo3 = "; ".join(hoo2)
            hours_of_operation = hoo3
        else:
            hours_of_operation = "<MISSING>"

        if (
            "<MISSING>" in hours_of_operation
            and "<MISSING>" in street_address
            and "<MISSING>" in phone
            and "<MISSING>" not in longitude
            and "<MISSING>" not in latitude
        ):
            for idx, sd in enumerate(supporting_data):
                if city in sd and state in sd:
                    url_coming_soon = supporting_data[idx][1]
                    r_cs = session.get(url_coming_soon)
                    tree_cs = html.fromstring(r_cs.text)
                    raw_data_cs = tree_cs.xpath("//body//text()")
                    raw_data_cs = " ".join("".join(raw_data_cs).strip().split()).lower()
                    if "coming soon" in raw_data_cs:
                        hours_of_operation = "Coming Soon"
                    else:
                        hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items.append(row)
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
