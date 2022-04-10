from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    postal = adr.postcode

    return street_address, city, postal


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.cemexdominicana.com/documents/46744215/46744967/places.json/b6bbe959-349b-c052-51c5-f229d006ded9",
        "https://www.cemexcostarica.com/documents/46130096/46404811/places.json/daa21376-2828-420e-2cfe-5cda6de79d10",
        "https://www.cemex.com.eg/documents/46936376/46950212/places_eg-17012020.json/e0a8f26d-b9c9-00a8-cad2-489b91416d21",
        "https://www.cemex.ae/documents/47051412/47052168/places_uae.json/b7d1db36-99bc-5a9e-1118-f556a4be7b69",
    ]
    for api in apis:
        locator_domain = "/".join(api.split("/")[:3])
        country = "AE"
        if "dominicana" in locator_domain:
            country = "DO"
        elif "costa" in locator_domain:
            country = "CR"
        elif ".eg" in locator_domain:
            country = "EG"

        page_url = f"{locator_domain}/locations"
        r = session.get(api, headers=headers)
        for j in r.json():
            location_name = j.get("name")
            store_number = j.get("id")
            raw_address = j.get("address")
            street_address, city, postal = get_international(raw_address)
            state = j.get("states")

            latitude = j.get("latitude")
            longitude = j.get("longitude")

            source = j.get("phone") or "<html></html>"
            tree = html.fromstring(source)
            try:
                phone = tree.xpath("//a/text()")[0].strip()
            except IndexError:
                phone = SgRecord.MISSING

            row = SgRecord(
                location_name=location_name,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
