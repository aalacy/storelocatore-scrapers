import json
from urllib.parse import unquote
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://good2gostores.com/locations/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//div[@data-elfsight-google-maps-options]/@data-elfsight-google-maps-options"
        )
    )
    js = json.loads(unquote(text))["markers"]

    for j in js:
        location_name = j.get("infoTitle") or ""
        store_number = location_name.split("#")[-1]
        raw_address = j.get("position") or ""
        line = raw_address.split(", ")
        state, postal = line.pop().split()
        city = line.pop()
        street_address = ", ".join(line)
        if not street_address:
            street_address = " ".join(city.split()[:-2])
            city = " ".join(city.split()[-2:])
        phone = j.get("infoPhone")
        geo = j.get("coordinates") or ""
        latitude, longitude = geo.split(", ")
        hours_of_operation = j.get("infoWorkingHours") or ""
        if "Fuel Pumps" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Fuel Pumps")[0].strip()
        if hours_of_operation.endswith(","):
            hours_of_operation = hours_of_operation[:-1]

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
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://good2gostores.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
