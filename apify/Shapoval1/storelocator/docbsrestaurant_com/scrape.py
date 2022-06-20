import re
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://docbsrestaurant.com/"
    api_url = "https://docbsrestaurant.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@href, "locations/")]')
    for d in div:

        slug = "".join(d.xpath("./@href"))
        page_url = f"https://docbsrestaurant.com{slug}"
        location_name = "".join(
            d.xpath(
                './/div[./img[contains(@src, "locations")]]/following-sibling::div[1]/div[1]//text()'
            )
        ).strip()
        street_address = "".join(
            d.xpath(
                './/div[./img[contains(@src, "locations")]]/following-sibling::div[1]/div[2]//text()'
            )
        ).strip()
        ad = "".join(
            d.xpath(
                './/div[./img[contains(@src, "locations")]]/following-sibling::div[1]/div[3]//text()'
            )
        ).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        js_block = "".join(tree.xpath('//script[@type="application/json"]/text()'))
        js = json.loads(js_block)["props"]["pageProps"]
        store_number = js.get("location").get("id") or "<MISSING>"
        latitude = js.get("location").get("latitude") or "<MISSING>"
        longitude = js.get("location").get("longitude") or "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )

        search = re.search(r"(\d{3}-\d{3}-\d{4})", phone)
        if search:
            phone = search.group(1)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(text(), "Hours")]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("Valet") != -1:
            hours_of_operation = hours_of_operation.split("Valet")[0].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
