# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "royalfarms.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_splitted_address(address):
    add_dict = {}
    if address[0][0].isdigit():
        add_dict["street_address"] = address[0]
        add_dict["city_state_zip"] = address[1].replace(",,", ",").strip()
    else:
        if len(address) == 3:
            add_dict["street_address"] = address[0]
            add_dict["city_state_zip"] = address[1].replace(",,", ",").strip()
        else:
            add_dict["street_address"] = address[1]
            add_dict["city_state_zip"] = address[2].replace(",,", ",").strip()
    return add_dict


def fetch_data():
    # Your scraper here
    locator_domain = website
    locations_resp = session.get(
        "https://royalfarms.com/location_results.asp",
        headers=headers,
    )
    locations_sel = lxml.html.fromstring(locations_resp.text)
    states = locations_sel.xpath('//select[@id="state"]' "/option[position()>1]/@value")
    for state in states:
        data = {
            "submitStore": "yes",
            "city": "",
            "state": state,
            "zip": "",
            "miles": "15",
        }

        stores_resp = session.post(
            "https://royalfarms.com/location_results.asp", data=data, headers=headers
        )

        stores_sel = lxml.html.fromstring(stores_resp.text)
        stores = stores_sel.xpath('//tr[@class="listdata"]')
        for store in stores:
            page_url = "https://royalfarms.com/locations"
            temp_address = store.xpath("td[1]/text()")
            address_mobile = [
                "".join(add).strip()
                for add in temp_address
                if len("".join(add).strip()) > 0
            ]
            location_name = "".join(store.xpath("td[1]/strong/text()")).strip()
            add_dict = get_splitted_address(address_mobile)
            add_dict["city_state_zip"] = (
                add_dict["city_state_zip"].replace(", ,", ", ").strip()
            )
            street_address = "".join(add_dict["street_address"]).strip()

            city = "".join(add_dict["city_state_zip"]).strip().split(",")[0].strip()
            state = (
                "".join(add_dict["city_state_zip"])
                .strip()
                .split(",")[1]
                .strip()
                .split("\xa0")[0]
                .strip()
            )

            try:
                zip = (
                    "".join(add_dict["city_state_zip"])
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split("\xa0")[1]
                    .strip()
                )
            except:
                zip = "<MISSING>"

            store_number = location_name.replace("STORE #", "").strip()
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            country_code = "US"
            phone = "".join(address_mobile[-1]).strip()
            if (
                not phone.replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(" ", "")
                .strip()
                .isdigit()
            ):
                phone = "<MISSING>"

            hours_of_operation = "".join(store.xpath("td[2]/em/text()")).strip()
            if "Closed" in hours_of_operation:
                hours_of_operation = "<MISSING>"
                location_type = "Temporarily Closed"

            if "Coming Soon" in hours_of_operation:
                hours_of_operation = "<MISSING>"
                location_type = "Coming Soon"

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
