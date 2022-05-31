from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.youngs.co.uk"
    api_url = "https://www.youngs.co.uk/our-pubs"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="venues__card"]')
    for d in div:

        page_url = "https://www.youngs.co.uk/our-pubs"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = (
            " ".join(d.xpath(".//h3/following-sibling::p//text()"))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        info = d.xpath(".//h3/following-sibling::p//text()")
        info = list(filter(None, [b.strip() for b in info]))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if street_address.find(f"{postal}") != -1:
            street_address = ad.split(",")[0].strip()
        if street_address.find(f"{postal}") != -1:
            street_address = "".join(info[0]).strip()
        if postal == "<MISSING>" or postal.count(" ") != 1:
            postal = info[-1].strip()
        postal_slug = postal.split()[0].strip()
        if street_address.find(f"{postal_slug}") != -1:
            street_address = "".join(info[0]).strip()
        if city == "<MISSING>":
            city = "".join(info[-2]).strip()

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
