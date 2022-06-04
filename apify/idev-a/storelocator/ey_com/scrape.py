from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ey.com"
base_url = "https://www.ey.com/eydff/services/officeLocations.json"


def _c(_, page_url, street_address, state, zip_postal, country_code, phone):
    return SgRecord(
        page_url=page_url,
        location_name=_["name"],
        street_address=street_address.replace("\n", "").replace("\r", " "),
        city=_["officeCity"],
        state=state,
        zip_postal=zip_postal,
        latitude=_["officeLatitude"],
        longitude=_["officeLongitude"],
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
    )


def _d(_, data, state=""):
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
        zip_postal = " ".join(zip_postal.split()[1:]).strip()
    elif country_code == "SE":
        zip_postal = zip_postal.split(",")[-1].strip()
    elif country_code == "RS":
        zip_postal = zip_postal.split()[0].strip()

    phone = _.get("officePhoneNumber")
    if phone:
        phone = phone.split("/")[0].strip()

    _s = street_address.split("//")
    if len(_s) > 1:
        for ss in _s:
            if ss.strip():
                data.append(
                    _c(_, page_url, ss.strip(), state, zip_postal, country_code, phone)
                )
    else:
        data.append(
            _c(_, page_url, street_address, state, zip_postal, country_code, phone)
        )


def fetch_data():
    with SgRequests() as session:
        countries = session.get(base_url, headers=_headers).json()["countries"]
        data = []
        for country in countries:
            for state in country["states"]:
                for city in state["cities"]:
                    for _ in city["offices"]:
                        _d(_, data, state["name"])
            for city in country["cities"]:
                for _ in city["offices"]:
                    _d(_, data)

        return data


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
