from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("resultspt")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.resultspt.com"


days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def fetch_data():
    locator_domain = "https://www.resultspt.com/"
    base_url = "https://www.resultspt.com/locations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        api_key = res.split("apiKey:")[1].split("shopKitApiUrl:")[0].strip()[1:-2]
        json_url = f"https://www.resultspt.com/swx/api/v2/locations/271799.json?api_key={api_key}"
        locations = session.get(json_url, headers=_headers).json()
        for _ in locations["Places"]:
            hours = []
            for hh in _["Hours"]:
                time = (
                    "Closed"
                    if not hh["OpenAt"] and not hh["CloseAt"]
                    else f"{hh['OpenAt']}-{hh['CloseAt']}"
                )
                hours.append(f"{days[hh['Day']]}: {time}")
            yield SgRecord(
                page_url=_["Url"],
                store_number=_["PlaceId"],
                location_name=_["Name"],
                street_address=_["Address"],
                city=_["City"],
                state=_["State"],
                latitude=_["CenterPointLat"],
                longitude=_["CenterPointLong"],
                zip_postal=_["Zipcode"],
                country_code=_["Country"],
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
