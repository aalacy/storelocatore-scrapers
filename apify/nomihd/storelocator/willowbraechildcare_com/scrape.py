# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser


website = "willowbraechildcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "willowbraechildcare.com",
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


def fetch_data():
    # Your scraper here
    base = "https://willowbraechildcare.com"
    search_url = "https://willowbraechildcare.com/our-academies/browse-list-view"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        search_sel.xpath(
            '//div[@itemprop]//p[./a]//a[@href and not(contains(@href,"tel"))]/@href'
        )
    )

    for store in store_list:

        page_url = base + store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = (
            "   ".join(store_sel.xpath("//h2/text()")).split("   ")[0].strip()
        )

        raw_address = (
            store_res.text.split("mapCenterAddress")[1]
            .split('",mapCenter')[0]
            .strip()
            .strip('": ')
            .strip()
        )
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        if street_address is not None:
            street_address = (
                street_address.replace("Way Glen Arbour", "Way")
                .strip()
                .replace("Burlington Power", "")
                .strip()
            )
        city = formatted_addr.city
        state = location_name.split(",")[-1].strip()
        zip = formatted_addr.postcode

        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            " | ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//*[contains(@class,"ph-details")]//text()'
                            )
                        ],
                    )
                )
            )
            .split("|")[0]
            .strip()
            .replace("(KIDZ)", "")
            .strip()
        )

        location_type = "<MISSING>"

        hours = store_sel.xpath('//*[@class="table-hours"]//tr')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            if len(day) > 0 and len(time) > 0:
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list)

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
