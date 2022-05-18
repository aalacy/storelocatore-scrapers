from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.parkview.com/_services/LocationsService.asmx/GetLocations"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    js = tree.xpath("//location")

    for j in js:
        location_name = "".join(j.xpath("./name/text()"))
        adr1 = "".join(j.xpath("./address1/text()"))
        adr2 = "".join(j.xpath("./address2/text()"))
        street_address = f"{adr1} {adr2}".strip()
        city = "".join(j.xpath("./city/text()"))
        state = "".join(j.xpath("./state/text()"))
        postal = "".join(j.xpath("./zip/text()"))
        country_code = "US"
        store_number = "".join(j.xpath("./id/text()"))
        page_url = f"https://www.parkview.com/locations/location-details?location={store_number}"
        phone = "".join(j.xpath("./phone/text()"))
        latitude = "".join(j.xpath("./latitude/text()"))
        longitude = "".join(j.xpath("./longitude/text()"))

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.parkview.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
