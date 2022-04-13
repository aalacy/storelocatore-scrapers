# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mscdirect.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.mscdirect.com/corporate/locations-branches"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//div[@class="state-div"]')
        for store in stores:
            Type = "".join(store.xpath("div/@class")).strip()
            location_type = "<MISSING>"
            if Type == "state-block customer-service ns-p":
                location_type = "customer-service"
            elif Type == "state-block customer-service-fulfillment ns-p":
                location_type = "customer-service-fulfillment"
            else:
                location_type = "branch"

            page_url = search_url

            location_name = "".join(store.xpath("div/strong/text()")).strip()

            locator_domain = website

            raw_info = store.xpath("div/text()")
            add_list = []
            for add in raw_info:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            phone = ""
            raw_address = ""
            for index in range(0, len(add_list)):
                if "Local:" in add_list[index]:
                    phone = add_list[index]
                    if len(add_list[:index]) > 1:
                        raw_address = ", ".join(add_list[:index])

                if "Toll-Free" in add_list[index]:
                    phone = add_list[index]
                    if len(add_list[:index]) > 1:
                        raw_address = ", ".join(add_list[:index])
                if "Customer Service:" in add_list[index]:
                    phone = add_list[index]
                    if len(add_list[:index]) > 1:
                        raw_address = ", ".join(add_list[:index])

                if "Offices:" in add_list[index]:
                    phone = add_list[index]
                    if len(add_list[:index]) > 1:
                        raw_address = ", ".join(add_list[:index])

                try:
                    if "(" in add_list[index]:
                        if (
                            len(
                                "".join(
                                    add_list[index]
                                    .split(" ")[0]
                                    .strip()
                                    .replace("(", "")
                                    .replace(")", "")
                                    .strip()
                                )
                            )
                            == 3
                        ):
                            phone = add_list[index]
                            if len(add_list[:index]) > 1:
                                raw_address = ", ".join(add_list[:index])
                except:
                    pass

            phone = (
                phone.replace("Local:", "")
                .replace("Toll-Free", "")
                .replace("Customer Service:", "")
                .replace("Offices:", "")
                .strip()
            )
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "US"

            if street_address:
                street_address = (
                    street_address.replace("Cardinal Point At Bayside ", "")
                    .replace("Msc Metalworking Call Center ", "")
                    .replace("Jefferson Business Center ", "")
                    .replace("Portland North Business Park", "")
                    .replace("Previously Deer Park Ny", "")
                    .replace("Eastpointe Business Center ", "")
                    .strip()
                )
            if city is None:
                city = location_name.split(",")[0].strip()
                if street_address:
                    street_address = street_address.replace(city, "").strip()

            if state is None:
                state = location_name.split(",")[-1].strip().split(" ")[0].strip()

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            location_name = (
                "MSC " + location_type.replace("-", " ").strip().capitalize()
            )

            map_link = "".join(
                store.xpath('div/a[contains(text(),"Map and Directions")]/@href')
            ).strip()
            latitude = ""
            longitude = ""
            if len(map_link) > 0:
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
                    SgRecord.Headers.PHONE,
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
