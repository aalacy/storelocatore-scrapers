import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.needs.ca/en/store-locator/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//div[contains(@class, 'store-result')]")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='name']/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='store-title']/@href"))
        store_number = "".join(d.xpath("./@data-id"))
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))

        street_address = ", ".join(
            d.xpath(".//span[contains(@class, 'location_address_address')]/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@class='city']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='province']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='postal_code']/text()")).strip()
        country_code = "CA"
        phone = "".join(d.xpath(".//span[@class='phone']/a/text()")).strip()

        _tmp = []
        text = "".join(d.xpath("./@data-hours")) or "{}"
        j = json.loads(text)
        for day, inter in j.items():
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.needs.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
