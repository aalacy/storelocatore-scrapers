from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://workhaus.ca/"
    api_url = "https://workhaus.ca/location-sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()"))
        ad = (
            "".join(
                tree.xpath('//section[@id="intro"]//div[@class="full-address"]/text()')
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "coordinates")]/text()'))
            .split("coordinates")[1]
            .split("[")[1]
            .split(",")[0]
            .replace("'", "")
            .strip()
        )
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "coordinates")]/text()'))
            .split("coordinates")[1]
            .split("[")[1]
            .split(",")[1]
            .split("]")[0]
            .replace("'", "")
            .strip()
        )
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        slug = "".join(tree.xpath('//div[contains(text(), "24/7")]/text()'))
        hours_of_operation = "<MISSING>"
        if slug:
            hours_of_operation = "24/7"

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
