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
        locator_domain = "https://chilis.com.my"
        api_url = "https://chilis.com.my/outlets/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="outlet-accordion-item"]')
        for d in div:

            page_url = "https://chilis.com.my/outlets/"
            location_name = (
                "".join(d.xpath('.//div[@class="outlet-accordion-item-head"]/text()'))
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(d.xpath('./div[@class="outlet-accordion-item-content"]/text()'))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            country_code = "MY"
            city = a.city or "<MISSING>"
            city = city.replace(".", "").strip()
            text = "".join(d.xpath('.//a[text()="Show on map"]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("/@")[1].split(",")[0]
                    longitude = text.split("/@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(
                    d.xpath(
                        './/strong[contains(text(), "Tel:")]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/h5[contains(text(), "Operation hours")]/following-sibling::p[position()<3]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
