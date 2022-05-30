import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chargeyourcar.org.uk/"
    api_url = "https://m.chargeyourcar.org.uk/api/chargepoints/search?location="
    with SgFirefox() as driver:
        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = "".join(tree.xpath("//*//text()"))
        js = json.loads(div)
        for j in js["chargePoints"]:
            store_number = j.get("bayNo")
            page_url = f"https://m.chargeyourcar.org.uk/chargePoint?bayNo={store_number}&referrer=&scheme=default&mapHeight=500&mapZoom=16"
            location_name = j.get("siteName")
            location_type = j.get("chargerType")
            street_address = f"{j.get('address1')} {j.get('address2')}".strip()
            postal = j.get("postcode")
            country_code = "UK"
            city = j.get("city")
            latitude = j.get("lat")
            longitude = j.get("lon")

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=SgRecord.MISSING,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
