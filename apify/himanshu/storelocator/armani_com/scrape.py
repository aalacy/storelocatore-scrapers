import json
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

session = SgRequests()
website = "armani.com"

headers = {
    "authority": "www.armani.com",
    "path": "/api/armani/wcs/resources/store/armanigroup_US/storelocator/boutiques/?pageSize=1000&pageNumber=1",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "x-dtpc": "3$370197139_564h3vDWDKQSNBJCCMBJPFHEJUGBWWQHUMMKER-0e8",
    "x-ibm-client-id": "d96f05f8-4f2f-4444-9787-bb6f0ea29bc8",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data(sgw: SgWriter):
    stores_req = session.get(
        "https://www.armani.com/api/armani/wcs/resources/store/armanigroup_US/storelocator/boutiques/?pageSize=1000&pageNumber=1",
        headers=headers,
    )

    found = []
    dict_from_json = json.loads(stores_req.text)["data"]
    for store_data in dict_from_json:
        location_name = store_data["storeName"].replace("&amp;", "&")
        raw_address = store_data["address"]["line1"]
        formatted_addr = parser.parse_address_intl(raw_address)

        street_address = formatted_addr.street_address_1
        if street_address is not None and formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2
        if not street_address and formatted_addr.street_address_2:
            street_address = formatted_addr.street_address_2

        state = formatted_addr.state
        if state is None:
            state = "<MISSING>"

        zip = formatted_addr.postcode

        if zip and ";" in zip:
            street_address = street_address + ", " + zip.split(";")[-1]
            zip = zip.split(";")[1]

        city = store_data["address"]["city"]

        if not street_address or len(street_address) < 4 or street_address == "Cancun":
            street_address = raw_address[: raw_address.rfind(city)].strip()
            if ";" in street_address:
                street_address = street_address[: street_address.rfind(";")].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]

        country_code = store_data["address"]["countryCode"].upper()
        store_number = store_data["storeNumber"]

        if not zip and country_code == "GB":
            if " W1" in street_address:
                zip = street_address[street_address.find("W1") :]
            elif "Sw1X7Xl" in street_address:
                zip = "Sw1X7Xl"
            if zip:
                street_address = (
                    street_address.replace(zip, "").replace(" ,", ",").strip()
                )

        if location_name.strip() + street_address.strip() in found:
            continue
        found.append(location_name.strip() + street_address.strip())

        try:
            phone = store_data["address"]["phone1"]
        except:
            phone = ""
        location_type = ""
        raw_types = store_data["attributes"]
        for row in raw_types:
            if row["name"] == "Store Type":
                types = row["values"]
                for t in types:
                    location_type = (location_type + ", " + t["value"]).strip()
                location_type = location_type[1:].strip()
        latitude = store_data["spatialData"]["latitude"]
        longitude = store_data["spatialData"]["longitude"]
        hours_of_operation = ""
        raw_hours = store_data["openingTimes"]
        for row in raw_hours:
            if row["dayNumber"] == 1:
                day = "Mon"
            elif row["dayNumber"] == 2:
                day = "Tue"
            elif row["dayNumber"] == 3:
                day = "Wed"
            elif row["dayNumber"] == 4:
                day = "Thu"
            elif row["dayNumber"] == 5:
                day = "Fri"
            elif row["dayNumber"] == 6:
                day = "Sat"
            elif row["dayNumber"] == 7:
                day = "Sun"

            slots = row["slots"]
            day_times = day
            for slot in slots:
                day_times = (
                    day_times + " " + slot["openTime"] + "-" + slot["closeTime"]
                ).strip()
            hours_of_operation = (hours_of_operation + " " + day_times).strip()

        page_url = "https://www.armani.com/en-us/store-locator#store/" + str(
            store_data["storeNumber"]
        )

        sgw.write_row(
            SgRecord(
                locator_domain=website,
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
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
