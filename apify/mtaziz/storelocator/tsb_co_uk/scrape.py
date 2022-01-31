from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
import html
from tenacity import retry, stop_after_attempt
import tenacity


logger = SgLogSetup().get_logger("tsb_co_uk")
URL_BRANCH_LOCATOR = "http://www.tsb.co.uk/branch-locator/"
DOMAIN = "tsb.co.uk"
MISSING = SgRecord.MISSING
headers_tsb = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(10))
def get_response(url):
    with SgRequests() as http:
        logger.info(f"Pulling the data from: {url}")
        r = http.post(url, headers=headers_tsb)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{url} >> Temporary Error: {r.status_code}")


def get_hours(data_hours):
    hours_of_operation = ""
    tue = (
        "Tuesday:"
        + " "
        + data_hours["tuesOpen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["tuesClose"].rstrip("00").rstrip(":")
    )
    wed = (
        "Wednesday:"
        + " "
        + data_hours["wedsopen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["wedsClose"].rstrip("00").rstrip(":")
    )
    thu = (
        "Thursday:"
        + " "
        + data_hours["thursOpen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["thursClose"].rstrip("00").rstrip(":")
    )
    fri = (
        "Friday:"
        + " "
        + data_hours["friOpen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["friClose"].rstrip("00").rstrip(":")
    )
    sat = (
        "Saturday:"
        + " "
        + data_hours["satOpen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["satClose"].rstrip("00").rstrip(":")
    )
    if "- - -" in sat:
        sat = "Closed"
    sun = "Sunday:" + " " + "Closed"
    mon = (
        "Monday:"
        + " "
        + data_hours["monOpen"].rstrip("00").rstrip(":")
        + " - "
        + data_hours["monClose"].rstrip("00").rstrip(":")
    )
    hours_of_operation = f"{tue}; {wed}; {thu}; {fri}; {sat}; {sun}; {mon}"
    hours_of_operation = hours_of_operation.replace("- - -", "Closed")
    return hours_of_operation


def fetch_data():
    s = set()
    url = "https://www.tsb.co.uk/sites/Satellite?c=Page&pagename=public%2FseBranchLocator&longitude=-4.3878&latitude=56.5685&filter=null&numBranches=1&rows=1000&isAppend=false"
    r = get_response(url)
    text = html.unescape(r.content.decode("unicode-escape"))
    sp1 = text.split("jsonBranches = ")[-1]
    sp2 = sp1.split(";")[0]
    sp3 = sp2.replace("'", "")
    sp4 = json.loads(sp3)
    all_branches = sp4["branches"]
    logger.info(f"Total Number of Branches found: {len(all_branches)}")
    for idx, data in enumerate(all_branches):
        locator_domain = DOMAIN
        slug = data["branchLocationNormalization"]
        if slug:
            page_url = f"{URL_BRANCH_LOCATOR}{slug}"
        else:
            page_url = MISSING

        location_name = data["branchLocation"]
        location_name = " ".join(location_name.split())
        location_name = location_name.replace("Bo ess", "Boness")
        location_name = (
            location_name.encode("unicode-escape").decode("utf8").replace("\\\\", "")
        )
        location_name = location_name if location_name else MISSING

        street_address = data["branchAddrLine1"]
        street_address = (
            street_address.encode("unicode-escape").decode("utf8").replace("\\\\", "")
        )
        street_address = street_address if street_address else MISSING

        city = data["branchTown"]
        city = city.encode("unicode-escape").decode("utf8").replace("\\\\", "")
        city = city if city else MISSING

        state = data["branchAddrLine4"]
        state = state if state else MISSING

        zip_postal = data["branchPostCode"]
        zip_postal = zip_postal if zip_postal else MISSING

        country_code = "GB"
        store_number = data["sortCode"]
        if store_number in s:
            continue
        s.add(store_number)
        store_number = store_number if store_number else MISSING

        phone = data["telNumFull"]
        phone = phone if phone else MISSING

        location_type = MISSING
        latitude = data["postcodeLatitude"]
        latitude = latitude if latitude else MISSING

        longitude = data["postcodeLongitude"]
        longitude = longitude if longitude else MISSING

        hours_of_operation = get_hours(data)
        raw_address = data["fullBranchDirection"]
        raw_address = " ".join(raw_address.split())
        raw_address = (
            raw_address.encode("unicode-escape").decode("utf8").replace("\\\\", "")
        )
        raw_address = raw_address if raw_address else MISSING
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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
