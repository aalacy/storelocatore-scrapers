from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[@id='tablepress-1']/tbody/tr")

    for d in divs:
        location_name = city = "".join(d.xpath("./td[1]//text()")).strip()
        if "(" in city:
            city = city.split("(")[0].strip()
        street_address = "".join(d.xpath("./td[2]//text()")).strip()
        if city in street_address:
            street_address = street_address.replace(city, "").strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = "".join(d.xpath("./td[3]//text()")).strip()
        postal = "".join(d.xpath("./td[4]//text()")).strip()
        country_code = "US"
        phone = "".join(d.xpath("./td[5]//text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.tapiocaexpress.com/"
    page_url = "https://www.tapiocaexpress.com/list-of-franchisees/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
