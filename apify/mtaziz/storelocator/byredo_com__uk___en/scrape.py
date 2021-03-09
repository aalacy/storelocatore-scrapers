import csv
from lxml import html
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("byredo_com__uk___en")


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

locator_domain_url = "https://www.byredo.com"
base_url_uk = "https://www.byredo.com/uk_en/find-a-store/united-kingdom"
base_url_us = "https://www.byredo.com/uk_en/find-a-store/united-states"
headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
}

r_uk = session.get(base_url_uk, headers=headers)
r_us = session.get(base_url_us, headers=headers)


def get_data_from_uk():
    tree_uk = html.fromstring(r_uk.text, "lxml")
    tds_uk = tree_uk.xpath('//div[@class="block-cms-text"]/table/tbody')
    items_uk = []
    for idxuk, td_uk in enumerate(tds_uk):
        location_names_uk = td_uk.xpath("//tr/td/h2//descendant::text()")
        address_data_uk = td_uk.xpath(
            "//tr/td//text()[count(preceding-sibling::h2)=$count]",
            count="{}".format(idxuk),
        )
        address_data_uk1 = " ".join(address_data_uk)
        address_data_uk2 = address_data_uk1.split("Map")
        address_data_uk3 = [" ".join(i.split()) for i in address_data_uk2 if i]
        phone_numbers_uk = ["+" + i.split("+")[-1] for i in address_data_uk3 if i]

    for idxuk1, address in enumerate(address_data_uk3):
        address_without_phone_data = address.split("+")
        address_wpd = address_without_phone_data[0].strip()
        address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
        paddress = parse_address_intl(address_wpd1)
        street_address = paddress.street_address_1 or "<MISSING>"
        city = paddress.city or "<MISSING>"
        state = paddress.state or "<MISSING>"
        zip = paddress.postcode or "<MISSING>"
        locator_domain = locator_domain_url
        page_url = "<MISSING>"
        location_name = location_names_uk[idxuk1] or "<MISSING>"
        country_code = "UK"
        store_number = "<MISSING>"
        phone = phone_numbers_uk[idxuk1] or "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = address_wpd.split("Temporarily closed")[1].strip()
        if hoo:
            hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = "Temporarily closed"
        row_uk = [
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
        items_uk.append(row_uk)
    return items_uk


def get_data_from_us():
    locator_domain = "https://www.byredo.com"
    tree_us = html.fromstring(r_us.text, "lxml")
    tds_us = tree_us.xpath('//div[@class="block-cms-text"]/table/tbody')
    items_us = []
    for idxus, td_us in enumerate(tds_us):
        location_names_us = td_us.xpath("//tr/td/h2//descendant::text()")
        address_data_us = td_us.xpath(
            "//tr/td//text()[count(preceding-sibling::h2)=$count]",
            count="{}".format(idxus),
        )
        address_data_us1 = " ".join(address_data_us)
        address_data_us2 = address_data_us1.split("Map")
        address_data_us3 = [" ".join(i.split()) for i in address_data_us2 if i]
        phone_numbers_us = ["+" + i.split("+")[-1] for i in address_data_us3 if i]

    for idxus1, address in enumerate(address_data_us3):
        locator_domain = locator_domain_url
        page_url = "<MISSING>"
        location_name = location_names_us[idxus1] or "<MISSING>"
        paddress = parse_address_intl(address)
        street_address = paddress.street_address_1 or "<MISSING>"
        city = paddress.city or "<MISSING>"
        state = paddress.state or "<MISSING>"
        zip = paddress.postcode or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = phone_numbers_us[idxus1] or "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        row_us = [
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
        items_us.append(row_us)
    return items_us


def fetch_data():
    uk_data = get_data_from_uk()
    us_data = get_data_from_us()
    items = []
    items.extend(uk_data)
    items.extend(us_data)
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
