# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "3m.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.3m.com",
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


def fetch_data():
    # Your scraper here
    base = "https://www.3m.com"
    search_url = "https://www.3m.com/3M/en_US/plant-locations-us/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath("//ul[@dir]//a")

        for store in store_list:

            page_url = base + "".join(store.xpath("./@href"))

            locator_domain = website
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locations = store_sel.xpath(
                '//div[@itemprop="address"]//div[contains(@class,"content-bd_half")]//p[br]'
            )
            if not locations:
                locations = locations = store_sel.xpath(
                    '//div[@itemprop="address"]//div[contains(@class,"content-bd_half")]'
                )
                if not locations:
                    locations = store_sel.xpath(
                        '//div[@id="contact3MModule"]//div[contains(@class,"content-bd_half")]'
                    )[1:]
            for no, loc in enumerate(locations):
                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in loc.xpath(".//text()")],
                    )
                )

                location_name = "".join(store_sel.xpath("//title/text()")).strip()
                name_txt = loc.xpath("./../p[not(br)]/text()")
                if name_txt:
                    log.info(name_txt)
                    location_name = location_name + f"({name_txt[no].strip()})".replace(
                        "()", ""
                    )

                raw_address = " ".join(store_info).replace("\n", " ")

                formatted_addr = parser.parse_address_usa(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = "US"

                phone_sel = store_sel.xpath(
                    '//div[@id="contact3MModule"]/div[1]//div[contains(@class,"content-bd_half")]//p[br]'
                )
                if phone_sel:

                    if len(phone_sel) == len(locations):
                        phone = (
                            " ".join(phone_sel[no].xpath(".//text()"))
                            .split("Fax:")[0]
                            .split("Administration")[0]
                            .replace("Telephone:", "")
                            .replace("Phone:", "")
                            .replace("Site Director:", "")
                            .strip()
                        )
                    else:
                        phone = (
                            " ".join(phone_sel[0].xpath(".//text()"))
                            .split("Fax:")[0]
                            .split("Administration")[0]
                            .replace("Telephone:", "")
                            .replace("Phone:", "")
                            .replace("Site Director:", "")
                            .strip()
                        )
                else:
                    phone = (
                        "".join(
                            store_sel.xpath(
                                '//div[@id="contact3MModule"]/div[1]//div[contains(@class,"content-bd_half")]//text()'
                            )
                        )
                        .split("Administration")[0]
                        .replace("Telephone:", "")
                        .replace("Phone:", "")
                        .replace("Site Director:", "")
                        .strip()
                    )

                store_number = "<MISSING>"

                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"

                map_link = "".join(store_sel.xpath('//a[contains(@href,"maps")]/@href'))

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
