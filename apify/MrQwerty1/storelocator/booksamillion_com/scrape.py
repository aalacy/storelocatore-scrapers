from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for _zip in search:
        api = f"https://www.bullseyelocations.com/pages/BAMStoreFinder?PostalCode={_zip}&CountryId=1&Radius=500"
        r = session.get(api, headers=headers)
        tree = html.fromstring(r.text)

        li = tree.xpath("//ul[@id='resultsCarouselWide']/li")
        for l in li:
            location_name = "".join(l.xpath(".//h3[@itemprop='name']/text()")).strip()
            slug = "".join(l.xpath(".//a[@itemprop='url']/@href")).split("?")[0].strip()
            page_url = f"https://www.bullseyelocations.com/pages/{slug}"

            street_address = "".join(
                l.xpath(".//span[@itemprop='streetAddress']/text()")
            ).strip()
            city = "".join(
                l.xpath(".//span[@itemprop='addressLocality']/text()")
            ).strip()[:-1]
            state = "".join(
                l.xpath(".//span[@itemprop='addressRegion']/text()")
            ).strip()
            postal = "".join(l.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            store_number = "".join(l.xpath(".//input[@id='ThirdPartyId']/@value"))

            try:
                phone = l.xpath(".//span[@itemprop='telephone']/@data-content")[0]
            except IndexError:
                phone = SgRecord.MISSING

            latitude = "".join(l.xpath(".//meta[@itemprop='latitude']/@content"))
            longitude = "".join(l.xpath(".//meta[@itemprop='longitude']/@content"))

            if latitude == "0" or longitude == "0":
                latitude = SgRecord.MISSING
                longitude = SgRecord.MISSING

            hours_of_operation = "".join(
                l.xpath(".//div[@class='popDetailsHours']/meta/@content")
            ).replace("|", ";")[:-1]

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.booksamillion.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
