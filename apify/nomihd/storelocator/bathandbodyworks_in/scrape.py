# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bathandbodyworks.in/bbw-store-locator.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="store_address"]/..')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            location_name = "".join(
                store.xpath('.//div[@class="store_title"]/text()')
            ).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//p[@class="store_addressline"]//text()')
                    ],
                )
            )

            raw_address = (
                " ".join(store_info)
                .strip('" ')
                .replace("MAJOR BRANDS INDIA PVT LTD, BATH & BODY WORKS,", "")
                .strip()
                .replace("MAJOR BRANDS INDIA PVT LTD,  Bath & Body Works,", "")
                .strip()
                .replace("MAJOR BRANDS INDIA PVT LTD,", "")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            state = formatted_addr.state
            raw_address = (
                raw_address.split("!!!")[-1]
                .strip()
                .replace("\\/", "/")
                .strip()
                .split("PH -")[0]
                .strip()
                .split("; Contact-")[0]
                .strip()
                .replace("\\u2013", "-")
                .strip()
                .split("; contact -")[0]
                .strip()
                .replace("\\n", "")
                .strip()
                .split("Email:")[0]
                .strip()
                .split(", INDIA")[0]
                .strip()
                .split(". Contact")[0]
                .strip()
            )
            if raw_address[-1] == ",":
                raw_address = "".join(raw_address[:-1]).strip()

            street_address = ", ".join(raw_address.split(",")[:-1]).strip()
            city = (
                raw_address.split(",")[-1]
                .strip()
                .replace(
                    "Chandigarh Industrial Area (Near centra mall) Phase", "Chandigarh"
                )
                .strip()
            )
            try:
                city = city.split("-")[0].strip()
            except:
                pass
            state = "<MISSING>"
            zip = "<MISSING>"
            try:
                if "Pincode" in raw_address:
                    city = city.split("Pincode")[0].strip()
                    zip = raw_address.split("Pincode")[1].strip()
                else:
                    zip = raw_address.rsplit("-", 1)[-1].strip()
            except:
                pass

            if not zip.isdigit():
                zip = "<MISSING>"

            if city == "Shop No":
                street_address = (
                    "Shop No - G 14 15 L2 Lower ground floor Hi-tech city opp to I Labs"
                )
                city = "Hyderabad"

            if city == "Infinity 2 Link RD Malad(W) Mumbai":
                street_address = "F-118, Infinity 2 Link RD Malad(W)"
                city = "Mumbai"

            try:
                if city.split(" ")[-1].isdigit():
                    zip = city.split(" ")[-1]
                    city = " ".join(city.split(" ")[:-1]).strip()
            except:
                pass

            country_code = "IN"

            store_number = "".join(
                store.xpath('.//span[@class="store-number"]/text()')
            ).strip(" .")
            phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude, longitude = (
                "".join(store.xpath("./@str_lati/@value")).strip(),
                "".join(store.xpath("./@str_longi/@value")).strip(),
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
