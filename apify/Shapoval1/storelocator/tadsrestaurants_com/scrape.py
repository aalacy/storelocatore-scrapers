import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    page_url = "https://tadsrestaurants.com/visit"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col sqs-col-3 span-3"]')
    for d in div:

        location_name = "".join(d.xpath(".//h2/text()"))
        ll = "".join(d.xpath(".//div/@data-block-json"))
        js = json.loads(ll)
        street_address = js.get("location").get("addressLine1")

        state = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/h3[3]/text()'))
            .split(",")[1]
            .strip()
        )
        postal = "".join(js.get("location").get("addressLine2")).split()[-1].strip()

        country_code = "USA"
        city = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/h3[3]/text()'))
            .split(",")[0]
            .strip()
        )

        latitude = js.get("location").get("mapLat")
        longitude = js.get("location").get("mapLng")
        phone = "".join(d.xpath(".//p/text()"))
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/following::p[contains(text(), "Katy, Tomball, and College Station:")]/text()'
                )
            )
            .replace("Katy, Tomball, and College Station:", "")
            .strip()
        )
        if location_name.find("Lake Charles") != -1:
            hours_of_operation = (
                "".join(
                    d.xpath('.//following::p[contains(text(), "Lake Charles:")]/text()')
                )
                .replace("Lake Charles:", "")
                .strip()
            )

        close = (
            "".join(d.xpath('.//following::p[contains(text(), "KITCHENS")]/text()'))
            .replace("KITCHENS AT ALL LOCATIONS CLOSE AT", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.replace("am", f"am to {close}")

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
    locator_domain = "https://tadsrestaurants.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
