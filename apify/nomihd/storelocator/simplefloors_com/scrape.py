# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "simplefloors.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()
    country_code = "US"
    return street_address, city, state, zip, country_code


def get_latlng(lat_lng_href):
    if "z/data" in lat_lng_href:
        lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in lat_lng_href:
        lat_lng = lat_lng_href.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://simplefloors.com/pages/copy-of-residential"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath("//table//tr/td")

    for store in store_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(store.xpath("strong/text()")).strip()
        if len(location_name) <= 0:
            location_name = " ".join(store.xpath("p/strong/text()")).strip()
            if len(location_name) <= 0:
                continue
        raw_info = list(filter(str, ([x.strip() for x in store.xpath(".//text()")])))
        address_info = []
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        for index in range(0, len(raw_info)):
            if "Tel:" in raw_info[index]:
                phone = raw_info[index].strip().replace("Tel:", "").strip()

            if "Store Hours" in raw_info[index]:
                hours_of_operation = (
                    "; ".join(raw_info[index + 1 :])
                    .strip()
                    .replace("PM; ", "PM ")
                    .strip()
                )

            if raw_info[index].split(" ")[0].strip().isdigit():
                address_info = raw_info[index : index + 2]

        street_address, city, state, zip, country_code = split_fulladdress(address_info)

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        latitude, longitude = "<MISSING>", "<MISSING>"

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
