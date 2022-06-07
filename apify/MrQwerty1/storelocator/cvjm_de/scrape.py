import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from tenacity import retry, stop_after_attempt, wait_fixed
from sglogging import sglog


def get_ids():
    ids = []
    r = session.get(
        "https://aktiv.cvjm.de/index/ajax-prefetch-organisations", headers=headers
    )
    js = r.json()
    for j in js:
        ids.append(j.get("id"))

    return ids


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def get_j(_id):
    data = {
        "clubId": _id,
        "ajax": "1",
    }
    r = session.post(api, headers=headers, data=data)
    logger.info(f"{_id}: {r}")
    j = r.json()

    return j


def get_data(store_number, sgw: SgWriter):
    j = get_j(store_number)
    location_name = j.get("clubname")
    source = j.get("html") or "<html>"
    tree = html.fromstring(source)
    line = tree.xpath("//div[@class='col-sm-6']/p[1]/text()")
    line = list(filter(None, [li.strip() for li in line]))
    raw_address = ", ".join(line)
    if len(line) == 1:
        street_address = SgRecord.MISSING
        postal = "".join(re.findall(r"\d{5}", raw_address))
        city = raw_address.replace(postal, "").strip()
    elif len(line) == 2:
        street_address = line.pop(0)
        zc = line.pop()
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
    else:
        street_address, city, postal = (
            SgRecord.MISSING,
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

    if "," in city:
        city = city.split(",")[0].strip()

    phone = "".join(
        tree.xpath(
            "//span[@class='glyphicon glyphicon-earphone']/following-sibling::text()[1]"
        )
    ).strip()
    latitude = j.get("lat")
    longitude = j.get("lng")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="DE",
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        raw_address=raw_address,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()
    logger.info(f"{len(ids)} IDs to crawl..")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    logger = sglog.SgLogSetup().get_logger(logger_name="cvjm.de")
    locator_domain = "https://www.cvjm.de/"
    page_url = "https://aktiv.cvjm.de/"
    api = "https://aktiv.cvjm.de/index/ajax-load-club"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
