# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "jeep.com.bd"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.jeep.com.bd",
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
        "Bangladesh": [
            "https://www.jeep.com.bd/content/dam/cross-regional/asean/jeep/en_bd/fad/bangladesh_fad.js",
            "https://www.jeep.com.bd/en/find-a-dealer.html",
        ],
        "Brunei": [
            "https://www.jeep.com.bn/content/dam/cross-regional/asean/jeep/en_bn/fad/brunei_fad.js",
            "https://www.jeep.com.bn/en/find-a-dealer.html",
        ],
        "Cambodia": [
            "https://www.jeep.com.kh/content/dam/cross-regional/asean/jeep/en_bn/fad/brunei_fad.js",
            "https://www.jeep.com.kh/en/find-a-dealer.html",
        ],
        "French Polynesia": [
            "https://www.jeep-pf.com/content/dam/cross-regional/asean/jeep/fr_pf/fad/frenchpolynesia_fad.js",
            "https://www.jeep-pf.com/fr/find-a-dealer.html",
        ],
        "Hong Kong (China)": [
            "https://www.jeep.com.hk/content/dam/cross-regional/asean/jeep/en_hk/fad/hongkong_fad.js",
            "https://www.jeep.com.hk/en/find-a-dealer.html",
        ],
        "Indonesia": [
            "https://www.jeep-id.com/content/dam/cross-regional/asean/jeep/en_id/fad/indonesia_fad.js",
            "https://www.jeep-id.com/en/find-a-dealer.html",
        ],
        "Mongolia": [
            "https://www.jeep.mn/content/dam/cross-regional/asean/jeep/en_mn/fad/mongolia_fad.js",
            "https://www.jeep.mn/en/find-a-dealer.html",
        ],
        "New Caledonia": [
            "https://www.jeep.nc/content/dam/cross-regional/asean/jeep/fr_nc/fad/newcaledonia_fad.js",
            "https://www.jeep.nc/fr/find-a-dealer.html",
        ],
        "Philippines": [
            "https://www.jeep.com.ph/content/dam/cross-regional/asean/jeep/en_ph/fad/philippines_fad.js",
            "https://www.jeep.com.ph/en/find-a-dealer.html",
        ],
        "Singapore": [
            "https://www.jeep.com.sg/content/dam/cross-regional/asean/jeep/en_sg/fad/singapore_fad.js",
            "https://www.jeep.com.sg/en/find-a-dealer.html",
        ],
        "Sri Lanka": [
            "https://www.jeep.com.lk/content/dam/cross-regional/asean/jeep/en_lk/fad/srilanka_fad.js",
            "https://www.jeep.com.lk/en/find-a-dealer.html",
        ],
        "Vietnam": [
            "https://www.jeep-vn.com/content/dam/cross-regional/asean/jeep/en_vn/fad/vietnam_fad.js",
            "https://www.jeep-vn.com/en/find-a-dealer.html",
        ],
        "Gabon": [
            "https://www.jeep.ga/content/dam/cross-regional/fcacountryfinder/assets/glps/africa/jeep/jeep_ga_dealer.js",
            "https://www.jeep.ga/",
        ],
        "Bahrain": [
            "https://www.jeep-bahrain.com/content/dam/cross-regional/emea/jeep/ar_me/configform/bahrain/fad_Bahrain_ar.js",
            "https://www.jeep-bahrain.com/ar/find-us.html",
        ],
        "Iraq": [
            "https://www.jeep-iraq.com/content/dam/cross-regional/emea/jeep/ar_me/configform/iraq/fad_iraq_ar.js",
            "https://www.jeep-iraq.com/ar/find-us.html",
        ],
        "Jordan": [
            "https://www.jeep-jordan.com/content/dam/cross-regional/emea/jeep/ar_me/configform/jordan/fad_Jordon_ar.js",
            "https://www.jeep-jordan.com/ar/find-us.html",
        ],
        "Oman": [
            "https://www.jeep-oman.com/content/dam/cross-regional/emea/jeep/ar_me/configform/oman/fad_Oman_ar.js",
            "https://www.jeep-oman.com/ar/find-us.html",
        ],
        "Qatar": [
            "https://www.jeep-qatar.com/content/dam/cross-regional/emea/jeep/ar_me/configform/qatar/fad_qatar_ar.js",
            "https://www.jeep-qatar.com/ar/find-us.html",
        ],
        "UAE (Abudhabi)": [
            "https://www.jeep-abudhabi.com/content/dam/cross-regional/emea/jeep/en_me/configform/abudhabi/fad_abu_dhabi.js",
            "https://www.jeep-abudhabi.com/en/find-us.html",
        ],
        "UAE (Dubai)": [
            "https://www.jeep-dubai.com/content/dam/cross-regional/emea/jeep/en_me/find-us/uae/fad_uae.js",
            "https://www.jeep-dubai.com/en/",
        ],
        "Australia": [
            "https://www.jeep.com.au/content/dam/cross-regional/apac/jeep/en_au/find-a-dealer/new/jeep-dealers.js",
            "https://www.jeep.com.au/dealers.html",
        ],
        "India": [
            "https://www.jeep-india.com/content/dam/cross-regional/apac/jeep/en_in/find-a-dealer/jeep-dealers.js",
            "https://www.jeep-india.com/find-dealer.html",
        ],
        "Japan": [
            "https://www.jeep-japan.com/content/dam/cross-regional/apac/jeep/ja_jp/find-a-dealer/jeep-dealers.js",
            "https://www.jeep-japan.com/dealer.html",
        ],
        "South Korea": [
            "https://www.jeep.co.kr/content/dam/cross-regional/apac/jeep/ko_kr/find-a-dealer/jeep-korea-dealers211108.js",
            "https://www.jeep.co.kr/find_a_dealer.html",
        ],
    }

    with SgRequests() as session:
        for key, val in url_dict.items():
            country_code = key
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

                    if street_address:
                        if street_address == "154":
                            street_address = "CPOBox 154"

                    city = store.get("dealerCity", "<MISSING>")
                    state = (
                        store.get("dealerState", "<MISSING>")
                        .replace("UAE-AbuDhabi", "")
                        .replace("United Arab Emirates", "")
                        .strip()
                    )
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
