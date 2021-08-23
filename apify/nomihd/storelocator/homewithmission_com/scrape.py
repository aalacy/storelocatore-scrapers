# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "homewithmission.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "homewithmission.com",
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
    base = "https://homewithmission.com"
    search_url = "https://homewithmission.com/locations/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    locations = search_sel.xpath('//li[@id="dropdown-menu-locations"]//li')

    for location in locations:

        page_url = base + "".join(location.xpath("./a/@href"))

        locator_domain = website

        log.info(page_url)
        loc_res = session.get(page_url, headers=headers)
        loc_sel = lxml.html.fromstring(loc_res.text)

        stores = loc_sel.xpath("//main//p[text()]")

        for store in stores:

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//text()")],
                )
            )

            if not store_info or store_info[0] == "Headquarters":
                continue

            full_address = (
                " ".join(store_info[1:]).split("Office:")[0].strip().replace("Â ", " ")
            )
            street_address = ", ".join(full_address.split(",")[:-2]).strip()
            city = full_address.split(",")[-2].strip()
            state = full_address.split(",")[-1].strip().split(" ")[0].strip()
            zip = full_address.split(" ")[-1].strip().replace("CA", "").strip()
            state = state.replace(zip, "").strip()
            country_code = "US"

            location_name = f"MISSION HealthCare {store_info[0]}".strip()

            phone = " ".join(store_info).split("Fax")[0].split("Office:")[1].strip()

            store_number = "".join(store.xpath("./@data-id"))

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
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
