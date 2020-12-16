import csv
from lxml import etree
from requests_toolbelt import MultipartEncoder
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "linex.com"
    start_url = "https://linex.com/find-a-location"
    response = session.get("https://linex.com/find-a-location")
    dom = etree.HTML(response.text)
    token = dom.xpath('//meta[@name="csrf-token"]/@content')[0]

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        frm = {"_token": token, "country": "US", "location": code, "country_intl": ""}
        hdr = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        me = MultipartEncoder(fields=frm)
        me_boundary = me.boundary[2:]
        me_body = me.to_string()
        hdr["Content-Type"] = (
            "multipart/form-data; charset=utf-8; boundary=" + me_boundary
        )
        code_response = session.post(start_url, data=me_body, headers=hdr)
        code_dom = etree.HTML(code_response.text)
        print(code, len(code_dom.xpath('//div[@class="find-result "]')))
        all_locations += code_dom.xpath('//div[@class="find-result "]')
        token = dom.xpath('//meta[@name="csrf-token"]/@content')[0]

    for loc_html in all_locations:
        store_url = loc_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = loc_html.xpath("@data-title")
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_html.xpath(".//address//text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        add_check = ["Visit us at our New Location!", "Get Directions"]
        address_raw = [elem.strip() for elem in address_raw if elem not in add_check]
        if len(address_raw) > 1:
            check_elems = [
                "Ste ",
                "(",
                "Suit",
                "Unit",
                "Building",
                "#",
                "STE",
                "Hangar",
                "Ste.",
                "Ste-",
            ]
            for elem in check_elems:
                if elem in address_raw[1]:
                    address_raw = [" ".join(address_raw[:2])] + address_raw[2:]
                    break
        if len(address_raw) > 1:
            if len(address_raw[1].split()) == 6:
                address_raw = address_raw.pop(1)

        if len(address_raw[0]) == 1:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip_code = "<MISSING>"
        else:
            if len(address_raw) > 1:
                street_address = address_raw[0]
                city = address_raw[1].split(",")[0].split()[:-1]
                if not city:
                    city = [
                        street_address,
                    ]
                    street_address = "<MISSING>"
                city = " ".join(city) if city else "<MISSING>"
                if not address_raw[1].split(",")[0]:
                    state = "<MISSING>"
                else:
                    state = address_raw[1].split(",")[0].split()[-1]
                state = state if state else "<MISSING>"
                zip_code = address_raw[-1].split(",")[-1]
                zip_code = zip_code.strip() if zip_code else "<MISSING>"
            else:
                street_address = "<MISSING>"
                city = address_raw[0].split(",")[0].split()[0]
                state = address_raw[0].split(",")[0].split()[-1]
                zip_code = address_raw[0].split(",")[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_html.xpath(
            './/h5[contains(text(), "Contact:")]/following-sibling::p/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_html.xpath("@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_html.xpath("@data-lon")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_html.xpath('.//p[@class="hours"]/text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = [
            DOMAIN,
            store_url,
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
