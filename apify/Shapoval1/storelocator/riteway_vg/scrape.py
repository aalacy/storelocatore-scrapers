from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.riteway.vg/"
    api_url = "https://www.riteway.vg/storelocator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="source VG"]')
    for d in div:

        page_url = "https://www.riteway.vg/storelocator/"
        ids = "".join(d.xpath('.//a[@class="go-to-source"]/@id'))
        location_name = "".join(d.xpath(".//h3/a/text()")).replace("\n", "").strip()
        ad = " ".join(d.xpath(".//table//tr/td[1]//text()")).replace("\n", "").strip()
        adr = (
            " ".join(d.xpath(".//table//tr/td[1]/text()[position() > 1]"))
            .replace("\n", "")
            .split("☎")[0]
            .strip()
        )
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "")
            .replace("Vg1110", "")
            .strip()
            or adr
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "VG"
        city = a.city or "<MISSING>"
        if "Vg" in city:
            postal = city
            city = "<MISSING>"
        if "Tortola" in adr:
            city = "Tortola"
        if "VG" in adr:
            postal = adr.split("VG")[1].split()[0].strip()
        latitude = (
            "".join(
                tree.xpath('//script[contains(text(), "storelocator.sources")]/text()')
            )
            .split(f'id":"{ids}"')[1]
            .split('"lat":"')[1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath('//script[contains(text(), "storelocator.sources")]/text()')
            )
            .split(f'id":"{ids}"')[1]
            .split('"lng":"')[1]
            .split('"')[0]
            .strip()
        )
        phone = (
            ad.split("☎")[1]
            .split("✉")[0]
            .replace("=", "+")
            .replace("+1284", "+1 284")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr/td[2]//text()")).replace("\n", "").strip()
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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
