from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.brunofoodcorner.be/"
    api_url = "https://www.brunofoodcorner.be/nl/location/ajax?filter%5B%5D=3"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    tree = html.fromstring(js)
    div = tree.xpath('//div[@class="heroblock"]')
    for d in div:

        slug = "".join(d.xpath("./a/@href"))
        page_url = f"https://www.brunofoodcorner.be{slug}"
        location_name = "".join(
            d.xpath(".//h2[@class='heroblock-pretitle self']//text()")
        )
        street_address = (
            "".join(d.xpath('.//p[@class="heroblock-contents"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="heroblock-contents"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        state = "<MISSING>"
        postal = ad.split()[0].strip()
        country_code = "BE"
        city = ad.split()[1].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        store_number = page_url.split("detail/")[1].split("/")[0].strip()
        phone = (
            "".join(
                tree.xpath('//i[@class="fas fa-phone"]/following-sibling::text()[1]')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        info = (
            " ".join(tree.xpath('//p[./i[@class="fas fa-phone"]]//text()'))
            .replace("\n", "")
            .strip()
        )
        info = " ".join(info.split())
        hours_of_operation = info.split(f"{ad}")[1].split(f"{phone}")[0].strip()
        hours_of_operation = " ".join(hours_of_operation.split())
        r = session.get(
            f"https://www.brunofoodcorner.be/nl/api/locations/{store_number}"
        )
        js = r.json()
        latitude = js[0][1]
        longitude = js[0][2]

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
