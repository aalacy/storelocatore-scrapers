from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt
import json
from lxml import html


logger = SgLogSetup().get_logger("_com")
locator_domain = "burgerking.com.pk"
API_URL = "https://bkdelivery.pk/"
MISSING = SgRecord.MISSING
headers = {
    "accept": "application/json, text/plain, */*",
    "Host": "bkdelivery.pk",
    "Referer": "https://bkdelivery.pk/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


@retry(stop=stop_after_attempt(3))
def fetch_res(http, url):
    r = http.get(url, headers=headers)
    return r


def fetch_records(http: SgRequests):
    res = fetch_res(http, API_URL)
    tree = html.fromstring(res.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var cityData = ")]/text()'))
        .split("var cityData = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    cities = list(js.keys())
    for city in cities:
        for item in js[city]:
            page_url = "https://bkdelivery.pk/"
            location_name = "".join(item.get("area_name")) + ", " + city
            country_code = "Pakistan"
            latitude = item.get("lat")
            latitude = latitude if latitude else MISSING
            longitude = item.get("lng")
            longitude = longitude if longitude else MISSING
            store_number = item.get("id")

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=MISSING,
                city=city,
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=store_number,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
                raw_address=location_name,
            )


def scrape():
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
