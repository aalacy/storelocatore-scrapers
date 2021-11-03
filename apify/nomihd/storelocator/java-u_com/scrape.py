# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "java-u.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.java-u.com",
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

    search_url = "https://www.java-u.com/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        log.info(search_res)
        search_sel = lxml.html.fromstring(search_res.text)

        for no in range(1, 50):
            store_info_divs = search_sel.xpath(
                f"//div[@data-testid][count(preceding-sibling::div[@tabindex])={no}]"
            )

            if not store_info_divs:
                break

            page_url = search_url

            locator_domain = website

            location_name = "".join(store_info_divs[0].xpath(".//text()")).strip()

            full_address = list(
                filter(
                    str,
                    [x.strip() for x in store_info_divs[3].xpath(".//p//text()")],
                )
            )
            if "Canada" not in full_address[-1]:
                full_address = full_address[:-1]

            street_address = " ".join(full_address[0:-1])
            if "International Airport" in street_address:
                street_address = street_address.split("International Airport")[
                    -1
                ].strip()

            city_state_zip = full_address[-1]

            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip()
            zip = city_state_zip.split(",")[-1].strip().replace("Canada", "").strip()
            country_code = "CA"

            store_number = "<MISSING>"

            phone = (
                "".join(store_info_divs[1].xpath(".//text()"))
                .strip()
                .replace("Phone:", "")
                .strip()
            )

            location_type = "<MISSING>"

            hours = store_info_divs[-1].xpath("p")
            hours_list = []
            for hour in hours:
                hours_list.append("".join(hour.xpath(".//text()")).strip())

            hours_of_operation = "; ".join(hours_list)
            latitude, longitude = "<MISSING>", "<MISSING>"
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
