from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://massagegreenspa.com/"
    api_url = "https://massagegreenspa.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div[@class="sabai-directory-title"]]')
    for d in div:

        page_url = "".join(d.xpath('.//div[@class="sabai-directory-title"]/a/@href'))
        location_name = "".join(
            d.xpath('.//div[@class="sabai-directory-title"]/a/text()')
        )
        ad = (
            "".join(d.xpath('.//div[@class="sabai-directory-location"]/span/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = "".join(d.xpath('.//span[@itemprop="telephone"]/text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(
                tree.xpath('//div[@id="sabai-inline-content-map"]/script[1]/text()')
            )
            .split('"lat":')[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath('//div[@id="sabai-inline-content-map"]/script[1]/text()')
            )
            .split('"lng":')[1]
            .split(",")[0]
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
