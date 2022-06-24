import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.mamafus.com/locations"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//h4")

    cnt = 0
    for d in divs:
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line.pop(0)
        phone = line.pop()

        csz = line.pop()
        street_address = ", ".join(line)
        city = csz.split(", ")[0]
        csz = csz.split(", ")[1]
        state, postal = csz.split()

        text = tree.xpath("//div/@data-block-json")[cnt]
        cnt += 1

        j = json.loads(text)["location"]
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mamafus.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
