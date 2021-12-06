# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "ram.com/ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.ram.com/ae",
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
        "French Polynesia": [
            "https://www.ram.com/content/dam/cross-regional/asean/ramtrucks/fr_pf/fad/frenchpolynesia_fad.js",
            "https://www.ram.com/pf/fr/find-a-dealer.html",
        ],
        "New Caledonia": [
            "https://www.ram.com/content/dam/cross-regional/asean/ramtrucks/fr_nc/fad/newcaledonia_fad.js",
            "https://www.ram.com/nc/fr/find-a-dealer.html",
        ],
        "Vietnam": [
            "https://www.ram.com/content/dam/cross-regional/asean/ramtrucks/en_vn/fad/vietnam_fad.js",
            "https://www.ram.com/vn/en/find-a-dealer.html",
        ],
        "United Arab Emirates": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_ae/configForms/fad_uae.js",
            "https://www.ram.com/ae/en/find-us.html",
        ],
        "Philippines": [
            "https://www.ram.com/content/dam/cross-regional/asean/ramtrucks/en_ph/fad/philippines_fad.js",
            "https://www.ram.com/ph/en/find-a-dealer.html",
        ],
        "Bahrain": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_bh/configForms/fad_Bahrain.js",
            "https://www.ram.com/bh/en/find-us.html",
        ],
        "Iraq": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_iq/configForms/fad_iraq.js",
            "https://www.ram.com/iq/en/find-us.html",
        ],
        "Jordan": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_jo/configForms/findus_Jordon.js",
            "https://www.ram.com/jo/en/find-us.html",
        ],
        "Kuwait": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_kw/configForms/fad_kuwait.js",
            "https://www.ram.com/kw/en/find-us.html",
        ],
        "Oman": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_om/configForms/FindUs_Oman.js",
            "https://www.ram.com/om/en/find-us.html",
        ],
        "Qatar": [
            "https://www.ram.com/content/dam/cross-regional/emea/ramtrucks/en_qa/configForms/fad_qatar.js",
            "https://www.ram.com/qa/en/find-us.html",
        ],
        "Cambodia": [
            "https://www.ram.com/content/dam/cross-regional/asean/ramtrucks/en_kh/fad/cambodia_fad.js",
            "https://www.ram.com/kh/en/find-a-dealer.html",
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
