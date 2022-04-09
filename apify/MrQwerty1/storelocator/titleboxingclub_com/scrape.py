import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hours(page_url):
    r = session.get(page_url)
    if r.status_code == 410:
        return SgRecord.MISSING

    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'ExerciseGym')]/text()")
    ).replace("[ , ", "[")
    j = json.loads(text)

    _tmp = []
    hours = j.get("openingHours") or []
    for h in hours:
        h = h.strip()
        if len(h) != 2:
            _tmp.append(h)

    hours_of_operation = ";".join(_tmp)
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

    iscoming = tree.xpath("//span[@class='coming_soon']")
    if iscoming:
        hours_of_operation = "Coming Soon"

    return hours_of_operation


def fetch_data(sgw: SgWriter):
    api = "https://titleboxingclub.com/locations/"
    r = session.get(api)
    tree = html.fromstring(r.text)
    li = tree.xpath("//ul[@class='maplocationsectionbottom']/li")

    for l in li:
        location_name = "".join(
            l.xpath(".//h3[contains(@class, 'locationName')]/text()")
        ).strip()
        street_address = "".join(l.xpath(".//span[@itemprop='streetAddress']/text()"))
        city = "".join(l.xpath(".//span[@itemprop='addressLocality']/text()"))
        state = "".join(l.xpath(".//span[@itemprop='addressRegion']/text()"))
        postal = "".join(l.xpath(".//span[@itemprop='postalCode']/text()"))
        country = "US"
        if state == "MX":
            state = SgRecord.MISSING
            country = "MX"

        page_url = "".join(l.xpath(".//a[@class='btn primary-btn']/@href"))
        if not page_url:
            continue
        phone = "".join(l.xpath(".//span[@itemprop='telephone']/text()"))
        if phone.lower().find("text") != -1:
            phone = phone.lower().split("text")[-1].replace(":", "").strip()
        latitude = "".join(l.xpath("./@data-lat"))
        longitude = "".join(l.xpath("./@data-lon"))
        try:
            hours_of_operation = get_hours(page_url)
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://titleboxingclub.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
