from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.youngs.co.uk"
    api_url = "https://www.youngs.co.uk/our-hotels"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="venues__card"]')
    for d in div:

        page_url = "".join(d.xpath("./a/@href")) + "contact/"
        if page_url.find("spreadeaglewandsworth") != -1:
            page_url = "https://www.spreadeaglewandsworth.co.uk/"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = " ".join(d.xpath(".//h3/following-sibling::p//text()"))
        ad = " ".join(ad.split())
        info = d.xpath(".//h3/following-sibling::p//text()")
        info = list(filter(None, [b.strip() for b in info]))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if city.find("Whitway Newbury") != -1:
            city = city.split()[1].strip()
        if city == "<MISSING>":
            city = "".join(info[-2]).strip()
        if postal == "<MISSING>":
            postal = "".join(info[-1])
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        try:
            phone = (
                "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
                .split('"telephone": "')[1]
                .split('"')[0]
                .strip()
            )
        except:
            phone = "<MISSING>"
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//p[contains(text(), "Tel:")]/strong[1]/text()'))
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//*[text()="Opening Times"]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("Festive") != -1:
            hours_of_operation = hours_of_operation.split("Festive")[0].strip()
        if hours_of_operation.find("Opening Hours") != -1:
            hours_of_operation = hours_of_operation.split("Opening Hours")[0].strip()
        if hours_of_operation.find("New") != -1:
            hours_of_operation = hours_of_operation.split("New")[0].strip()
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath('.//p[contains(text(), "Opening times:")]/strong/text()')
                )
                .replace("\n", "")
                .replace("\r", "")
                .strip()
            )
        if hours_of_operation == "Open":
            hours_of_operation = "<MISSING>"
        hours_of_operation = " ".join(hours_of_operation.split())

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
