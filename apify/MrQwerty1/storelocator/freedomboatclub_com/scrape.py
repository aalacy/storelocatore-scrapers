from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_phone(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    phones = tree.xpath(
        "//a[contains(@href, 'tel:')]/text()|//div[@class='col-md-4']//h6//text()"
    )
    for p in phones:
        if not p.strip():
            continue
        if p.strip()[0].isdigit() or p.strip()[0] == "(":
            return p.strip()
    return SgRecord.MISSING


def fetch_data(sgw: SgWriter):
    api = "https://www.freedomboatclub.com/bcom/LocationsDataServlet.json?unit=mi&size=1000&currentPagePath=/content/brunswick/fbc/na/us/en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()["results"]

    for j in js:
        location_name = j.get("title")
        page_url = j.get("url") or ""
        street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = j.get("country")
        try:
            phone = get_phone(page_url)
        except:
            phone = SgRecord.MISSING

        try:
            latitude, longitude = j.get("location").split(",")
        except:
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.freedomboatclub.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
