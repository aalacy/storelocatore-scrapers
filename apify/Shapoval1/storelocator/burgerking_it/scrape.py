from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.it"
    api_url = "https://www.burgerking.it/ristoranti/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.burgerking.it/ristoranti/",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        storeId = j.get("storeId") or "<MISSING>"

        session = SgRequests()
        r = session.get(
            f"https://www.burgerking.it/map-markers-info/?storeId={storeId}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        slug = "".join(tree.xpath('//a[text()="Info"]/@href'))

        page_url = f"https://www.burgerking.it{slug}"
        if page_url == "https://www.burgerking.it/trash/8586735.7983420.1_ravenna/":
            continue

        session = SgRequests()
        headers_1 = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        }
        r_1 = session.get(page_url, headers=headers_1)
        tree = html.fromstring(r_1.text)

        location_name = "".join(tree.xpath('//h2[@id="store-title"]/text()'))
        adr_1 = " ".join(tree.xpath('//p[@class="address1"]/text()'))
        adr_2 = " ".join(tree.xpath('//p[@class="address2"]/text()'))
        ad = adr_1 + " " + adr_2

        a = parse_address(International_Parser(), ad)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Italy"
        city = "".join(tree.xpath('//h1[@id="store-city"]/text()')) or "<MISSING>"
        if city == "<MISSING>":
            city = a.city or "<MISSING>"

        phone = "".join(tree.xpath('//p[@class="phone"]/a/text()')) or "<MISSING>"
        _tmp = []
        days = tree.xpath('//div[@id="store-orari"]//table//tr/td[1]/text()')
        times = tree.xpath('//div[@id="store-orari"]//table//tr/td[2]/text()')
        for d, t in zip(days, times):
            _tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = ";".join(_tmp)

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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
