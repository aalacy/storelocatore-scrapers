from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://nespresso.lv/"
    api_urls = [
        "https://nespresso.lv/en/stores",
        "https://nespresso.lt/en/stores",
        "https://nespresso.ee/en/stores",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//p[@class="sidebar-store-locator-address"]')
        for d in div:

            page_url = api_url
            location_name = (
                "".join(d.xpath(".//b/span/text()")).replace("\n", "").strip()
            )
            ad = (
                "".join(d.xpath(".//b/following-sibling::span[1]/text()"))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = (
                "".join(d.xpath(".//b/following-sibling::span[3]/text()"))
                .replace("\n", "")
                .replace("Post:", "")
                .strip()
            )
            country_code = page_url.split("nespresso.")[1].split("/")[0].upper().strip()
            city = (
                "".join(d.xpath(".//b/following-sibling::span[2]/text()"))
                .replace("\n", "")
                .strip()
            )
            latitude = (
                "".join(d.xpath('.//span[contains(text(), "Latitude:")]/text()'))
                .replace("Latitude:", "")
                .strip()
            )
            longitude = (
                "".join(d.xpath('.//span[contains(text(), "Longitude:")]/text()'))
                .replace("Longitude:", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/span[contains(text(), "-VI")]/text() | .//span[contains(text(), "V-")]/text()'
                    )
                )
                .replace("\n", "")
                .replace("\r", "")
                .strip()
                or "<MISSING>"
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
                phone=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
