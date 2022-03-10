from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cannabishouseyeg.com"
    api_url = "https://cannabishouseyeg.com/Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[contains(text(), "Locations")]/following-sibling::ul//a[contains(@href, "/")]'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://cannabishouseyeg.com{slug}"
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        line1 = "".join(
            tree.xpath('//h4[text()="Address"]/following-sibling::p[1]/text()[1]')
        )
        line2 = (
            "".join(
                tree.xpath('//h4[text()="Address"]/following-sibling::p[1]/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        street_address = " ".join(line1.split(",")[:-1])
        state = line2.split()[0].strip()
        postal = " ".join(line2.split()[1:])
        country_code = "CA"
        city = line1.split(",")[-1].strip()
        latitude = "".join(tree.xpath("//div/@data-lat"))
        longitude = "".join(tree.xpath("//div/@data-lng"))
        phone = (
            "".join(
                tree.xpath(
                    '//h4[text()="Contact"]/following-sibling::p[1]/a[not(contains(@href, "mail"))]//text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Business Hours"]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Coming Soon") != -1:
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
            raw_address=f"{line1} {line2}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
