# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dsv.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://dsv.ankiro.dk/Rest/www.dsv.com-en%20offices/Search?ScPageType=office&regionLang=en&q=*&officeRegion=&officeCountry=&officeService=&officeType=&officeLocationType=&MaxResults=10000"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["Documents"]

    for store in stores:

        page_url = store["Uri"]
        locator_domain = website
        Properties = store["Properties"]
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = ""
        location_type = ""
        for prop in Properties:
            if prop["Name"] == "OfficeCity":
                city = prop["Value"]
            if prop["Name"] == "OfficeCountry":
                country_code = prop["Value"]
            if prop["Name"] == "OfficeName":
                location_name = prop["Value"]
            if prop["Name"] == "OfficeState":
                state = prop["Value"]
            if prop["Name"] == "OfficeZipCode":
                zipp = prop["Value"]
            if prop["Name"] == "OfficeType":
                if prop["ValueList"] is not None:
                    location_type = ", ".join(prop["ValueList"]).strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        address = store_sel.xpath('//div[@class="office-details__address"]')
        street_address = ""
        if len(address) > 0:
            address = address[0].xpath("p/text()")
            if len(address) > 0:
                street_address = address[0].strip()

        phone = store_sel.xpath('//a[contains(@href,"tel:")]')
        if len(phone) > 0:
            phone = "".join(phone[0].xpath("text()")).strip()
        else:
            phone = "<MISSING>"

        hours_of_operation = "<MISSING>"

        store_number = "<MISSING>"

        map_link = "".join(
            store_sel.xpath('//a[contains(text(),"Get directions")]/@href')
        ).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(map_link) > 0:
            try:
                latitude = map_link.split("/place/")[1].strip().split(",")[0].strip()
            except:
                pass

            try:
                longitude = map_link.split("/place/")[1].strip().split(",")[-1].strip()
            except:
                pass

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
