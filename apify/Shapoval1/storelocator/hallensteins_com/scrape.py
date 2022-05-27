import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hallensteins.com/"
    api_url = "https://www.hallensteins.com/store-locations/all-stores-worldwide"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store__main--details u-pb-24"]')
    for d in div:

        page_url = "".join(d.xpath("./a/@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        js_block = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        j = json.loads(js_block)
        location_name = "".join(tree.xpath('//h1[@class="s-heading-2"]/text()'))
        a = j.get("address")
        ad = "".join(a.get("streetAddress")).replace("\r\n", " ").strip() or "<MISSING>"
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("addressCountry") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        ll = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            latitude = ll.split("center=")[1].split(",")[0].strip()
            longitude = ll.split("center=")[1].split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="info__hours--week"]/p//text()'))
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
