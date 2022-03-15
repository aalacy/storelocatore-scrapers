import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.highlandparkmarket.com"
    api_url = "https://www.highlandparkmarket.com/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div[@data-block-json]]")
    for d in div:
        ll = "".join(d.xpath(".//div/@data-block-json"))
        js = json.loads(ll)
        page_url = "https://www.highlandparkmarket.com/contact"
        location_name = "".join(d.xpath(".//preceding::h2[1]/text()"))
        street_address = "".join(
            d.xpath(".//preceding::h2[1]/following-sibling::p[1]/text()[1]")
        )
        ad = (
            "".join(d.xpath(".//preceding::h2[1]/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = js.get("location").get("mapLat")
        longitude = js.get("location").get("mapLng")
        phone = (
            " ".join(d.xpath('.//preceding::p[contains(text(), "Manager")][1]//text()'))
            .replace("\n", "")
            .split("Telephone:")[1]
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//preceding::p[contains(text(), "Manager")][1]//text()'))
            .replace("\n", "")
            .split("Store Hours:")[1]
            .split("Tel")[0]
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
