import time
import json
import re
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import sglog


MISSING = SgRecord.MISSING
DOMAIN = "ferrari.com"
website = "https://www.ferrari.com/"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
}


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def fetchData():
    dataUrl = "https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D1%26idLayer%3DD%26licenza%3Dgeo-ferrarispa%26progetto%3DFerrari-Locator%26lang%3DALL&encoding=UTF-8"

    body = request_with_retries(dataUrl)
    rawData = "".join(re.findall("{.*}", str(body.text))).replace("\\", "")
    d = json.loads(rawData)
    j = d["L"][0]["O"]
    log.info(f"Total Locations: {len(j)}")
    for i in j:
        data = i["U"]
        try:
            page_url = data["URLSite"]
        except:
            page_url = MISSING
        try:
            store_number = i["D"]
            if store_number == "GHOST":
                continue
        except:
            store_number = MISSING
        try:
            location_type = data["DealerType"]
        except:
            location_type = MISSING
        try:
            location_name = data["Name"]
        except:
            location_name = MISSING
        try:
            street_address = data["Address"]
        except:
            street_address = MISSING
        try:
            country_code = data["Nation"]
        except:
            country_code = MISSING
        try:
            zip_postal = data["Zipcode"]
            if zip_postal == "-":
                zip_postal = MISSING
            elif zip_postal == "NA":
                zip_postal = MISSING
        except:
            zip_postal = MISSING
        try:
            city = data["Locality"]
        except:
            city = MISSING
        try:
            state = data["ProvinceState"].replace("0", MISSING)
            if state == "-":
                state = MISSING
        except:
            try:
                state = data["ProvinceStateExt"].replace("0", MISSING)
                if state == "-":
                    state = MISSING
            except:
                state = MISSING
        try:
            longitude = i["G"][0]["P"][0]["x"]
            log.info(f"Longitude: {longitude}")
            if longitude == "0.0":
                longitude = MISSING
                log.info(f"==>Longitude: {longitude}")
        except:
            longitude = MISSING
        try:
            latitude = i["G"][0]["P"][0]["y"].strip()
            log.info(f"Latitude: {latitude}")
            if latitude == str(0.0):
                latitude = MISSING
                log.info(f"==>Latitude: {latitude}")
        except:
            latitude = MISSING

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone="",
            location_type=location_type,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
            raw_address="",
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
