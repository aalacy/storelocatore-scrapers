from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.com.sg/"
    api_url = "https://www.honda.com.sg/about-us/our-locations.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="data-address"]/li')
    for d in div:

        page_url = "https://www.honda.com.sg/about-us/our-locations.html"
        location_name = "".join(d.xpath('.//h5[@class="title"]/text()'))
        if "Showroom" not in location_name:
            continue
        location_type = "<MISSING>"
        if "Showroom" in location_name:
            location_type = "Showroom"
        ad = (
            "".join(
                d.xpath(
                    './/i[@class="fas fa-map-marker-alt"]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "SG"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//@onclick")).split("(")[1].split(",")[0].strip()
        longitude = "".join(d.xpath(".//@onclick")).split("(")[1].split(",")[1].strip()
        phone = (
            "".join(d.xpath('.//i[@class="fas fa-phone"]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(d.xpath('.//i[@class="far fa-clock"]/following-sibling::text()'))
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
