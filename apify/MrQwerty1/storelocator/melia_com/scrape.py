import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog
from tenacity import retry, stop_after_attempt, wait_fixed


def get_ids():
    r = session.get("https://www.melia.com/rest/hotels/destinations-tree?lang=en")

    return set(re.findall(r'"hotelCode":"(.*?)"', r.text))


@retry(stop=stop_after_attempt(8), wait=wait_fixed(5))
def get_j(_id):
    api = f"https://www.melia.com/rest/hotels/hotel-sheet/{_id}/en"
    r = session.get(api, headers=headers)
    if r.status_code != 200:
        logger.info(f"{api}: {r.status_code}")
        raise Exception

    return r.json()["hotel"]["hotelSection"]


def get_data(store_number, sgw: SgWriter):
    j = get_j(store_number)
    location_name = j.get("title")
    street_address = j.get("address") or ""
    street_address = " ".join(street_address.split())
    city = j.get("location") or ""
    country_code = j.get("countryCode")
    if not country_code and "Vietnam" in city:
        country_code = "VN"
    if not street_address and "," in city:
        street_address = city.split(",")[0].strip()
        city = city.split(",")[1].strip()
    if "," in city:
        city = city.split(",")[0].strip()
    postal = j.get("postalCode")
    phone = j.get("phoneContact") or ""
    black_list = ["Fast", ";", "-", "/"]
    for b in black_list:
        if b in phone:
            phone = phone.split(b)[0].strip()

    latitude = j.get("latitudeCoordinates")
    longitude = j.get("longitudeCoordinates")
    slug = j.get("url")
    page_url = f"https://www.melia.com{slug}"

    location_type = SgRecord.MISSING
    cats = j.get("categories") or []
    for c in cats:
        if c.get("type") == "Marca":
            location_type = c.get("title")
            break

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        location_type=location_type,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.melia.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="melia")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
