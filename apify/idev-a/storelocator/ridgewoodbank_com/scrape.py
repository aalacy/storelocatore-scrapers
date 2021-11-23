from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.ridgewoodbank.com/"
    base_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=59988490a310f6125098e7c4147e5ebf&jsLibVersion=v1.6.5&sessionTrackingEnabled=true&input=Locations%20near%20me&experienceKey=ridgewood_savings&version=PRODUCTION&filters=%7B%7D&facetFilters=%7B%7D&verticalKey=locations&limit=20&offset=0&retrieveFacets=true&locale=en&referrerPageUrl=https%3A%2F%2Fwww.ridgewoodbank.com%2F"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations["response"]["results"]:
            _ = loc["data"]
            hours = []
            for day, hh in _["hours"].items():
                if day == "holidayHours":
                    break
                times = "Closed"
                if not hh.get("isClosed"):
                    times = f"{hh['openIntervals'][0]['start']}-{hh['openIntervals'][0]['end']}"
                hours.append(f"{day}: {times}")
            yield SgRecord(
                page_url=_["websiteUrl"]["url"],
                store_number=_["id"],
                location_name=_["c_branchName"],
                street_address=_["address"]["line1"],
                city=_["address"]["city"],
                state=_["address"]["region"],
                zip_postal=_["address"]["postalCode"],
                latitude=_["geocodedCoordinate"]["latitude"],
                longitude=_["geocodedCoordinate"]["longitude"],
                country_code="US",
                phone=_["mainPhone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
