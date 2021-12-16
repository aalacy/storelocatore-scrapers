from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.menchies.com/"
    api_url = "https://www.menchies.com/all-locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[@class="font-purple title-case"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        cms = "".join(
            d.xpath('.//following-sibling::span[@class="coming-soon"]/text()')
        )
        page_url = f"https://www.menchies.com{slug}"
        country_code = "".join(
            d.xpath(
                './/preceding::h3[contains(@class, "loc-header country-name")][1]/text()'
            )
        )

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(tree.xpath('//a[@class="loc-full-address"]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        if location_name == "<MISSING>":
            continue
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        if state == "Ab Ab":
            state = "AB"
        postal = a.postcode or "<MISSING>"

        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = (
                " ".join(tree.xpath('//a[@class="loc-full-address"]//text()[last()]'))
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
        try:
            latitude = (
                "".join(tree.xpath('//a[@class="loc-full-address"]/@href'))
                .split("=")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//a[@class="loc-full-address"]/@href'))
                .split("=")[1]
                .split(",")[1]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            try:
                latitude = (
                    "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
                    .split("LatLng(")[1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
                    .split("LatLng(")[1]
                    .split(",")[1]
                    .split(")")[0]
                    .strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
        if not latitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(tree.xpath('//p[@class="loc-phone"]/a//text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//p[@class="loc-hours"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
