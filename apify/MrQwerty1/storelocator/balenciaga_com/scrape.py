from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, city, state, postal):
    adr = parse_address(
        International_Parser(), line, city=city, state=state, postcode=postal
    )
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_countries():
    r = session.get(
        "https://www.balenciaga.com/en-en/storelocator?showMap=true&horizontalView=true&isForm=true"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@id='country']/option[@value!='']/@value")


def fetch_data(sgw: SgWriter):
    countries = get_countries()

    for country in countries:
        api_url = f"https://www.balenciaga.com/on/demandware.store/Sites-BAL-INTL-Site/en_ZW/Stores-FindStoresData?countryCode={country}"
        r = session.get(api_url)
        js = r.json()["storesData"]["stores"]

        for j in js:
            line = f"{j.get('address1')} {j.get('address2') or ''}".replace(
                "\n", ", "
            ).strip()

            city = j.get("city") or ""
            city = city.replace("(S)", "").strip()
            state = j.get("stateCode") or ""
            postal = j.get("postalCode") or ""

            street_address, city, state, postal = get_international(
                line, city, state, postal
            )

            if postal.count("0") == 5:
                postal = SgRecord.MISSING
            raw_address = " ".join(f"{line} {city} {state} {postal}".split())
            country_code = j.get("countryCode")
            store_number = j.get("ID")
            page_url = j.get("detailsUrl")
            location_name = j.get("storeName")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            if country_code == "JP":
                street_address = line

            _tmp = []
            hours = j.get("openingHours") or {}
            for day, h in hours.items():
                inter = h.get("openFromTo") or ""
                if "DATA" in inter:
                    inter = "Closed"
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
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.balenciaga.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
