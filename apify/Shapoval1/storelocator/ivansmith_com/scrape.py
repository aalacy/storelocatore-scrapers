from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ivansmith.com/"
    api_url = "https://www.ivansmith.com/location.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="StoreAddress"]')
    for d in div:

        page_url = "https://www.ivansmith.com/location.html"
        location_name = "".join(d.xpath('.//span[@class="location-name"]//text()'))
        street_address = "".join(d.xpath('.//span[@itemprop="streetAddress"]/text()'))
        state = "".join(d.xpath('.//span[@itemprop="addressRegion"]/text()'))
        postal = "".join(d.xpath('.//span[@itemprop="postalCode"]/text()'))
        country_code = "US"
        city = "".join(d.xpath('.//span[@itemprop="addressLocality"]/text()'))
        phone = "".join(d.xpath('.//span[@itemprop="telephone"]//text()'))
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/strong[contains(text(), "Store Hours")]/following-sibling::text()'
                )
            )
            .replace("\r\n", " ")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        ll = (
            "".join(
                d.xpath(
                    '//preceding::script[contains(text(), "directionsDisplay.setPanel")]/text()'
                )
            )
            .split(
                'directionsDisplay.setPanel(document.getElementById("directionsPanel"));'
            )[1]
            .split("addMarker")
        )
        latitude = (
            "".join(ll)
            .split(f"{location_name}")[0]
            .split("(")[-1]
            .split(",")[0]
            .replace("'", "")
            .strip()
        )
        longitude = (
            "".join(ll)
            .split(f"{location_name}")[0]
            .split("(")[-1]
            .split(",")[1]
            .replace("'", "")
            .strip()
        )

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
