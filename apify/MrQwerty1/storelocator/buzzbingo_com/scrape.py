from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    _zip = " ".join(line.split()[-2:])
    adr = parse_address(International_Parser(), line, postcode=_zip)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'initMap()')]/text()"))
    lat, lng = text.split(".LatLng(")[1].split("),")[0].split(",")
    hoo = ";".join(tree.xpath("//div[@class='times']//li/text()"))

    return lat, lng, hoo


def fetch_data(sgw: SgWriter):
    api = "https://club-api.buzzbingo.com/buzzapi/get_clubs"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "multipart/form-data; boundary=---------------------------3799747382567986838214268301",
    }
    data = '-----------------------------3799747382567986838214268301\r\nContent-Disposition: form-data; name="apiKey"\r\n\r\n5418a40c-d74c-4d58-a258-a086d4a952b9\r\n-----------------------------3799747382567986838214268301--\r\n'
    r = session.post(api, headers=headers, data=data)
    js = r.json()

    for j in js:
        location_name = j.get("club_name")
        page_url = j.get("club_url")
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)

        phone = j.get("telephone")
        store_number = j.get("hall_code")
        latitude, longitude, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://clubs.buzzbingo.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
