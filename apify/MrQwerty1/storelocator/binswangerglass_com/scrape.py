import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="binswangerglass.com")


def get_additional(page_url):
    r = session.get(page_url)
    log.info(f"Crawling: {page_url}, Status: {r.status_code}")

    if r.status_code == 404:
        return "", ("", "")

    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'LocalBusiness')]/text()"))
    j = json.loads(text)

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = str(h.get("dayOfWeek")).split("/")[-1]
        start = str(h.get("opens")).rsplit(":00", 1).pop(0)
        end = str(h.get("closes")).rsplit(":00", 1).pop(0)
        if start == "None":
            _tmp.append(f"{day}: Closed")
        else:
            _tmp.append(f"{day}: {start}-{end}")

    geo = j.get("geo") or {}
    lat = geo.get("latitude")
    lng = geo.get("longitude")

    return ";".join(_tmp), (lat, lng)


def fetch_data(sgw: SgWriter):
    for i in range(1, 5000):
        if i == 1:
            api = "https://www.binswangerglass.com/branch/"
        else:
            api = f"https://www.binswangerglass.com/branch/page/{i}/"

        r = session.get(api)
        log.info(f"Crawling: {api}, Status: {r.status_code}")
        tree = html.fromstring(r.text)

        divs = tree.xpath("//div[contains(@class, 'branch-locations')]")
        for d in divs:
            location_name = " ".join("".join(d.xpath(".//h2/a/text()")).split())
            store_number = location_name.split("#")[-1].strip()
            page_url = "".join(d.xpath(".//h2/a/@href"))
            line = d.xpath(".//h2/following-sibling::p/text()")
            line = list(filter(None, [l.strip() for l in line]))

            csz = line.pop()
            city = csz.split(",")[0].strip()
            csz = csz.split(",")[1].strip()
            postal = csz.split()[-1]
            state = csz.replace(postal, "").strip()
            street_address = ", ".join(line)

            phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            hours_of_operation, coords = get_additional(page_url)
            latitude, longitude = coords

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(divs) < 12:
            break


if __name__ == "__main__":
    locator_domain = "https://www.binswangerglass.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
