# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thececilianbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.thececilianbank.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.thececilianbank.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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


def fetch_data():
    # Your scraper here
    search_url = "https://www.thececilianbank.com/locations-2/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = list(search_sel.xpath('//*[contains(@class,"section") and .//h4]'))

        for store in store_list:

            page_url = search_url
            locator_domain = website

            location_name = "".join(store.xpath(".//h4[1]/text()")).strip()

            full_address = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p[1]//text()")],
                )
            )
            hours = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p[3]//text()")],
                )
            )
            hours_of_operation = ("; ".join(hours)).replace(":;", ":")

            if "ATM Only Location" in full_address:
                full_address = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//p[2]//text()")],
                    )
                )
                hours_of_operation = "<MISSING>"

            if "Loan Office/ATM Only Location" in full_address:
                full_address = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//p[2]//text()")],
                    )
                )
                hours = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//p[4]//text()")],
                    )
                )
                hours_of_operation = ("; ".join(hours)).replace(":;", ":")
            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            store_number = "<MISSING>"
            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//p[contains(.//text(),"P:")]/text()')
                    ],
                )
            )

            if len(phone) > 0:
                phone = phone[0].strip()
            else:
                phone = "<MISSING>"

            if "ATM" in location_name:
                location_type = "ATM"
            elif "Loan Office" in location_name:
                location_type = "Loan Office"
            else:
                location_type = "Branch"

            map_link = store.xpath('.//div[@title="Google Map"]')

            latitude = "".join(map_link[0].xpath("@data-lat"))
            longitude = "".join(map_link[0].xpath("@data-lng"))

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
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
