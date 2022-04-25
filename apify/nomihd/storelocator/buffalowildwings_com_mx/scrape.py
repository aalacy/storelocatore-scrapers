# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "buffalowildwings.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.buffalowildwings.com.mx",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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


def fetch_data():
    # Your scraper here
    search_url = "https://www.buffalowildwings.com.mx/ubicaciones"
    search_res = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(search_res.text)
    stores = stores_sel.xpath('//div[@role="listitem"]')
    for store in stores:
        page_url = search_url
        locator_domain = website

        location_name = "".join(
            store.xpath('div[@class="title-div-sucursal-item"]/h3[1]/text()')
        ).strip()

        street_address = ", ".join(
            store.xpath('.//h4[@class="direccionsucursal"]/text()')
        ).strip()
        city = "".join(
            store.xpath('div[@class="title-div-sucursal-item"]/h3[2]/text()')
        ).strip()
        state = "<MISSING>"
        zip = "<MISSING>"
        country_code = "MX"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = (
            "".join(store.xpath('.//div[@class="telefonowrapper"]//text()'))
            .strip()
            .split("y")[0]
            .strip()
            .split("\n")[0]
            .strip()
        )

        hours = store.xpath('.//div[@class="accordion-content"]//p/text()')
        hours_list = []
        for hour in hours:
            if (
                len(
                    "".join(hour)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )
                > 0
            ):
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        map_link = "".join(
            store.xpath('.//a[@class="google-maps-button w-button"]/@href')
        ).strip()
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
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
