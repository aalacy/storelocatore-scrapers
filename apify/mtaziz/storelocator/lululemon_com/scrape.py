from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lululemon_com")


DOMAIN = "https://www.lululemon.com"
URL_LOCATION = "https://shop.lululemon.com/stores"
MISSING = "<MISSING>"

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}

session = SgRequests()


def fetch_data():
    url = "https://wae-store-experience-prod.lllapi.com/stores"
    s = set()

    json_data = session.get(url, headers=headers, timeout=180).json()
    for item in json_data:

        # for item in json.loads(r.content):
        logger.info(f"item : {item}")
        locator_domain = DOMAIN
        page_url = item["websiteUrl"] or MISSING
        location_name = item["name"]

        # Address Data
        addinfo = item["fullAddress"]
        pa = parse_address_intl(addinfo)
        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING
        city = item["city"]
        state = item["state"]
        zip_postal = addinfo.rsplit(" ", 1)[1]
        country_code = item["country"]
        store_number = item["storeNumber"]
        logger.info(f"Store Number: {store_number}")
        if store_number in s:
            continue
        s.add(store_number)

        latitude = item["latitude"] or MISSING
        longitude = item["longitude"] or MISSING

        location_type = item["storeType"] or MISSING

        # Phone
        try:
            phone = item["phone"]
        except:
            phone = MISSING
        if country_code == "US" or country_code == "CA":
            try:
                if len(phone) < 5:
                    phone = MISSING
            except:
                phone = MISSING

        # Hours of operation
        hours = ""
        for day in item["hours"]:
            try:
                hrs = day["name"] + ": " + day["openHour"] + "-" + day["closeHour"]
            except:
                hours = day["name"] + ": Closed"
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs

        hours_of_operation = hours if hours else MISSING
        raw_address = item["fullAddress"]

        if store_number == "12019" and street_address == "23":
            street_address = street_address.replace("23", "23 E Main")

        if store_number == "11927" and street_address == "114":
            street_address = street_address.replace("114", "114 West County Center")

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
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
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
