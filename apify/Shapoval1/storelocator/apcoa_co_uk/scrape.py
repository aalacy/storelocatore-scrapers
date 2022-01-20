import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.apcoa.co.uk/"
    api_url = "https://www.apcoa.co.uk/typo3temp/assets/js/1d282eaa2d.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    r = session.get(api_url, headers=headers)
    div = r.text.split("uid:")[1:]
    for d in div:

        location_name = d.split("title:")[1].split(",")[0].replace("'", "").strip()
        country_code = "UK"
        store_number = d.split(",")[0].strip()
        latitude = d.split("latitude:")[1].split(",")[0].strip()
        longitude = d.split("longitude:")[1].split(",")[0].strip()
        r = session.get(
            f"https://www.apcoa.co.uk/parking-locations/all-locations/?type=1372255351&tx_fmlocations_locations%5Bcontroller%5D=Ajax&tx_fmlocations_locations%5Baction%5D=callAjaxObject&tx_fmlocations_locations%5BobjectName%5D=GetMarkerContent&tx_fmlocations_locations%5Barguments%5D%5Blocation%5D={store_number}"
        )
        js = r.json()
        con = js.get("content")
        tree = html.fromstring(con)

        slug = "".join(
            tree.xpath('//div[@class="locationlistBoxPad"]/a[@class="loctitle"]/@href')
        )
        page_url = f"https://www.apcoa.co.uk/{slug}"
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            page_url = "https://www.apcoa.co.uk/parking-locations/all-locations/"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        if (
            page_url.find("=") != -1
            and page_url != "https://www.apcoa.co.uk/parking-locations/all-locations/"
        ):
            slug = "".join(
                tree.xpath('//ol[@itemprop="breadcrumb"]/li[last()]/a/@href')
            )
            page_url = f"https://www.apcoa.co.uk/{slug}"
        try:
            city = page_url.split("parking-in/")[1].split("/")[0].capitalize().strip()
        except:
            city = "<MISSING>"
        ad = tree.xpath("//address/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        try:
            street_address = "".join(ad[0]).strip()
        except:
            street_address = "<MISSING>"
        try:
            adr = "".join(ad[1]).strip()
        except:
            adr = "<MISSING>"
        state = "<MISSING>"
        postal = " ".join(adr.split()[:2]) or "<MISSING>"
        if postal.find(f"{city}") != -1:
            postal = postal.replace(f"{city}", "").strip()
        phone = "<MISSING>"
        if len(ad) == 3:
            phone = "".join(ad[2])
        try:
            if "".join(ad[-1]).replace(" ", "").isdigit():
                phone = "".join(ad[-1])
        except:
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[text()="Opening Hours"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        js_block = "".join(
            tree.xpath('//script[contains(text(), "LocalBusiness")]/text()')
        )
        if page_url == "https://www.apcoa.co.uk/parking-locations/all-locations/":
            street_address = (
                d.split("address:")[1].split(",")[0].replace("'", "").strip()
            )
        if js_block:
            js = json.loads(js_block)
            page_url = js.get("url")
            location_name = js.get("name") or "<MISSING>"
            a = js.get("address")
            street_address = a.get("streetAddress") or "<MISSING>"
            city = a.get("addressLocality") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"

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
