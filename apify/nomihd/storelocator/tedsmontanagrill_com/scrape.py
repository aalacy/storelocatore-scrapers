# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us
from lxml import etree

website = "tedsmontanagrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.tedsmontanagrill.com/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="featurelink"]/@href')
    for store_id in stores:
        log.info(f"pulling info for storeID:{store_id}")
        store_req = session.get(
            "https://www.tedsmontanagrill.com/scripts/CtLocationsXmlV2.3.php?lat=0&lng=0&radius=200&sid="
            + store_id,
            headers=headers,
        )

        store_xml = etree.fromstring(store_req.text)

        page_url = search_url
        locator_domain = website
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zip = ""
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = ""

        markers = store_xml.xpath("//markers/marker")
        for marker in markers:
            latitude = marker.attrib["tmglat"]
            longitude = marker.attrib["tmglng"]
            store_number = marker.attrib["tmgid"].replace("tmg", "").strip()
            location_name = marker.attrib["tmgname"]
            street_address = (
                marker.attrib["tmgaddress"]
                .replace("<br>", " ")
                .strip()
                .replace("<b>(Near Denver International Airport)</b>", "")
                .strip()
            )
            city = marker.attrib["tmgcity"]
            state = marker.attrib["tmgstate"]
            zip = marker.attrib["tmgzip"]
            phone = marker.attrib["tmgphone"]
            hours_of_operation = marker.attrib["tmghours"]
            if "temporarily closed" in hours_of_operation:
                location_type = "temporarily closed"

        try:
            hours_of_operation = "".join(
                "; ".join(hours_of_operation.split("<br>")[1:]).strip().split("\n")
            ).strip()
            try:
                hours_of_operation = hours_of_operation.split("<")[0].strip()
            except:
                pass
        except:
            pass

        try:
            if "-->" in marker.attrib["tmghours"]:
                hours_of_operation = "".join(
                    "; ".join(
                        marker.attrib["tmghours"].split("-->")[-1].strip().split("<br>")
                    )
                    .strip()
                    .split("\n")
                ).strip()

        except:
            pass
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

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
