from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://communitysurgical.com"
    api_url = "https://www.powr.io/map/u/75667338_1547049950#platform=shopify&url=https%3A%2F%2Fcommunitysurgical.com%2Fpages%2Fservicing-locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://communitysurgical.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "iframe",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "window.CONTENT")]/text()'))
        .split('"locations":')[1]
        .split(',"smartDesign"')[0]
        .strip()
    )
    jsblock = (
        "["
        + jsblock.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
        + "]"
    )
    jsblock = (
        jsblock.replace('"address"', '["address"')
        .replace(',["address"', '],["address"')
        .replace("/", "")
        .replace("\\", "")
        .replace(":", "")
        .replace('"', "")
    )
    jsblock = jsblock.replace("[[", '[["').replace("],[address", '"],["address')
    jsblock = jsblock + "]"
    jsblock = jsblock.replace("]]", '"]]')
    js = eval(jsblock)

    for i in js:
        page_url = "https://communitysurgical.com/pages/servicing-locations"
        location_name = "".join(i).split("nameu003cpu003e")[1].split(",")[0].strip()
        location_type = "Community Surgical Supply"
        ad = "".join(i).split("address")[1].split("USA")[0].strip()
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[1].strip()
        latitude = "".join(i).split("lat")[1].split(",")[0].strip()
        longitude = "".join(i).split("lng")[1].split(",")[0].strip()

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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
