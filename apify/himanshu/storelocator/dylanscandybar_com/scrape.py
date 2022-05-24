import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dylanscandybar.com/"
    page_url = "https://www.dylanscandybar.com/pages/visit"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="map-section-content"]')
    for d in div:

        location_name = "".join(d.xpath("./h2[1]//text()"))
        ad = "".join(d.xpath("./p[last()]/text()")).replace(".", "").strip()
        if ad.find("Located") != -1:
            ad = ad.split("Located")[0].strip()
        if ad.find("-") != -1:
            ad = ad.split("-")[0].strip()

        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        if ad.find("Bahamas") != -1:
            country_code = "Bahamas"
        city = a.city or "<MISSING>"
        adr = " ".join(d.xpath(".//*//text()")).replace("\n", "").strip()
        adr = " ".join(adr.split())
        ph = re.findall(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?", adr) or "<MISSING>"
        phone = "".join(ph)
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/strong[contains(text(), "Hours:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        cls = "".join(d.xpath('.//strong[contains(text(), "Closed due")]/text()'))
        if cls:
            hours_of_operation = "Closed"
        if hours_of_operation.find("Opening for") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("Opening") != -1:
            hours_of_operation = hours_of_operation.split("13th")[1].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
