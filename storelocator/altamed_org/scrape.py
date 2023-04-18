from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.altamed.org/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    zeeps = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=30,
        max_search_results=None,
    )
    for zips in zeeps:
        r = session.get(
            f"https://www.altamed.org/find/results?type=clinic&keywords={str(zips)}&affiliates=yes",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="geolocation-location js-hide location-purple"]')
        if len(div) == 0:
            zeeps.found_nothing()
        for d in div:

            page_url = f"https://www.altamed.org/find/results?type=clinic&keywords={str(zips)}&affiliates=yes"
            location_name = "".join(d.xpath('.//div[@class="title"]//text()'))
            location_type = (
                " ".join(
                    d.xpath(
                        './/div[contains(text(), "Service")]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", ",")
                .strip()
            )
            location_type = " ".join(location_type.split())
            ad = (
                " ".join(d.xpath('.//div[@class="address"]//text()'))
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
            longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
            zeeps.found_location_at(latitude, longitude)
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]//text()')) or "<MISSING>"
            )
            hours_of_operation = "<MISSING>"

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
                location_type=location_type,
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
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
