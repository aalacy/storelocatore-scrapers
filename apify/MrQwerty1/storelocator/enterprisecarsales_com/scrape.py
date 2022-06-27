import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.enterprisecarsales.com/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'rooftops:')]/text()"))
    text = text.split("rooftops:")[1].split("}]}],")[0].strip() + "}]}]"
    js = json.loads(text)

    for j in js:
        a = j.get("Location") or {}
        adr1 = a.get("Address1") or ""
        adr2 = a.get("Address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("City")
        state = a.get("State")
        postal = a.get("Zipcode")
        country_code = "US"
        store_number = j.get("Code") or ""
        if store_number == "Yes":
            continue
        location_name = j.get("Name")
        page_url = f"https://www.enterprisecarsales.com/location/{store_number}/"
        phone = a.get("ContactNumber")
        latitude, longitude = (a.get("LatLon") or ",").split(",")

        _tmp = []
        s = j.get("Store") or {}
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            start = s.get(f"{day}Open")
            end = s.get(f"{day}Close")
            if start == end and start:
                _tmp.append(f"{day}: Closed")
            elif not start:
                continue
            else:
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
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.enterprisecarsales.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
