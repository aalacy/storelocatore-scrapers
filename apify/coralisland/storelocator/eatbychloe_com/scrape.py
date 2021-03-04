from sgrequests import SgRequests
import lxml.html
from sgscrape import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

base_url = "https://eatbychloe.com"
log = sglog.SgLogSetup().get_logger(logger_name="eatbychloe_com")


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip().replace("\n", "").replace("\t", "")


def get_value(item):
    if item == None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def fetch_data():
    output_list = []
    url = "https://eatbychloe.com/locations/"
    session = SgRequests()
    request = session.get(url)
    response = lxml.html.fromstring(request.text)
    store_list = response.xpath('//div[@class="marker"]')

    for store in store_list:
        location_name = get_value(store.xpath(".//h4/text()"))
        if "COMING SOON!" in location_name:
            continue

        raw_address = ", ".join(eliminate_space(store.xpath(".//p/text()"))).strip()
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = (
            "".join(store.xpath("@data-region"))
            .strip()
            .replace("-locations", "")
            .strip()
        )
        if country_code == "europe":
            country_code = "GB"

        store_number = "<MISSING>"
        phone = "".join(store.xpath('.//p[@class="phone-number"]/text()')).strip()
        location_type = "Classic Taste, Plant-Based | Vegan Restaurant"
        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()
        hours_of_operation = get_value(
            store.xpath('.//div[@class="hours-item"]//text()')
        )

        yield SgRecord(
            locator_domain=base_url,
            page_url=url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
