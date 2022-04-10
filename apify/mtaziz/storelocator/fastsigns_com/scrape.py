from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("fastsigns_com")
LOCATOR_URL = "https://www.fastsigns.com/locations"
DOMAIN = "fastsigns.com"
MAX_WORKERS = 10
MISSING = SgRecord.MISSING
headers_c = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Host": "www.fastsigns.com",
    "Origin": "https://www.fastsigns.com",
    "Referer": "https://www.fastsigns.com/locations/",
}


def get_hours(page_url_):
    with SgRequests() as s1:
        rpg = s1.get(page_url_, headers=headers_c)
        data_app_json = html.fromstring(rpg.text, "lxml")
        hours_popup = data_app_json.xpath(
            '//*[@id="OfficeInfo_ExtendedHours"]/div[@class="popup"]/ul/li'
        )
        hours_ = []
        for hpop in hours_popup:
            dtime = hpop.xpath(".//text()")
            dtime1 = [" ".join(i.split()) for i in dtime]
            dtime2 = " ".join([i for i in dtime1 if i])
            hours_.append(dtime2)
        hoo = "; ".join(hours_)
        return hoo


def fetch_records(storenum, _, sgw: SgWriter):
    purl = _["page_url"]
    logger.info(f"[{storenum}] Pulling the hours from {purl}")
    hours_of_operation = get_hours(purl)
    if "Coming Soon" in _["hours_of_operation"]:
        hours_of_operation = "Coming Soon"
    item = SgRecord(
        locator_domain=DOMAIN,
        page_url=purl,
        location_name=_["location_name"],
        street_address=_["street_address"],
        city=_["city"],
        state=_["state"],
        zip_postal=_["zip"],
        country_code=_["country_code"],
        store_number=_["store_number"],
        phone=_["phone"],
        location_type=_["location_type"],
        latitude=_["latitude"],
        longitude=_["longitude"],
        hours_of_operation=hours_of_operation,
        raw_address=_["raw_address"],
    )
    sgw.write_row(item)


def get_data():
    with SgRequests() as s:
        api_endpoint_url = "https://www.fastsigns.com/locations/?CallAjax=GetLocations"
        payload = {"CallAjax": "GetLocations"}
        jsp = s.post(api_endpoint_url, data=json.dumps(payload), headers=headers_c)
        js = jsp.json()
        items = []
        for idx, _ in enumerate(js[0:]):
            web = "https://www.fastsigns.com"
            page_url = ""
            path = _["Path"]
            if path:
                page_url = web + path
            logger.info(f"[{idx}] Pulling data for {page_url}")
            add1 = _["Address1"]
            add2 = _["Address2"]
            sta = ""
            if add1 and not add2:
                sta = add1
            elif add1 and add2:
                sta = add1 + ", " + add2
            elif not add1 and add2:
                sta = add2
            else:
                sta = ""
            cs = _["ComingSoon"]
            hoo_comingsoon_status = ""
            if cs == 1:
                hoo_comingsoon_status = "Coming Soon"

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=_["FranchiseLocationName"],
                street_address=sta,
                city=_["City"],
                state=_["State"],
                zip_postal=_["ZipCode"],
                country_code=_["Country"],
                store_number=_["FranchiseLocationID"],
                phone=_["Phone"],
                location_type=_["LocationType"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                hours_of_operation=hoo_comingsoon_status,
                raw_address=sta,
            )
            items.append(item.as_dict())
        return items


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    data_without_hours = get_data()
    logger.info("Pulling Data without Hours Finished!!")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [
            executor.submit(fetch_records, storenum, store_data, sgw)
            for storenum, store_data in enumerate(data_without_hours[0:])
        ]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
