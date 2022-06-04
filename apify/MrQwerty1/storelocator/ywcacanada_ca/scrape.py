from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    coords = dict()
    data = {"action": "get_associations"}
    r = session.post("https://ywcacanada.ca/wp-admin/admin-ajax.php", data=data)
    js = r.json()

    for j in js:
        _id = str(j.get("association_id"))
        lat = j.get("lat")
        lng = j.get("lng")
        coords[_id] = (lat, lng)

    return coords


def fetch_data(sgw: SgWriter):
    coords = get_coords()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='association']")

    for d in divs:
        line = d.xpath(".//div[@class='association-address']/text()")
        line = list(filter(None, [li.strip() for li in line]))
        postal = line.pop()
        city = line.pop()
        if "," in city:
            city = city.split(",")[0].strip()

        street_address = " ".join(line)
        state = "".join(d.xpath("./parent::div/preceding-sibling::div/text()")).strip()
        country_code = "CA"
        store_number = "".join(d.xpath(".//a/@data-id"))
        location_name = "".join(
            d.xpath(".//div[@class='association-title']/text()")
        ).strip()
        latitude, longitude = coords.get(store_number) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://ywcacanada.ca/"
    page_url = "https://ywcacanada.ca/find-your-ywca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
