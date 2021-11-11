from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.link.nyc/"
    api_url = "https://www.link.nyc/map/LinkNYC.kml?cacheBuster=983495891"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//name")
    for d in div:

        page_url = "https://www.link.nyc/find-a-link.html"
        location_name = (
            "".join(d.xpath(".//text()")).replace("&amp;", "&") or "<MISSING>"
        )
        street_address = (
            "".join(d.xpath(".//following-sibling::address/text()")) or "<MISSING>"
        )
        country_code = "US"
        city = (
            "".join(d.xpath(".//following-sibling::phonenumber/text()")) or "<MISSING>"
        )
        latitude = (
            "".join(d.xpath(".//following-sibling::point/coordinates/text()"))
            .split(",")[1]
            .strip()
            or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//following-sibling::point/coordinates/text()"))
            .split(",")[0]
            .strip()
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
