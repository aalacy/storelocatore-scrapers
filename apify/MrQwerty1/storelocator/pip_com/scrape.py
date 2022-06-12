from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath("//div[@class='c-cta-row__hours-row']/text()")
    for h in hours:
        if not h.strip() or "appointment" in h.lower() or "Fall" in h:
            continue
        _tmp.append(h.strip())

    return ";".join(_tmp)


def get_number(slug):
    _tmp = []
    for s in slug:
        if s.isdigit():
            _tmp.append(s)

    return "".join(_tmp)


def fetch_data(sgw: SgWriter):
    data = '{"Input":"75022","TopN":-1,"Radius":5000,"Page":1}'
    r = session.post("https://pip.com/api/location/search", headers=headers, data=data)
    js = r.json()["results"]

    for j in js:
        slug = j.get("locationId") or ""
        store_number = get_number(slug)
        c = j.get("coordinate") or {}
        latitude = c.get("lat")
        longitude = c.get("lng")
        page_url = f"{locator_domain}{slug}"
        phone = j.get("phone")
        street_address = f'{j.get("address1")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        location_name = f"PIP {city}"
        try:
            hours_of_operation = get_hoo(page_url)
        except:
            hours_of_operation = SgRecord.MISSING

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


if __name__ == "__main__":
    locator_domain = "https://pip.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://pip.com/find-a-location?location=75022",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://pip.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
