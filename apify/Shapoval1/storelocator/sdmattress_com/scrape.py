import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sdmattress.com"
    api_url = "https://www.sdmattress.com/locations.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="View Details"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.sdmattress.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h2//text()")) or "<MISSING>"
        street_address = (
            "".join(tree.xpath("//address/text()[1]")).replace("\n", "").strip()
        )
        street_address = " ".join(street_address.split())
        ad = "".join(tree.xpath("//address/text()[2]")).replace("\n", "").strip()
        ad = " ".join(ad.split())
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        js = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        j = json.loads(js)
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        phone = (
            "".join(tree.xpath('//p[text()="Phone"]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath('//p[text()="Hours"]/following-sibling::table//tr/td/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
