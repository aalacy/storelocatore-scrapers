# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "alfaromeo.co.nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://alfaromeo.co.nz/find-a-dealer"

    with SgRequests() as session:
        search_res = session.get(api_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        sections = search_sel.xpath("//optgroup")
        for sec in sections:
            location_type = "".join(sec.xpath("@label")).strip()
            stores = sec.xpath("option")

            for store in stores:

                locator_domain = website

                location_name = "".join(store.xpath(".//text()"))
                no = "".join(store.xpath("./@value"))
                page_url = f"https://alfaromeo.co.nz/get-dealers-by-region/{no}"

                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                json_res = json.loads(store_res.text)

                store_sel = lxml.html.fromstring(json_res["html"])

                raw_address = ", ".join(
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    "//h6[@class='address']//text()"
                                )
                            ],
                        )
                    )
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                if city:
                    city = city.replace(
                        "New Plymouth New Plymouth", "New Plymouth"
                    ).strip()
                state = formatted_addr.state

                zip = formatted_addr.postcode
                if zip:
                    zip = zip.split(" ")[-1].strip()

                country_code = "NZ"

                phone = "".join(store_sel.xpath("//a[@class='phone']//text()")).strip()

                url = "".join(store_sel.xpath(".//a[last()]/@href"))
                if "http" in url:
                    page_url = url
                    log.info(page_url)
                    store_res = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_res.text)

                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[contains(./h4/text(),"SALES")]/p[last()]//text()'
                                )
                            ],
                        )
                    )
                    hours_of_operation = "; ".join(hours).replace(".;", ":").strip()
                else:
                    hours_of_operation = "<MISSING>"

                store_number = no

                latitude, longitude = (
                    json_res["dealers"][0][1],
                    json_res["dealers"][0][2],
                )
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
