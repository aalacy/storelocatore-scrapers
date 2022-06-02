import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "hollisterco_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.hollisterco.com"
MISSING = SgRecord.MISSING


def fetch_locations(base_url, session):
    location_url = f"{base_url}/shop/ViewAllStoresDisplayView?storeId=11205&catalogId=10201&langId=-1"

    session.get(base_url, headers=headers)
    res = session.get(location_url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")
    links = soup.find("main", {"class": "all-stores"}).findAll("li")
    return [link.a["href"] for link in links]


def fetch_location(url, session):

    res = session.get(url, headers=headers)
    if res.status_code == 404:
        return None

    soup = BeautifulSoup(res.text, "lxml")

    return extract_data(soup)


def extract_data(soup):
    scripts = soup.find_all("script")

    for script in scripts:
        if script.string and "geoNodeUniqueId" in script.string:
            data = json.loads(
                script.string.split("try {digitalData.set('physicalStore',")[1].split(
                    ");}"
                )[0]
            )

            return data


def fetch_data():
    requests = SgRequests()
    links = fetch_locations(DOMAIN, requests)
    for link in links:
        page_url = f"{DOMAIN}{link}"
        log.info(page_url)
        data = fetch_location(page_url, requests)
        if not data:
            continue
        location_name = data["name"]
        street_address = data["addressLine"][0]
        city = data["city"]
        state = data["stateOrProvinceName"]
        zip_postal = data["postalCode"]
        if zip_postal == "-":
            zip_postal = MISSING
        country_code = data["country"]
        store_number = data["storeNumber"]
        phone = data["telephone"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        hours_of_operation = "<INACCESSIBLE>"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
