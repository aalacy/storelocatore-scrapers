from sgzip.dynamic import SearchableCountries, DynamicZipSearch, Grain_1_KM
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog
import time
from tenacity import retry, stop_after_attempt
import tenacity
import random

locator_domain = "abbeycarpet.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(api_url):
    with SgRequests() as http:
        response = http.get(api_url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            log.info(f"HTTP STATUS Return: {response.status_code}")
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def get_data(zipps, sgw: SgWriter):

    api_url = (
        f"https://www.abbeycarpet.com/storelocator.aspx?&searchZipCode={str(zipps)}"
    )

    r = get_response(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "results-address")]')
    if div:
        log.debug(f"From {zipps} stores = {len(div)}")

        for d in div:

            page_url = api_url
            location_name = "".join(d.xpath("./p[1]/text()")) or "<MISSING>"
            street_address = "".join(d.xpath("./p[2]/text()")) or "<MISSING>"
            ad = "".join(d.xpath("./p[3]/text()"))
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[0].strip()
            country_code = "US"
            phone = "".join(d.xpath("./p[4]/text()")) or "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    postals = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=10,
        expected_search_radius_miles=10,
        granularity=Grain_1_KM(),
        max_search_results=5,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in postals}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
