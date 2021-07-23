# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape import sgpostal as parser


website = "lasikmd.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.lasikmd.com",
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
    base = "https://www.lasikmd.com"
    search_url = "https://www.lasikmd.com/clinics"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath("//p/a/@href"))

    for store in store_list:

        page_url = base + store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = store_sel.xpath("//h1/text()")[0].strip()

        full_address = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//p[ contains(.//text(),"address")]//text()'
                    )
                ],
            )
        )

        raw_address = " ".join(full_address[1:])

        formatted_addr = parser.parse_address_intl(raw_address)

        street_address = (
            store_res.text.split('"streetAddress":')[1]
            .split("},")[0]
            .strip()
            .strip('" ')
            .strip()
            .replace("HSBC Tower", "")
            .replace("Edmonton City Centre Mall", "")
            .replace("Princeton Tower", "")
            .replace("Complexe Jules Dallaire (Tour 2)", "")
            .replace("Mumford Professional Centre", "")
            .replace("1 First Canadian Place,", "")
            .replace("Frederick Tower", "")
            .replace(",Minto Place Atrium", "")
            .replace("MD Level", "")
            .strip()
        )
        city = (
            store_res.text.split('"addressLocality":')[1]
            .split(",")[0]
            .strip('" ')
            .strip()
            .split("(")[0]
            .strip()
        )

        state = (
            store_res.text.split('"addressRegion":')[1]
            .split(",")[0]
            .strip('" ')
            .strip()
        )

        zip = formatted_addr.postcode

        if us.states.lookup(state):
            country_code = "US"
        else:
            country_code = "CA"

        store_number = "<MISSING>"
        phone = (
            " ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//p[ contains(.//text(),"all us")]//text()'
                            )
                        ],
                    )
                )
            )
            .upper()
            .split(" TOLL-FREE")[0]
            .replace("CALL US", "")
            .replace("DOCTORS (", "")
            .replace(")", "")
            .strip(": ")
            .strip()
        )

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//*[ contains(.//text(),"opening hours")]//p//text()'
                    )
                ],
            )
        )

        hours_of_operation = " ".join(hours).replace("day :", "day:")

        latitude = store_res.text.split('data-lat="')[1].split('"')[0].strip()
        longitude = store_res.text.split('data-lon="')[1].split('"')[0].strip()

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
