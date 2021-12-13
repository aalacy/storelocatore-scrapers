from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ey.com"
base_url = "https://www.ey.com/eydff/services/officeLocations.json"


def _d(_, state=""):
    page_url = locator_domain + "/en_gl" + _["href"]
    street_address = _["officeAddress"]
    if not street_address:
        street_address = _["translations"][0]["officeAddress"]
    country_code = _["officeCountryCode"]
    zip_postal = _.get("officePostalCode")
    if zip_postal:
        zip_postal = (
            zip_postal.replace(_["officeCountry"], "")
            .replace("Tortola", "")
            .replace("Umeå", "")
            .replace("Cedex", "")
            .replace("Frederiksberg", "")
            .replace("Aalborg", "")
            .replace(",", "")
            .strip()
        )
    if country_code in ["AU", "MX", "US"]:
        zip_postal = zip_postal.split()[-1].strip()
    elif country_code == "BS":
        zip_postal = ""
    elif country_code == "CA":
        zip_postal = " ".join(zip_postal.split()[:-2]).strip()
    elif country_code == "SE":
        zip_postal = zip_postal.split(",")[-1].strip()
    elif country_code == "RS":
        zip_postal = zip_postal.split()[0].strip()

    return SgRecord(
        page_url=page_url,
        location_name=_["name"],
        street_address=street_address.replace("\n", "").replace("\r", " "),
        city=_["officeCity"],
        state=state,
        zip_postal=zip_postal,
        latitude=_["officeLatitude"],
        longitude=_["officeLongitude"],
        country_code=_["officeCountryCode"],
        phone=_.get("officePhoneNumber"),
        locator_domain=locator_domain,
    )


def fetch_data():
    with SgRequests() as session:
        countries = session.get(base_url, headers=_headers).json()["countries"]
        for country in countries:
            for state in country["states"]:
                for city in state["cities"]:
                    for _ in city["offices"]:
                        yield _d(_, state["name"])
            for city in country["cities"]:
                for _ in city["offices"]:
                    yield _d(_)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
