import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://mikescarwash.com"
        api_url = "https://mikescarwash.com/pages/locations"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="locationList-wrap"]')
        for d in div:

            page_url = "https://mikescarwash.com/pages/locations"
            location_name = "".join(
                d.xpath('.//div[@class="locationList-locationName"]/text()')
            )
            ad = (
                " ".join(d.xpath('.//div[@class="locationList-address"]/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            slug = (
                "".join(d.xpath('.//div[@class="locationList-info-container"]/@id'))
                .split("-")[-1]
                .strip()
            )
            street_address = (
                " ".join(d.xpath('.//div[@class="locationList-address"]/text()[1]'))
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            latitude = (
                "".join(
                    tree.xpath(
                        '//script[contains(text(), "new google.maps.LatLng")]/text()'
                    )
                )
                .split(f"locNum: {slug}")[1]
                .split("(")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(
                        '//script[contains(text(), "new google.maps.LatLng")]/text()'
                    )
                )
                .split(f"locNum: {slug}")[1]
                .split("(")[1]
                .split(",")[1]
                .split(")")[0]
                .strip()
            )
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="locationList-dailyHours"]/text()'))
                .replace("\n", "")
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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
