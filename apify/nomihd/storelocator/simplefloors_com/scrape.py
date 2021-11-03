# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

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

    search_url = "https://www.simplefloors.com/page/store-locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath("//table//table//tr")

    for store in store_list:

        page_url = search_url
        locator_domain = website

        location_name = " ".join(
            list(
                filter(
                    str,
                    store.xpath('.//a[not(contains(@href,"maps"))]//text()'),
                )
            )
        ).strip()

        address_info = list(
            filter(
                str,
                store.xpath('.//a[not(contains(@href,"maps"))]/../text()'),
            )
        )

        address_info = list(filter(str, ([x.strip() for x in address_info])))
        street_address, city, state, zip, country_code = split_fulladdress(address_info)

        store_number = "<MISSING>"

        phone = "".join(store.xpath("./td[2]/div[1]//text()")).strip()

        location_type = "<MISSING>"

        hours_info = list(filter(str, store.xpath("./td[2]/div[2]//text()")))
        hours_info = list(filter(str, [x.strip() for x in hours_info]))

        hours_of_operation = "; ".join(hours_info)

        lat_lng_href = "".join(store.xpath('.//a[contains(@href,"maps")]/@href'))
        latitude, longitude = get_latlng(lat_lng_href)

        raw_address = "<MISSING>"
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
            raw_address=raw_address,
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
