from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.youngs.co.uk/"
    api_url = "https://www.youngs.co.uk/wp-json/youngs/v1/venues?status=complete&criteria=burger-shack"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["venues"]
    info = js.get("cards")
    a = html.fromstring(info)
    div = a.xpath('//div[@class="venue-card  js-search-venue"]')
    for d in div:

        page_url = (
            "https://www.youngs.co.uk/search?status=complete&criteria=burger-shack"
        )
        location_name = "".join(d.xpath(".//h4//text()"))
        ad = d.xpath('.//p[@class="address"]/text()')
        adr = " ".join(ad).replace("\n", "").strip()
        adr = " ".join(adr.split())
        n = parse_address(International_Parser(), adr)
        street_address = "".join(ad[0])
        if len(ad) > 4:
            street_address = " ".join(ad[:2])
        street_address = " ".join(street_address.split()).replace(",", "").strip()
        state = "<MISSING>"
        postal = "".join(ad[-1])
        country_code = "UK"
        city = n.city or "<MISSING>"
        if city == "<MISSING>":
            city = "".join(ad[-2])
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        phone = (
            "".join(
                d.xpath(
                    './/p[@class="phone  text  text--push-left"]/a[contains(@href, "tel")][1]/text()'
                )
            )
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
            hours_of_operation=SgRecord.MISSING,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
