# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "therealreal.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.therealreal.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.therealreal.com/about"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//select[@aria-labelledby="visit-us"]/option[position()>1]'
        )
        for store in stores:
            if "http" not in "".join(store.xpath("@value")).strip():
                page_url = (
                    "https://www.therealreal.com"
                    + "".join(store.xpath("@value")).strip()
                )
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                location_name = "".join(store.xpath("text()")).strip()
                location_type = "<MISSING>"
                locator_domain = website
                phone = ""
                hours_of_operation = ""

                raw_info = store_sel.xpath(
                    '//div[@class="formatted-content "]//div[@class="structured-text-line__paragraph"]//text()'
                )
                if len(raw_info) <= 0:
                    raw_info = store_sel.xpath(
                        '//h6/a[contains(@href,"google")]//text()'
                    )
                    if len(raw_info) <= 0:
                        raw_info = [
                            store_req.text.split('"type":"heading6","text":"')[1]
                            .strip()
                            .split('",')[0]
                            .strip()
                        ]
                    phone = store_sel.xpath(
                        '//div[.//h6[contains(text(),"CONTACT")]]//a[contains(@href,"tel:")]/text()'
                    )
                    if len(phone) > 0:
                        phone = phone[0]
                    else:
                        phone = (
                            store_req.text.split('"link_type":"Web","url":"tel:')[1]
                            .strip()
                            .split('"}')[0]
                            .strip()
                            .replace("+1", "")
                            .strip()
                        )
                    hours_of_operation = "".join(
                        store_sel.xpath('//p[contains(text(),"Monday")]/text()')
                    ).strip()
                else:
                    phone = raw_info[-2].strip()
                    if "@" in phone:
                        phone = raw_info[-3].strip()
                    if "(" not in phone:
                        phone = "(" + phone

                    hours_list = []
                    hours = store_sel.xpath(
                        "//div[@class='location-section__store-hours']"
                    )
                    if len(hours) > 0:
                        hours = hours[0].xpath(".//text()")
                        for hour in hours:
                            if len("".join(hour).strip()) > 0:
                                hours_list.append("".join(hour).strip())

                    hours_of_operation = "; ".join(hours_list).strip()

                if len(hours_of_operation) <= 0:
                    hours_of_operation = (
                        store_req.text.split('"type":"paragraph","text":"')[1]
                        .strip()
                        .split('",')[0]
                        .strip()
                    )

                if "teaming up to bring you" in raw_info[0].lower():
                    raw_info = store_sel.xpath(
                        '//div[@class="formatted-content "]//div[@class="structured-text-line__paragraph"][./a[contains(@href,"google")]]//text()'
                    )

                raw_address = raw_info[0].strip()
                formatted_addr = parser.parse_address_usa(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if city == "Ny":
                    city = "New York"

                state = formatted_addr.state
                zipp = formatted_addr.postcode

                country_code = "US"
                store_number = "<MISSING>"

                map_link = "".join(
                    store_sel.xpath('//a[@class="location-section__address"]/@href')
                ).strip()
                if len(map_link) <= 0:
                    map_link = (
                        store_req.text.split('"link_type":"Web","url":"')[1]
                        .strip()
                        .split('"}')[0]
                        .strip()
                    )

                latitude = ""
                longitude = ""
                if "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.replace(
                        "Find The RealReal on the 2nd Floor;", ""
                    ).strip(),
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
