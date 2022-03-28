from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.co.th"
    api_url = "https://www.honda.co.th/api/getDealersByFiltered?hasLocation=false&lat=&lng=&offset=0&perpage=300&keyword=&showrooms=%E0%B9%82%E0%B8%8A%E0%B8%A7%E0%B9%8C%E0%B8%A3%E0%B8%B9%E0%B8%A1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.honda.co.th/dealer/search?keyword=&showrooms=showroom&modelrelay=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["html"]
    tree = html.fromstring(js)
    div = tree.xpath('//div[@class="dealer-item dealer-item--setbox"]')
    for d in div:

        page_url = "https://www.honda.co.th/dealer/all"
        location_name = "".join(d.xpath('.//div[@class="dealer-name"]/text()'))
        ad = (
            "".join(d.xpath('.//div[@class="dealer-address"]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        location_type = "โชว์รูม"
        location_type = " ".join(location_type.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "TH"
        city = a.city or "<MISSING>"
        text = "".join(d.xpath(".//iframe/@src"))
        latitude = text.split("q=")[1].split(",")[0].strip()
        longitude = text.split("q=")[1].split(",")[1].split("&")[0].strip()
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="col-12 col-md-6 contact-detail"]//a[contains(@href, "tel")]//text()'
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
