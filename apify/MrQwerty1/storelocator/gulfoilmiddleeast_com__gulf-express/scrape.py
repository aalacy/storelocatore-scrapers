from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def fetch_data(sgw: SgWriter):
    api = "https://gulfoilmiddleeast.com/gulfexpress/map2.php"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    cities = tree.xpath("//ul[@id='tab']/li/a/text()")
    tabs = tree.xpath("//div[@class='tab_icerik']")

    coords = dict()
    text = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = text.split("var locations =")[1].split("];")[0].strip()[:-1] + "]"
    blocks = eval(text)
    for b in blocks:
        source, lat, lng, _id = b
        t = html.fromstring(source)
        name = "".join(t.xpath(".//b[1]/text()")).strip()
        coords[name] = {"lat": lat, "lng": lng, "_id": _id}

    for city, tab in zip(cities, tabs):
        divs = tab.xpath("./div")

        for d in divs:
            location_name = "".join(d.xpath(".//h2//text()")).strip()
            raw_address = "".join(
                d.xpath(".//h2/following-sibling::p[1]/text()")
            ).strip()
            street_address = get_street(raw_address)
            country_code = "AE"
            phone = "".join(d.xpath(".//a[@class='mapphone']/text()"))
            location_type = "".join(
                d.xpath(".//b[contains(text(), 'Location')]/following-sibling::text()")
            ).strip()
            if location_type.endswith(","):
                location_type = location_type[:-1]

            j = coords.get(location_name) or {}
            store_number = j.get("_id")
            latitude = j.get("lat")
            longitude = j.get("lng")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                location_type=location_type,
                store_number=store_number,
                raw_address=raw_address,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gulfoilmiddleeast.com/"
    page_url = "https://www.gulfoilmiddleeast.com/gulf-express/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
