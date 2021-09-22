# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import xmltodict

website = "narscosmetics.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
    "X-Prototype-Version": "1.7.2",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}
params = (
    ("lang", "en_US"),
    (
        "xml_request",
        '<request><appkey>18D36CFE-4EA9-11E6-8D1F-49249CAB76FA</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline></addressline><longitude></longitude><latitude></latitude><country>US</country></geoloc></geolocs><searchradius>1000</searchradius><where><or><curbsideflag><eq></eq></curbsideflag><deliveryflag><eq></eq></deliveryflag><doordashflag><eq></eq></doordashflag><banquets><eq></eq></banquets><patio><eq></eq></patio><onlineordering><eq></eq></onlineordering><grubhub><eq></eq></grubhub></or></where><nobf>1</nobf><stateonly>1</stateonly></formdata></request>',
    ),
)


def fetch_data():
    stores_req = session.get(
        "https://hosted.where2getit.com/ajax", headers=headers, params=params
    )

    xml_resp = xmltodict.parse(stores_req.text)
    stores = xml_resp["response"]["collection"]["poi"]
    for store in stores:
        page_url = (
            "http://locations.thecheesecakefactory.com"
            + store["menu_url"].split(".com")[1].strip().split("?")[0].strip()
        )
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store.get("city", "<MISSING>")
        state = store["state"] if store["state"] else store["province"]
        zip = store.get("postalcode", "<MISSING>")
        country_code = store["country"]
        store_number = store["uid"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        hours_list = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for key in store.keys():
            if key in days:
                day = key
                time = store[day]
                if time is not None:
                    hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(
            [
                str(store["hourslabel1"]).replace("None", "")
                + ": "
                + str(store["hoursfromto1"]).replace("None", ""),
                str(store["hourslabel2"]).replace("None", "")
                + ": "
                + str(store["hoursfromto2"]).replace("None", ""),
                str(store["hourslabel3"]).replace("None", "")
                + ": "
                + str(store["hoursfromto3"]).replace("None", ""),
                str(store["hourslabel4"]).replace("None", "")
                + ": "
                + str(store["hoursfromto4"]).replace("None", ""),
            ]
        )
        latitude = store["latitude"]
        longitude = store["longitude"]

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
