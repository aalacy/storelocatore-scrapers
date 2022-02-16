# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "dodge.com/ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.dodge.com/ae",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    # key => country, value=> [API-URL,Locator_url]
    url_dict = {
        "United Arab Emirates": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_ae/configForms/fad_uae.js",
            "https://www.dodge.com/ae/en/find-us.html",
        ],
        "Philippines": [
            "https://www.dodge.com/content/dam/cross-regional/asean/dodge/en_ph/fad/philippines_fad.js",
            "https://www.dodge.com/ph/en/find-a-dealer.html",
        ],
        "Bahrain": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_bh/configForms/fad_Bahrain.js",
            "https://www.dodge.com/bh/en/find-us.html",
        ],
        "Iraq": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_iq/configForms/fad_iraq.js",
            "https://www.dodge.com/iq/en/find-us.html",
        ],
        "Jordan": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_jo/configForms/fad_Jordon.js",
            "https://www.dodge.com/jo/en/find-us.html",
        ],
        "Kuwait": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_kw/configForms/fad_kuwait.js",
            "https://www.dodge.com/kw/en/find-us.html",
        ],
        "Lebanon": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_lb/configForms/fad_lebanon.js",
            "https://www.dodge.com/lb/en/find-us.html",
        ],
        "Oman": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_om/configForms/fad_Oman.js",
            "https://www.dodge.com/om/en/find-us.html",
        ],
        "Qatar": [
            "https://www.dodge.com/content/dam/cross-regional/emea/dodge/en_qa/configForms/fad_qatar.js",
            "https://www.dodge.com/qa/en/find-us.html",
        ],
        "Brunei": [
            "https://www.dodge.com/content/dam/cross-regional/asean/dodge/en_bn/fad/brunei_fad.js",
            "https://www.dodge.com/bn/en/find-a-dealer.html",
        ],
    }

    with SgRequests() as session:
        for key, val in url_dict.items():
            country_code = key.strip()
            search_url = val[0]
            log.info(
                f"fetching data for country:{country_code} having url: {search_url}"
            )
            search_res = session.get(search_url, headers=headers)
            store_json = search_res.json()
            if "sales" in store_json:
                stores = store_json["sales"]
                for store in stores:
                    locator_domain = website

                    location_name = store["dealerName"]
                    page_url = val[1]

                    location_type = store["division"] + " " + store["department"]
                    raw_address = store.get("dealerAddress1", "<MISSING>")
                    if raw_address:
                        if ")" in raw_address:
                            raw_address = raw_address.split(")", 1)[1].strip()

                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if street_address:
                        if formatted_addr.street_address_2:
                            street_address = (
                                street_address + ", " + formatted_addr.street_address_2
                            )
                    else:
                        if formatted_addr.street_address_2:
                            street_address = formatted_addr.street_address_2

                    city = store.get("dealerCity", "<MISSING>")
                    state = store.get("dealerState", "<MISSING>")
                    zip = store.get("dealerZipCode", "<MISSING>")
                    if zip == "no":
                        zip = "<MISSING>"

                    phone = store.get("phoneNumber", "<MISSING>")
                    if phone == "no":
                        phone = "<MISSING>"

                    phone = phone.split("/")[0].strip()
                    hours_list = []
                    if "openingHours" in store:
                        hours = store["openingHours"]
                        for day in hours.keys():
                            hours_list.append(day + ":" + hours[day])

                    hours_of_operation = "; ".join(hours_list).strip()
                    store_number = "<MISSING>"

                    latitude, longitude = (
                        store.get("dealerShowroomLatitude"),
                        store.get("dealerShowroomLongitude"),
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
                        location_type=location_type.strip(),
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
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LOCATION_NAME,
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
