from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_phone(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    line = tree.xpath(
        "//div[@class='carousel-card__contact']//a[contains(@class, 'phone-number')]/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))

    return line.pop()


def fetch_data(sgw: SgWriter):
    api = "https://www.theofficegroup.com/graphql?operationName=BUILDINGS&variables=%7B%22language%22%3A%22EN%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%227cce8052e3508c217b7beaaa8ec971890a5675addf6026febca6fd359b040bcd%22%7D%7D"
    r = session.get(api, headers=headers)
    js = r.json()["data"]["buildings"]["entities"]

    for j in js:
        a = j.get("address") or {}
        adr1 = a.get("line1") or ""
        adr2 = a.get("line2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("locality")
        postal = a.get("postcode")
        country_code = a.get("countryCode")
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j["url"]["alias"]
        page_url = f"https://www.theofficegroup.com{slug}"
        phone = get_phone(page_url)

        g = j.get("geolocation") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.theofficegroup.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
