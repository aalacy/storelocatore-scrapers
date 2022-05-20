from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ohiomulch.com/"
    api_url = "https://www.ohiomulch.com/apps/store-locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="addresses"]/ul/li')
    for d in div:

        page_url = "https://www.ohiomulch.com/apps/store-locator"
        location_name = (
            "".join(d.xpath('.//span[@class="name"]/text()')).strip() or "<MISSING>"
        )
        street_address = (
            "".join(d.xpath('.//span[@class="address"]/text()')).strip() or "<MISSING>"
        )
        state = (
            "".join(d.xpath('.//span[@class="prov_state"]/text()')).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath('.//span[@class="postal_zip"]/text()')).strip()
            or "<MISSING>"
        )
        country_code = "US"
        city = "".join(d.xpath('.//span[@class="city"]/text()')).strip() or "<MISSING>"
        latitude = (
            "".join(
                d.xpath(
                    f'.//preceding::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[0]
            .split("lat:")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    f'.//preceding::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[0]
            .split("lng:")[-1]
            .split(",")[0]
            .strip()
        )

        phone = (
            "".join(d.xpath('.//span[@class="phone"]/text()')).strip() or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//span[@class="hours"]//text()'))
            .replace("\n", "")
            .replace("Hours", "")
            .replace("Open", "")
            .strip()
            or "<MISSING>"
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
