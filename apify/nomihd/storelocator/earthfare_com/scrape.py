# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "earthfare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.earthfare.com/stores/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(
            stores_req.text.split("LOCATIONS COMING SOON")[0].strip()
        )
        stores = stores_sel.xpath(
            '//div[@class="elementor-text-editor elementor-clearfix"]'
        )
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath("h3/text()")).strip()
            if len(location_name) <= 0:
                location_name = "".join(store.xpath("h5/span/text()")).strip()

            address = store.xpath("p/text()")
            if len("".join(address).strip()) <= 0:
                address = store.xpath("text()")

            if len("".join(address).strip()) <= 0:
                address = store.xpath("h6/text()")

            add_list = []
            phone = ""
            for add in address:
                temp_text = "".join(add.strip())
                if len(temp_text) > 0:
                    if "Phone:" in temp_text or "Ph:" in temp_text:
                        if "," in temp_text:
                            try:
                                add_list.append(temp_text.split("Phone:")[0].strip())
                                phone = temp_text.split("Phone:")[1].strip()
                            except:
                                try:
                                    add_list.append(temp_text.split("Ph:")[0].strip())
                                    phone = temp_text.split("Ph:")[1].strip()
                                except:
                                    pass

                        else:
                            phone = (
                                temp_text.replace("Phone:", "")
                                .replace("Ph:", "")
                                .strip()
                            )
                            break

                    elif "(" in temp_text and ")" in temp_text:
                        phone = temp_text
                    else:
                        add_list.append("".join(temp_text))

            street_address = (
                ", ".join(add_list[:-1])
                .strip()
                .replace("Lady Lake Commons,", "")
                .strip()
            )
            city = add_list[-1].split(",")[0].strip()
            state = add_list[-1].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[-1].split(",")[1].strip().split(" ")[1].strip()
            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
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
