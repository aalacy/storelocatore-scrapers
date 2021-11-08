from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode
    if "Ingeldorf" in line:
        city = "Ingeldorf"
        street_address = line.split(city)[0].strip()[:-1]

    return street_address, city, state, postal


def get_geo(text):
    if "ll=" in text:
        lat = text.split("ll=")[1].split(",")[0].strip()
        lng = text.split("ll=")[1].split(",")[1].split("&")[0].strip()
        return lat, lng
    return SgRecord.MISSING, SgRecord.MISSING


def fetch_data(sgw: SgWriter):
    for store_number in range(1, 1000):
        page_url = f"https://mcd.lu/content.php?r=1_{store_number}&lang=de"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text.replace("<!--", "").replace("-->", ""))
        location_name = "".join(tree.xpath("//h1/text()")).strip()
        if not location_name:
            break
        if tree.xpath("//h1[@style='color: red;']"):
            continue
        phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()

        _tmp = []
        lines = tree.xpath("//h2[text()='Adresse']/following-sibling::text()")
        for line in lines:
            if not line.strip():
                continue
            if "Tel" in line:
                break
            _tmp.append(line.strip())

        ad = ", ".join(_tmp)
        street_address, city, state, postal = get_international(ad)
        text = "".join(tree.xpath("//iframe/@src"))
        latitude, longitude = get_geo(text)
        hours_of_operation = ";".join(
            tree.xpath("//meta[@itemprop='openingHours']/@content")
        )
        if store_number == 10:
            hours_of_operation = ";".join(
                tree.xpath("//meta[@itemprop='openingHours']/@content")[2:]
            )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="LU",
            store_number=str(store_number),
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://mcd.lu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
