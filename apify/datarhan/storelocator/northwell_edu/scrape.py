import json
from lxml import etree
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="northwell_edu")


start_url = "https://www.northwell.edu/api/locations/108781?browse_all=true"


hdr = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}


def get_api_urls():
    with SgRequests() as http:
        response = http.get(start_url, headers=hdr)
        logger.info(f"Pulling API Endpoin URLs[HTTP {response.status_code} OK!]")
        logger.info(f"Source: {response.text}")
        data = json.loads(response.text)
        start = int(data["showing"].get("start"))
        total = data["showing"].get("total")
        pagination = data["pagination"]
        end = pagination.get("8").get("url_page")
        logger.info(f"Start: {start} | End: {end} | Total: {total}")
        api_urls = [
            f"https://www.northwell.edu/api/locations/108781?browse_all=true&user_filtered=true&page={pgnum}"
            for pgnum in range(start, end + 1)
        ]
        return api_urls


def get_data_from_api_response():
    api_urls = get_api_urls()
    results = []
    for urlnum, api_url in enumerate(api_urls[0:]):
        logger.info(f"[{urlnum}] PullingFrom [ {api_url} ]")
        with SgRequests() as http:
            response = http.get(api_url, headers=hdr)
            data = json.loads(response.text)
            dr = data["results"]
            results.extend(dr)
    logger.info(f"Total Stores Found: {len(results)}")
    return results


def fetch_data():
    all_poi = get_data_from_api_response()
    for poinum, poi in enumerate(all_poi[0:]):
        with SgRequests() as session:
            store_url = poi.get("page_url")
            if store_url:
                if "https" not in store_url:
                    store_url = "https:" + store_url
            logger.info(f"[{poinum}] Pulling the data for {store_url}")
            location_name = poi.get("title")
            street_address = poi.get("street")
            if street_address:
                if poi.get("suite"):
                    street_address += ", " + poi["suite"]
            city = poi.get("city")
            state = poi.get("state")
            zip_code = poi.get("zip")
            phone = poi.get("phone")
            geo_data = poi.get("map")
            latitude = ""
            longitude = ""
            if geo_data:
                geo = geo_data.split("center=")[-1].split("&")[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
                if latitude == "-10":
                    latitude = ""
                    longitude = ""

            store_response = session.get(store_url, headers=hdr)
            hours_of_operation = ""
            if store_response.status_code == 200:
                store_dom = etree.HTML(store_response.text)
                hours_of_operation = store_dom.xpath(
                    '//div[contains(@class, "card__hours")]/table//text()'
                )
                hours_of_operation = " ".join(
                    [elem.strip() for elem in hours_of_operation if elem.strip()][2:]
                )

            item = SgRecord(
                locator_domain="northwell.edu",
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="US",
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
