from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import tenacity
from tenacity import retry, stop_after_attempt
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="slugandlettuce_co_uk")
MISSING = SgRecord.MISSING
DOMAIN = "slugandlettuce.co.uk"
MAX_WORKERS = 5

headers = {
    "accept": "*/*",
    "referer": "https://www.slugandlettuce.co.uk/find-a-bar",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        logger.info(f"Pulling the data from: {url}")
        r = http.get(url, headers=headers)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{url} >> Temporary Error: {r.status_code}")


global store_urls
store_urls = set()


def fetch_records(postcode, sgw: SgWriter):
    global store_urls
    s = SgRequests()
    postcode = postcode.replace(" ", "")
    logger.info(f"Pulling from the PostCode: {postcode}")
    apieurl = f"https://www.slugandlettuce.co.uk/heremapssearch?postcode={postcode}"
    r = s.post(apieurl, headers=headers)
    json_data = r.json()

    if "mapPoints" not in json_data:
        return
    else:

        mpoints = json_data["mapPoints"]
        logger.info(
            f"Number of Stores Found: {len(mpoints)} at postcode of << {postcode} >>"
        )
        for _ in mpoints:
            page_url = _["UrlText"]
            hours_of_operation = ""
            if page_url:
                page_url = f"https://www.slugandlettuce.co.uk/{page_url}"
            else:
                page_url = MISSING
            if page_url not in store_urls:
                r1 = get_response(page_url)
                sel = html.fromstring(r1.text, "lxml")
                hoo = sel.xpath(
                    '//h2[contains(text(), "Opening Times")]/following-sibling::div//text()'
                )
                hoo = [elem.strip() for elem in hoo if elem.strip()]
                hours_of_operation = " ".join(hoo) if hoo else MISSING
            else:
                pass
            store_urls.add(page_url)
            sta = ""
            sta1 = _["Address1"]
            sta2 = _["Address2"]
            if sta1 and sta2:
                sta = sta1 + ", " + sta2
            elif sta1 and not sta2:
                sta = sta1
            elif not sta1 and sta2:
                sta = sta2
            else:
                sta = MISSING
            a1 = _["Address1"] or "<MISSING>"
            a2 = _["Address2"] or "<MISSING>"
            tc = _["TownCity"] or "<MISSING>"
            pc = _["PostCode"] or "<MISSING>"
            ra = f"{a1} {a2}, {tc}, {pc}"
            ra1 = ra.replace("<MISSING>", "")
            ra2 = ra1.split(",")
            ra3 = [" ".join(i.split()) for i in ra2]
            ra4 = [i for i in ra3 if i]
            ra5 = ", ".join(ra4)

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=_["UnitName"] or MISSING,
                street_address=sta,
                city=_["TownCity"] or MISSING,
                state=_["County"] or MISSING,
                zip_postal=_["PostCode"] or MISSING,
                country_code="GB",
                store_number=_["id"] or MISSING,
                phone=_["Telephone"],
                location_type=MISSING,
                latitude=_["lat"] or MISSING,
                longitude=_["lng"] or MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=ra5,
            )
            sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=50,
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [executor.submit(fetch_records, postcode, sgw) for postcode in search]
        tasks.extend(task)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:

        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
