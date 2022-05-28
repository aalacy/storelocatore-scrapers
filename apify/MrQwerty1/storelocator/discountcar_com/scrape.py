import pycountry
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://prd.location.enterprise.com/enterprise-sls/search/location/enterprise/web/spatial/33.6166689358116/-90.88632923713895?rows=15000&cor=US&radius=50000"
    r = session.get(api, headers=headers)
    js = r.json()["locationsResult"]

    for j in js:
        location_name = j.get("locationNameTranslation")
        location_type = j.get("locationType")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phoneNumber")
        store_number = j.get("groupBranchNumber")
        line = j.get("addressLines") or []
        street_address = ", ".join(line)
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postalCode")
        country = j.get("countryCode") or ""
        country_name = (
            pycountry.countries.get(alpha_2=country)
            .name.replace("é", "e")
            .replace(" ", "-")
        )
        if "Viet" in country_name:
            country_name = "Vietnam"

        if country == "US":
            page_url = f"https://www.enterprise.com/en/car-rental/locations/{country}/{state}/-{store_number}.html".lower()
        elif country == "GB":
            page_url = f"https://www.enterprise.com/en/car-rental/locations/uk/-{store_number}.html".lower()
        else:
            page_url = f"https://www.enterprise.com/en/car-rental/locations/{country_name}/-{store_number}.html".lower().replace(
                "virgin-islands,-british", "tortola"
            )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
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
            location_type=location_type,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.enterprise.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
