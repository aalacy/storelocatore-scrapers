from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.benefitcosmetics.com/"
base_url = "https://api.benefitcosmetics.com/us/en/rest/storelocator/stores/?callback=jQuery21307271565409387377_1612435828814&1612435889926&key=952e29aebf5cec744b2097e69fdfb2f3999d8d1c&lat=51.5073509&lng=-0.1277583&radius=50000&unit=km&language=en-GB&programId=&nbp=true&_=1612435828817"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _v(val):
    if val:
        return val.replace("\n", " ").replace("\r", "").replace("\t", "")
    return ""


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:

        rr = session.get(base_url, headers=_headers)
        locations = json.loads(
            rr.text.replace("jQuery21307271565409387377_1612435828814(", "")[:-2]
        )["results"]["stores"]
        for _ in locations:
            street_address = _["address_1"] or ""
            if _.get("address_2"):
                street_address += _["address_2"]
            if _.get("address_3"):
                street_address += _["address_3"]

            hours = []
            for day in days:
                day = day.lower()
                start = _.get(f"{day}_hrs_o")
                end = _.get(f"{day}_hrs_c")
                if start:
                    hours.append(f"{day}: {start} - {end}")

            country_code = _.get("country")
            if country_code:
                country_code = country_code.replace("TÃ¼rkiye", "Turkey")

            phone = _["phone"]
            if _p(country_code):
                if not phone:
                    phone = country_code
                country_code = ""

            zip_postal = _["postal_code"]
            if zip_postal == "Turkey":
                zip_postal = ""
            yield SgRecord(
                page_url="https://www.benefitcosmetics.com/en-us/find-a-store",
                location_name=_["name"],
                street_address=_v(street_address),
                city=_v(_["city"]),
                state=_v(_["state"]),
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=country_code,
                location_type=_["store_type"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
