from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://exerurgentcare.com/"
    api_url = "https://exerurgentcare.com/exer-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-card location-data"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="location-card__link-holder"]/@href'))
        location_name = "".join(
            d.xpath('.//div[@class="location-card__title"]/text()')
        ).strip()
        ad = "".join(d.xpath('.//div[@class="location-card__address"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        if ad.find("CA") != -1:
            state = "CA"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="about__information"]//div[text()="Phone number"]/following-sibling::a/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//div[@class="about__information"]//div[@class="about__schedule"]/text()'
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
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
