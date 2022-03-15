# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "megafurnituretx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    # Your scraper here
    search_url = "https://www.google.com/maps/d/u/0/embed?mid=1MVFJyXQLsGuiwaJQUWFfDbb_GA44WoyZ&ll=29.958442008579446%2C-98.1693116&z=9"
    stores_req = session.get(search_url)
    raw_info = stores_req.text.replace('\\"', '"').strip()
    names = raw_info.split('["Name",["')
    street_addresses = raw_info.split('["Street",["')
    cities = raw_info.split('["City",["')
    states = raw_info.split('["State",["')
    zipcodes = raw_info.split('["Zipcode",["')
    phone_list = raw_info.split('["Telephone",["')

    for index in range(1, len(names)):
        page_url = "https://megafurnituretx.com/pages/find-our-locations"
        locator_domain = website

        location_name = "".join(names[index].split('"')[0]).strip()

        street_address = "".join(street_addresses[index].split('"')[0]).strip()
        city = "".join(cities[index].split('"')[0]).strip()
        state = "".join(states[index].split('"')[0]).strip()
        zip = "".join(zipcodes[index].split('"')[0]).strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(phone_list[index].split('"')[0]).strip()
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latlng = "".join(
            names[index - 1].rsplit("[[[", 1)[1].strip().split("]")[0]
        ).strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[1].strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
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
