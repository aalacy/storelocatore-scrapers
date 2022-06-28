from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog
from tenacity import stop_after_attempt, wait_fixed, retry


@retry(stop=stop_after_attempt(5), wait=wait_fixed(5))
def get_hours(_id):
    _tmp = []
    r = session.get(f"https://twomenandatruck.com/location-blocks/{_id}")
    log.info(f"{_id}: {r}")
    source = r.json().get("tmt_location_footer") or "<html>"
    tree = html.fromstring(source)
    divs = tree.xpath("//div[contains(@class, 'office-hours__item')]")

    for d in divs:
        day = "".join(d.xpath("./span[1]//text()")).strip()
        time = "".join(d.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    hours, ids = dict(), list()
    api = "https://twomenandatruck.com/feed/locations"
    r = session.get(api, headers=headers)
    js = r.json()["locations"]

    for j in js:
        ids.append(j.get("location_id"))

    log.info(f"{len(js)} URLs to crawl")
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_hours, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            _id = future_to_url[future]
            try:
                row = future.result()
                hours[_id] = row
            except Exception as e:
                log.info(f"{_id} failed, reason: {e}")
                pass

    for j in js:
        adr1 = j.get("address_street")
        adr2 = j.get("address_premise")
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("address_city")
        state = j.get("address_state_province")
        postal = j.get("address_postal_code")
        country_code = j.get("address_country")
        store_number = j.get("location_id")
        page_url = j.get("web_landing_page")
        location_name = f"Movers in {j.get('location_name')}, {state}"
        phone = j.get("phone_office")
        latitude = j.get("coordinates_latitude")
        longitude = j.get("coordinates_longitude")
        hours_of_operation = hours.get(store_number)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://twomenandatruck.com/"
    log = sglog.SgLogSetup().get_logger(logger_name="twomenandatruck.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
