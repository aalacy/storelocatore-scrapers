from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://supercleanmycar.com"
    api_url = "https://supercleanmycar.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[./span[text()="Locations"]]/following-sibling::ul/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        postal = (
            "".join(
                d.xpath(
                    f'.//following::h2[text()="{location_name}"]/following-sibling::p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .split()[-1]
            .strip()
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Hours"]/following-sibling::p/text() | //*[contains(text(), "HOURS:")]/text()'
                )
            )
            .replace("HOURS:", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        ad = (
            "".join(
                tree.xpath('//h2[text()="Directions"]/following-sibling::p[1]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
