# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "craneww.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "craneww.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    # Your scraper here

    search_url = "http://www.craneww.com/locations/"
    with SgRequests() as session:
        countries_req = session.get(search_url, headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath('//a[@class="menu__link justify_between"]')
        for cont in countries:
            country_code = "".join(cont.xpath("text()")).strip()
            stores_url = (
                "https://craneww.com/locations/" + "".join(cont.xpath("@href")).strip()
            )
            log.info(stores_url)
            stores_req = session.get(stores_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//div[@class="container"]/div[@class="grid"]/div'
            )
            for store in stores:
                page_url = (
                    stores_url
                    + "".join(
                        store.xpath(".//div[@class='card__body spacing']/h3/a/@href")
                    ).strip()
                )
                location_name = "".join(
                    store.xpath(".//div[@class='card__body spacing']/h3/a/text()")
                ).strip()
                location_type = "<MISSING>"
                locator_domain = website

                address = store.xpath(".//div[@class='card__body spacing']/p[1]/text()")
                add_list = []
                for add in address:
                    if len("".join(add).strip()) > 0:
                        add_list.append("".join(add).strip())

                raw_address = ", ".join(add_list).strip().replace(",,", ",").strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address and formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zipp = formatted_addr.postcode
                if state and state == "K67":
                    state = "<MISSING>"
                    zipp = "K67 " + zipp

                if zipp:
                    zipp = (
                        zipp.replace("CEP", "")
                        .strip()
                        .replace("CP ", "")
                        .strip()
                        .replace("C. P.", "")
                        .strip()
                    )

                if city and city == "Bandar Seri Begawan Bs8811":
                    city = "Bandar Seri Begawan"
                    zipp = "BS8811"

                phone = "".join(
                    store.xpath(".//div[@class='card__body spacing']/p[2]//text()")
                ).strip()

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                map_link = "".join(
                    store_sel.xpath(
                        '//div[@class="grid__item"]/a[contains(@href,"google.com/maps")]/@href'
                    )
                ).strip()

                latitude = ""
                longitude = ""
                if "sll=" in map_link:
                    latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("sll=")[1].strip().split(",")[1].strip()
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
