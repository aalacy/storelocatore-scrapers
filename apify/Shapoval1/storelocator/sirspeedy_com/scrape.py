from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sirspeedy.com"
    api_url = "https://sirspeedy.com/find-a-location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//section[@class="c-tab__panel"]')
    for d in div:

        blocks = d.xpath('.//div[@class="c-tab__panel-card"]//a')
        for b in blocks:
            slug = "".join(b.xpath(".//@href"))
            page_url = f"https://sirspeedy.com{slug}"

            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            ad = (
                " ".join(tree.xpath('//div[@class="c-cta-row__address"]//text()'))
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            country_code = "US"
            if state == "ON":
                country_code = "CA"
            country_head = "".join(b.xpath(".//preceding::h3[1]/text()"))
            if country_head == "Brazil":
                country_code = "Brazil"
            if country_head == "India":
                country_code = "India"
            if country_head == "Taiwan":
                country_code = "Taiwan"
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"
            if city == "<MISSING>":
                city = "".join(b.xpath(".//text()"))
            location_name = (
                "".join(
                    tree.xpath(
                        '//div[@class="c-cta-row__address"]/preceding-sibling::h2[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="c-cta-row__hours-row"]//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .replace("Email for Curbside", "")
                .replace("Weekends - Please Call", "")
                .replace("Please Call", "<MISSING>")
                .replace("(subject to change)", "")
                .replace("By Appointment Only", "")
                .replace("Available After Hours by Appointment", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="c-cta-row__franchise-content"]//a[contains(@href, "tel")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
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
