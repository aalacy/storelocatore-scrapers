import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.wirelesswave.ca/en/locations/"
    r = session.get(api)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'page.locations =')]/text()"))
    text = text.split("page.locations =")[1].split(";")[0].strip()
    js = json.loads(text)

    for j in js:
        adr1 = j.get("Address") or ""
        adr2 = j.get("Address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("City")
        state = j.get("ProvinceAbbrev")
        postal = j.get("PostalCode")
        country_code = j.get("CountryCode")
        store_number = j.get("LocationId")
        page_url = f"https://www.wirelesswave.ca/en/locations/{store_number}/"
        location_name = " ".join(str(j.get("Name")).replace("WW ", "").split()[:-2])
        phone = j.get("Phone")
        latitude = j.get("Google_Latitude")
        longitude = j.get("Google_Longitude")

        _tmp = []
        hours = j.get("HoursOfOperation") or []
        for h in hours:
            day = h.get("DayOfWeek")
            start = h.get("Open")
            end = h.get("Close")
            if start and end:
                start, end = str(start).zfill(4), str(end).zfill(4)
                _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")
            else:
                _tmp.append(f"{day}: Closed")

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
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.wirelesswave.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
