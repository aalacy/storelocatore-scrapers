from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.reiss.com"
    base_url = "https://www.reiss.com/us/stores/all/"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["data"]:
            page_url = locator_domain + _["url"]
            city = _["city"].split(",")[0].strip()
            state = ""
            if len(_["city"].split(",")) == 2:
                state = _["city"].split(",")[-1].strip()
            hours = []
            for hh in _.get("openingtimes", []):
                hours.append(f"{hh['days']}: {hh['time']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=city,
                state=state,
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phonenumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
