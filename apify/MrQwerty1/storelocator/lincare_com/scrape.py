import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hours(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'generalHoursText')]/text()"))
    text = text.split('"data":')[1].split("},")[0] + "}"
    j = json.loads(text)
    day = j.get("generalHoursDaysText")
    inter = j.get("generalHoursText")

    return f"{day}: {inter}"


def fetch_data(sgw: SgWriter):
    api = "https://www.lincare.com/api/LocationSearch/LocationSearch?skip=0&take=1000"
    r = session.get(api, headers=headers)
    js = r.json()["documents"]

    s = js[0].get("LocationDetailPageLink")
    url = f"https://www.lincare.com{s}"
    hours_of_operation = get_hours(url)

    for j in js:
        adr1 = j.get("Address1") or ""
        adr2 = j.get("Address2") or ""
        if "box" in adr2.lower() or "white" in adr2.lower():
            adr2 = ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        country_code = "US"
        store_number = j.get("Id")
        name = j.get("Name") or ""
        part = j.get("MarketingName") or ""
        location_name = f"{name} - {part}"
        slug = j.get("LocationDetailPageLink")
        page_url = f"https://www.lincare.com{slug}"
        phone = j.get("Phone")
        latitude = j.get("Lat")
        longitude = j.get("Lon")

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.lincare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
