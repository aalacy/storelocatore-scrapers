import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        return {}
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'pageContext =')]/text()")
    ).strip()
    text = text.split("pageContext =")[1].replace(";", "")
    j = json.loads(text)["analytics"]["store"]

    return j


def fetch_data(sgw: SgWriter):
    api = "https://www.hunkemoller.com/on/demandware.store/Sites-hunkemoller-us-Site/en_US/Stores-GetStoresJSON"
    r = session.get(api, headers=headers)
    text = r.text.replace("][", ",")
    js = json.loads(text)

    for j in js:
        slug = j.get("storeUrlPath")
        page_url = f"https://www.hunkemoller.com/stores{slug}"

        a = get_additional(page_url)
        location_name = j.get("name")
        adr1 = j.get("address") or ""
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("State")
        postal = a.get("postalCode")
        country_code = a.get("addressCountry")

        phone = a.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("openingHours") or []
        for h in hours:
            day = h.get("dayOfWeek")
            start = h.get("open")
            end = h.get("close")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hunkemoller.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
