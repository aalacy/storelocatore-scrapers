# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "zadig-et-voltaire.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "storelocator.zadig-et-voltaire.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://storelocator.zadig-et-voltaire.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = (
        "https://storelocator.zadig-et-voltaire.com/index.html?per=50&offset={}"
    )
    offset = 0
    with SgRequests() as session:
        while True:
            response = session.get(search_url.format(str(offset)), headers=headers)
            stores = response.json()["response"]["entities"]
            if len(stores) <= 0:
                break
            for store in stores:
                page_url = store["profile"].get("landingPageUrl", "<MISSING>")
                locator_domain = website
                if "c_pagesNom" not in store["profile"]:
                    continue
                location_name = store["profile"]["c_pagesNom"]
                addr = store["profile"]["address"]
                raw_address = addr["line1"]
                if addr["line2"] and len(addr["line2"]) > 0:
                    raw_address = raw_address + ", " + addr["line2"]

                if addr["line3"] and len(addr["line3"]) > 0:
                    raw_address = raw_address + ", " + addr["line3"]

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = addr["city"]

                state = addr["region"]
                zip = addr["postalCode"]

                country_code = addr["countryCode"]
                phone = "<MISSING>"
                try:
                    phone = store["profile"]["mainPhone"]["display"]
                except:
                    pass

                store_number = "<MISSING>"
                location_type = store["profile"].get("c_storeType", "")
                typ2 = store["profile"].get("c_typeDePDV", "")
                if len(typ2) > 0:
                    if len(location_type) > 0:
                        location_type = location_type + ", " + typ2
                    else:
                        location_type = typ2

                hours_list = []
                try:
                    hours = store["profile"]["hours"]["normalHours"]
                    for hour in hours:
                        day = hour["day"]
                        if hour["isClosed"] is False:
                            time = (
                                str(hour["intervals"][0]["start"])
                                + " - "
                                + str(hour["intervals"][0]["end"])
                            )
                            hours_list.append(day + ":" + time)
                        else:
                            hours_list.append(day + ":Closed")

                except:
                    pass

                hours_of_operation = "; ".join(hours_list).strip()

                latitude = store["profile"]["yextDisplayCoordinate"]["lat"]
                longitude = store["profile"]["yextDisplayCoordinate"]["long"]
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

            offset = offset + 50


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
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
