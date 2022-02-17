from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumph-motorcycles.co.za/"
    api_url = "https://www.triumph-motorcycles.co.za/data/visitor-centre/maps/42bf00a9-937e-4c12-a751-5d387ca03648/markers?page=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = (
            "https://www.triumph-motorcycles.co.za/dealers/south-africa/locate-a-dealer"
        )
        location_name = str(j.get("Title"))
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        ad = str(j.get("AddressText")).replace("<br/>", " ").strip()
        ad = " ".join(ad.split())
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "ZA"
        city = a.city or "<MISSING>"
        slug = str(j.get("AddressText")).split("<br/>")[0].replace(",", "").strip()
        phone = (
            "".join(
                tree.xpath(
                    f'//p[contains(text(), "{slug}")]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .replace(":", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    f'//p[contains(text(), "{slug}")]/following-sibling::p[last()]/text()'
                )
            )
            .replace("\n", " ")
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
