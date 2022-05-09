from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cswg.com/"
    api_url = "https://www.cswg.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="child-sidebar-menu"]//li//a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@id="main-core"]//p[position() > 1]')
        for d in div:

            info = d.xpath(".//text()")
            info = list(filter(None, [a.strip() for a in info]))
            if not info:
                continue
            address_line = " ".join(info)
            if (
                "Located" in address_line
                or "Links" in address_line
                or "With" in address_line
                or "In 20" in address_line
                or "Founded" in address_line
            ):
                continue
            address_line = (
                address_line.replace("Addresses", "")
                .replace("Address", "")
                .replace(":", "")
                .strip()
            )
            a = parse_address(International_Parser(), address_line)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = location_name.split(",")[1].replace(".", "").strip()
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = location_name.split(",")[0].strip()

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
                raw_address=address_line,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
