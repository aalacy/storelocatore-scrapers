import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.ippudo.com.my"
        page_url = "https://www.ippudo.com.my/store-location"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=page_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//div[./h3[./span[contains(text(), "Lot")]]] | //div[./h3[./span[contains(text(), "G1")]]] | //div[./h3[./span[contains(text(), "170-")]]]'
        )
        for d in div:
            ad = "".join(d.xpath(".//text()")).replace("\n", "").strip()
            location_name = "".join(
                d.xpath(
                    './/following::span[text()="GRAND MENU"][1]/preceding::span[contains(@style, "font-size:24px")][1]//text()'
                )
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "MY"
            city = a.city or "<MISSING>"
            phone = "".join(
                d.xpath(
                    './/following::span[text()="GRAND MENU"][1]/preceding::a[contains(@href, "tel")][1]//text()'
                )
            )
            hours_of_operation = (
                "".join(
                    d.xpath(
                        './/following::span[text()="GRAND MENU"][1]/preceding::h3[./span[contains(text(), "PM")]][1]//text()'
                    )
                )
                .replace("\n", "")
                .replace("PM", "PM ")
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
