from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data(_zip, sgw: SgWriter):
    api = f"https://wwwint.kemper.com/wps/portal/Kemper/Home/InformationCenter/FindAgency/!ut/p/b1/hY7LCsIwFES_yNy50XrJsqVEW2yLD7BmI1VECqZ1IYp_bwQ3LrSzGzhzGHJUk-uae3tubm3fNZd3d9P9bJXAJByj2mSCLGVbTFBo2HEAdgHAj8QY2ufk2oNXj6NXUAYSCRvNIkaYDW3JfQuAKggWZW6XqDTSaAAQ_QH-PCznvT_R1dfPdTaKX7H6rDk!/dl4/d5/L0lDU0lKSmdrS0NsRUpDZ3BSQ1NBL29Ob2dBRUlRaGpFS0lRQUJHY1p3aklDa3FTaFNOQkFOYUEhIS80RzNhRDJnanZ5aENreUZNTlFpa3lGS05SaklVUVEhIS9aN19HUkIwOUIxQTBPVEk3MElEMUZNNDBNMkdHNy8wL2libS5pbnYvNDk2NjUwNjQ1MDA5L2phdmF4LnBvcnRsZXQuYWN0aW9uL2ZpbmRBZ2VudA!!/?lob=AUTOP&lob=BOAT&lob=AUTOB&lob=HOME&lob=RENTER&lob=CONDO&lob=life&lob=health&searchType=zip&zipCode={_zip}&street=&city=&state=&seeAllFlag="
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//tr[contains(@class, 'searchResultsRow')]")

    for d in divs:
        street_address1 = "".join(
            d.xpath(".//span[@class='agencyAddressValue']/text()")
        ).strip()
        street_address2 = "".join(
            d.xpath(".//span[@class='agencyAddressLine2Value']/text()")
        ).strip()
        if street_address2:
            street_address = f"{street_address1}, {street_address2}"
        else:
            street_address = street_address1
        city = "".join(d.xpath(".//span[@class='agencyAddressCity']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='agencyAddressState']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='agencyAddressZip']/text()")).strip()
        country_code = "US"
        location_name = "".join(d.xpath(".//span[@class='agencyName']//text()")).strip()
        phone = "".join(d.xpath(".//span[@class='contactAgencyPhone']/text()")).strip()
        text = "".join(d.xpath("./@onclick"))
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        if "recenterMap" in text:
            latitude, longitude = eval(text.split("recenterMap")[1].replace(";", ""))

        row = SgRecord(
            page_url=SgRecord.MISSING,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.kemper.com"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for p in search:
            fetch_data(p, writer)
