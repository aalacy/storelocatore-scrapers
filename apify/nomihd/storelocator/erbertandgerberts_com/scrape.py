# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "erbertandgerberts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.erbertandgerberts.com/store-sitemap.xml"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = "".join(stores[index].split("</loc>")[0].strip()).strip()
        if not page_url.split("/locations/")[1].replace("/", "").strip().isdigit():
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            if (
                "coming soon"
                in "".join(
                    store_sel.xpath('//h2[@class="text-red text-bold mb0"]/text()')
                )
                .strip()
                .lower()
            ):
                continue
            locator_domain = website
            location_name = (
                "".join(
                    store_sel.xpath('//h1[@class="ph__title text-cursive mb0"]/text()')
                )
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
            address = store_sel.xpath("//address/text()")
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            if len(add_list) == 1:
                street_address = "<MISSING>"
                city = add_list[0].strip().split(",")[0].strip()
                state = add_list[0].strip().split(",")[1].strip().split(" ")[0].strip()
                zip = add_list[0].strip().split(",")[1].strip().split(" ")[1].strip()
            else:
                street_address = add_list[0].strip()
                city = add_list[1].strip().split(",")[0].strip()
                state = add_list[1].strip().split(",")[1].strip().split(" ")[0].strip()
                zip = add_list[1].strip().split(",")[1].strip().split(" ")[1].strip()

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"
            phone = (
                "".join(store_sel.xpath('//a[contains(@href,"tel:")]/text()'))
                .strip()
                .replace("(NEW)", "")
                .strip()
            )

            location_type = "<MISSING>"

            hours = store_sel.xpath('//div[@class="store__hours"]/ul/li')
            hours_list = []
            for hour in hours:
                hours_list.append(
                    "".join(hour.xpath("span/text()")).strip()
                    + "".join(hour.xpath("text()")).strip()
                )

            hours_of_operation = ";".join(hours_list).strip()
            latitude = (
                store_req.text.split("var lat")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace('"', "")
                .replace("=", "")
                .strip()
            )
            longitude = (
                store_req.text.split("var lng")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace('"', "")
                .replace("=", "")
                .strip()
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
