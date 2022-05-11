import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://killerburger.com"
    api_url = "https://killerburger.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var locations_meta =")]/text()'))
        .split("var locations_meta =")[1]
        .split("}];")[0]
        .strip()
        + "}]"
    )
    js = json.loads(div)
    for j in js:
        a = j.get("location")
        page_url = "https://killerburger.com/locations/"
        location_name = a.get("branch_name")
        b = a.get("map_pin")
        street_address = (
            f"{b.get('street_number')} {b.get('street_name')}" or "<MISSING>"
        )
        state = b.get("state") or "<MISSING>"
        postal = b.get("post_code") or "<MISSING>"
        country_code = "US"
        city = b.get("city") or "<MISSING>"
        latitude = b.get("lat")
        longitude = b.get("lng")
        phone = a.get("store_phone_number") or "<MISSING>"
        hours = a.get("locations_opening_times")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                time = h.get("open_times")
                line = f"{time}"
                tmp.append(line)
            hours_of_operation = ", ".join(tmp) or "<MISSING>"

        if street_address.find("None") != -1:
            street_address = (
                "".join(
                    tree.xpath(
                        f'//div[./h4[contains(text(), "{location_name}")]]/following-sibling::div[1]/p/text()[1]'
                    )
                )
                .replace(",", "")
                .strip()
            )
        if str(location_name).find("SOON") != -1:
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
