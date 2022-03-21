import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://customcomfortmattress.com"
    api_url = "https://code.metalocator.com/index.php?option=com_locator&view=directory&layout=combined_bootstrap&Itemid=14258&tmpl=component&framed=1&source=js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var location_data")]/text()'))
        .split("var location_data =")[1]
        .split("[]}];")[0]
        .strip()
        + "[]}]"
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = "https://customcomfortmattress.com/locations/"
        location_name = j.get("name")
        location_type = "Custom Comfort Mattress"
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postalcode")
        country_code = "US"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = (
            "".join(j.get("hours"))
            .replace("{", "")
            .replace("}", " ")
            .replace("|", " ")
            .strip()
        )
        if "Coming Soon" in location_name:
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
