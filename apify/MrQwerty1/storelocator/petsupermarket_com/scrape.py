from sgrequests import SgRequests
import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="petsupermarket.com")
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def get_ids(res):
    json_str = (
        '[{"type"'
        + res.split('"features":[{"type"')[1].split(']},"uiLocationsList"')[0]
        + "]"
    )
    json_res = json.loads(json_str)  # json_res is list and has all ids
    ids_list = []
    for obj in json_res:
        ids_list.append(str(obj["properties"]["id"]))

    ids = "%2C".join(ids_list)
    return ids


def fetch_data():
    search_url = "https://storelocator.petsupermarket.com/"
    search_res = session.get(search_url, headers=headers)
    ids = get_ids(search_res.text)

    locator_domain = "https://petsupermarket.com/"

    api_url = f"https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/ACdGkpGYCl9hdgJigx7fHE7Vx1Tujs/locations-details?locale=en_US&ids={ids}&clientId=5e3da261df2763dd5ce605ab&cname=storelocator.petsupermarket.com"
    r = session.get(api_url, headers=headers)
    js = r.json()["features"]
    for j in js:
        g = j["geometry"]["coordinates"]
        j = j["properties"]
        page_url = f"https://storelocator.petsupermarket.com/{j.get('slug')}"
        location_name = j.get("name")
        street_address = f"{j.get('addressLine1')} {j.get('addressLine2') or ''}"
        city = j.get("city")
        state = j.get("province")
        postal = j.get("postalCode")
        country_code = j.get("country")
        store_number = j.get("branch")
        phone = j.get("phoneLabel")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if g:
            latitude = g[1]
            longitude = g[0]

        hours = j.get("hoursOfOperation") or "<MISSING>"
        if hours == "<MISSING>":
            hours_of_operation = hours
        else:
            _tmp = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for d in days:
                try:
                    start = hours.get(d)[0][0]
                    close = hours.get(d)[0][1]
                    _tmp.append(f"{d}: {start} - {close}")
                except IndexError:
                    _tmp.append("Temporarily closed")
                    break

            hours_of_operation = ";".join(_tmp)

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
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
