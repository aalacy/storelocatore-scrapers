from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.fairweatherclothing.com"
    api_url = "https://cdn.shopify.com/s/files/1/0047/1118/6550/t/32/assets/sca.storelocatordata.json?v=1648581124&formattedAddress=&boundsNorthEast=&boundsSouthWest=&_=1649841551136"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()
    for j in js:

        page_url = "https://www.fairweatherclothing.com/pages/store-locator"
        location_name = j.get("description")
        street_address = j.get("address")
        phone = j.get("phone")
        city = j.get("city")
        state = j.get("state")
        country_code = j.get("country")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = j.get("name")
        hours_of_operation = "<MISSING>"
        hours = j.get("schedule")
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        postal = j.get("postal")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
