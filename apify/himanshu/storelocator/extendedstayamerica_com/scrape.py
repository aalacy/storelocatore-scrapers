import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://api.prod.bws.esa.com/cms-proxy-api/sitemap/property", headers=headers
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/hotels/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.extendedstayamerica.com/"
    page_url = "".join(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    session = SgRequests(verify_ssl=False)
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(
        tree.xpath('//script[contains(text(), "openingHoursSpecification")]/text()')
    )
    try:
        js = json.loads(js_block)
        a = js.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        location_name = js.get("name") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        store_number = js.get("identifier") or "<MISSING>"
        latitude = js.get("geo").get("latitude") or "<MISSING>"
        longitude = js.get("geo").get("longitude") or "<MISSING>"
        hours_of_operation = "Open 24 hours a day, seven days a week"
    except:
        location_name = "".join(tree.xpath("//h1//text()"))
        ad = (
            "".join(
                tree.xpath("//div[./h1]/following-sibling::div[1]/div/div[2]/text()")
            )
            .replace("\n", "")
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        phone = (
            "".join(
                tree.xpath(
                    "//div[./h1]/following-sibling::div[1]/div/div[1]//a//text()"
                )
            )
            .replace("\n", "")
            .strip()
        )
        ll = "".join(tree.xpath("//div[@data-latlng]/@data-latlng"))
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        hours_of_operation = "Open 24 hours a day, seven days a week"
        try:
            store_number = (
                "".join(
                    tree.xpath(
                        '//script[contains(text(), "openingHoursSpecification")]/text()'
                    )
                )
                .split('"identifier": "')[1]
                .split('"')[0]
                .strip()
            )
        except:
            store_number = "<MISSING>"
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


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
