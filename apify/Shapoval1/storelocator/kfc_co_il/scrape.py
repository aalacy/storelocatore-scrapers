import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.co.il"
    api_url = "https://www.kfc.co.il/branches/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "var address_list_76c3d36 = ")]/text()'
            )
        )
        .split("var address_list_76c3d36 = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:
        ad = "".join(j.get("address"))
        info = j.get("infoWindow")
        a = html.fromstring(info)
        al = a.xpath("//*//text()")
        page_url = "https://www.kfc.co.il/branches/"
        location_name = "".join(al[1]).strip()
        aa = parse_address(International_Parser(), ad)
        street_address = f"{aa.street_address_1} {aa.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = aa.postcode or "<MISSING>"
        country_code = "IL"
        city = ad.split(",")[-2].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = "".join(al[-1]).strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    f'//h5[text()="{location_name}"]/following::div[./div/h2[text()="טלפון"]][1]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = " ".join(phone.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
