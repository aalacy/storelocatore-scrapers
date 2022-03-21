import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    page_url = "https://www.renspets.com/store_locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    block = "".join(tree.xpath('//div[@class="store-results-map"]/@data-google-map'))
    js = json.loads(block)
    for j in js["locations"]:
        a = j.get("address")
        location_name = "".join(j.get("name"))
        street_address = f"{a.get('street')} {a.get('street_2')}"
        city = a.get("city")
        state = a.get("region")
        country_code = a.get("country")
        postal = a.get("postal_code")
        latitude = j.get("coordinates")[1]
        longitude = j.get("coordinates")[0]
        try:
            hours_of_operation = (
                "".join(j.get("description"))
                .replace("<br>", " ")
                .replace("<div> </div>", "")
                .replace("<p>", "")
                .replace("</p>", "")
            )
        except:
            hours_of_operation = "<MISSING>"
        phone = a.get("phone_number") or "<MISSING>"
        if location_name.find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.renspets.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
