from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curvesclub.hu/"
    session = SgRequests()
    api_url = "https://curvesclub.hu/en/find-your-club"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="same_height_max c transitions"]')
    for d in div:

        page_url = "".join(d.xpath("./@href"))
        location_name = "".join(d.xpath('.//span[@class="t"]/text()'))
        ad = "".join(d.xpath('.//span[@class="a"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "HU"
        city = a.city or "<MISSING>"
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
            "".join(tree.xpath('//p[contains(text(), "Telefon:")]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .replace("Telefon:", "")
            .strip()
            or "<MISSING>"
        )
        if phone.count("+") == 2:
            phone = "+" + phone.split("+")[1].strip()
        if phone.find("E") != -1:
            phone = phone.split("E")[0].strip()

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[text()="NYITVATARTÁS:"]]/following-sibling::p/text() | //strong[text()="NYITVATARTÁS:"]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        if hours_of_operation.find("Az utolsó") != -1:
            hours_of_operation = hours_of_operation.split("Az utolsó")[0].strip()
        cms = "".join(
            tree.xpath('//strong[contains(text(), "HAMAROSAN NYITUNK!")]/text()')
        )
        if cms:
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
