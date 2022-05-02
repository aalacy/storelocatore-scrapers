import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nmb-t.com/"
    api_url = "https://www.nmb-t.com/locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "location-item")]')
    for d in div:

        page_url = "https://www.nmb-t.com/locations"
        location_name = "".join(d.xpath(".//div[2]//h3/text()"))
        street_address = (
            "".join(d.xpath('.//div[@class="thoroughfare"]/text()'))
            + " "
            + "".join(d.xpath('.//div[@class="premise"]/text()'))
        )
        city = "".join(d.xpath('.//span[@class="locality"]/text()'))
        state = "".join(d.xpath('.//span[@class="state"]/text()'))
        country_code = "US"
        postal = "".join(d.xpath('.//span[@class="postal-code"]/text()'))
        store_number = "".join(d.xpath(".//div[1]//h3/text()"))
        ll = "".join(d.xpath('.//div[@class="coordinates"]/text()'))
        js = json.loads(ll)
        latitude = js.get("coordinates")[1]
        longitude = js.get("coordinates")[0]
        location_type = "Branch"
        hours_of_operation = (
            " ".join(d.xpath(".//text()"))
            .replace("\n", "")
            .split("Lobby hours:")[1]
            .split("Drive-up")[0]
            .replace("CT", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="addressfield-container-inline locality-block country-US"]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
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
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
