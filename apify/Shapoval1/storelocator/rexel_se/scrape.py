import json
import urllib.parse
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rexel.se"
    api_url = "https://www.rexel.se/swe/store-finder"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath("//div/@data-stores"))
    js = json.loads(div)
    for j in js.values():

        location_name = j.get("displayName")
        street_address = j.get("line1")
        state = "<MISSING>"
        postal = j.get("postalCode")
        country_code = "SE"
        city = j.get("town")
        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        slug = urllib.parse.quote(location_name)
        page_url = f"https://www.rexel.se/swe/{slug}/store/{j.get('name')}"
        phone = j.get("phone")
        hours_of_operation = (
            "".join(
                tree.xpath(
                    f'//div[@class="addressList addressList{store_number}"]//span[@class="openingSchedule"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = "".join(j.get("formatedAddress")).replace("<br/>", "").strip()

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
