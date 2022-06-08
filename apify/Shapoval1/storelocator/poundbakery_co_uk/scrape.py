from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.poundbakery.co.uk/"
    api_url = "https://www.poundbakery.co.uk/store-search/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="stores-ddl"]/option')
    for d in div:
        slug = "".join(d.xpath(".//@value"))
        if not slug:
            continue

        page_url = f"https://www.poundbakery.co.uk{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="store"]/text()')).replace("\n", "").strip()
        )
        location_name = " ".join(location_name.split())
        ad = tree.xpath('//p[@class="address"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))

        street_address = " ".join(ad[:-3])
        state = "".join(ad[-2]) or "<MISSING>"
        postal = "".join(ad[-1]) or "<MISSING>"
        country_code = "UK"
        city = "".join(ad[-3]) or "<MISSING>"
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
                .split("LatLng(")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
                .split("LatLng(")[1]
                .split(",")[1]
                .split(")")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

        phone = (
            "".join(tree.xpath('//p[@class="telephone"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        hours_of_operation = (
            " ".join(
                tree.xpath('//ul[@class="list-unstyled list-opening-times"]/li//text()')
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
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
