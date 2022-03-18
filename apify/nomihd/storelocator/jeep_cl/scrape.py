# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "jeep.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
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
    elif "&q=" in map_link:
        latitude = map_link.split("&q=")[1].split(",")[0].strip()
        longitude = map_link.split("&q=")[1].split(",")[1].strip()
    elif "?q=" in map_link:
        latitude = map_link.split("?q=")[1].split(",")[0].strip()
        longitude = map_link.split("?q=")[1].split(",")[1].strip().split("&")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    urls_list = [
        "https://www.jeep.cl/concesionarios/",
        "https://www.jeep.com.co/concesionarios/",
        "https://www.jeep.cr/concesionarios/",
        "https://www.jeep.com.pa/concesionarios/",
        "https://www.jeep.com.py/concesionarios/",
        "https://www.jeep.pe/concesionarios/",
        "https://www.jeep.com.uy/concesionarios/",
        "https://www.jeep.bo/concesionarios/",
    ]
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        for search_url in urls_list:
            log.info(search_url)
            search_res = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(search_res.text)
            cities_dict = {}
            cities = stores_sel.xpath(
                '//select[@class="b-concesionario2"]/option[position()>1]'
            )
            for city in cities:
                cities_dict["".join(city.xpath("@value")).strip()] = "".join(
                    city.xpath("@data-region")
                ).strip()
            stores = stores_sel.xpath("//div[@data-region]")
            for store in stores:
                if len("".join(store.xpath("@data-region")).strip()) <= 0:
                    continue
                page_url = "<MISSING>"
                locator_domain = website
                location_name = "".join(store.xpath("h2/text()")).strip()

                temp_address = store.xpath("div[1]/div[@class='marker']//text()")
                add_list = []
                for temp in temp_address:
                    if len("".join(temp).strip()) > 0:
                        add_list.append("".join(temp).strip())

                raw_address = ", ".join(add_list).strip()
                phone = "".join(
                    store.xpath('div[1]/div[@class="phone"]//text()')
                ).strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = "".join(store.xpath("@data-region")).strip()
                state = "<MISSING>"
                if city in cities_dict:
                    state = cities_dict[city]
                zip = formatted_addr.postcode

                country_code = (
                    search_url.split("/concesionarios")[0]
                    .strip()
                    .split(".")[-1]
                    .strip()
                )

                store_number = "<MISSING>"
                location_type = "<MISSING>"

                hours_of_operation = "; ".join(
                    store.xpath('div[1]/div[@class="clock"]/text()')
                ).strip()
                map_link = "".join(
                    store.xpath('div[1]/div[@class="marker"]/a/@href')
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
                    phone=phone.split("/")[-1].strip(),
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
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
