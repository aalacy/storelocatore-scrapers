# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import re
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "oddfellowsnyc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.oddfellowsnyc.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def addr_phn(x):
    if (
        "WEATHER" in x.upper()
        or "FOR" in x.upper()
        or "EVENTS@" in x.upper()
        or "HELLO@" in x.upper()
    ):
        return False
    return True


def fetch_data():
    # Your scraper here
    search_url = "https://www.oddfellowsnyc.com/pages/scoop-shops"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath('//div[@class="module-details module-item"]'))
    store_name_list = list(
        search_sel.xpath('//div[contains(@class,"shops-header-")]/h3/text()')
    )
    for no, store in enumerate(store_list):

        page_url = search_url

        locator_domain = website
        location_name = "".join(
            store.xpath('div[@class="module-title"]/h3/text()')
        ).strip()
        if no >= len(store_name_list):
            temp_loc_name = store_name_list[-1].strip()
        else:
            temp_loc_name = store_name_list[no].strip()

        coming_soon = store.xpath(
            'div[@class="shops-contact"]//p[contains(text(),"OPEN")]'
        )
        if coming_soon:
            continue

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        "div[@class='shops-contact']//p[text()]/text()"
                    )
                ],
            )
        )
        store_info = list(filter(addr_phn, store_info))

        for phn_idx, x in enumerate(store_info):
            if bool(re.search("^[0-9-.() ]{1,17}$", x)):
                break
        if re.search("^[0-9-.() ]{1,17}$", store_info[phn_idx]):
            full_address = store_info[:phn_idx]
            phone = store_info[phn_idx].strip()
        else:
            full_address = store_info
            phone = "<MISSING>"

        raw_address = (
            ", ".join(full_address)
            .strip()
            .replace(",,", ",")
            .strip()
            .split(", charleston@")[0]
            .strip()
        )
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if city is None:
            if "Brooklyn," in raw_address:
                city = "Brooklyn"

        state = formatted_addr.state
        if state is None:
            if " Ny" in street_address:
                street_address = street_address.replace(" Ny", "").strip()
                state = "NY"

        zip = formatted_addr.postcode
        country_code = "US"
        if temp_loc_name == "Korea":
            country_code = "Korea"

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        "div[@class='shops-contact']//p[./strong]/strong/text()"
                    )
                ],
            )
        )

        hours_of_operation = "; ".join(hours).replace("; :", ":").strip()

        map_link = "".join(
            store.xpath('div[@class="shops-contact"]//a[contains(@href,"maps")]/@href')
        )

        latitude, longitude = get_latlng(map_link)

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
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
