from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("andiamoitalia")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://andiamoitalia.com/"
    page_url = "https://www.amplehills.com/in-stores"
    base_url = "https://1v8tcmfe.apicdn.sanity.io/v1/data/query/production?query=*%5B_type%20%3D%3D%20%27retailLocation%27%5D%20%7B%0A%20%20_id%2C%0A%20%20_createdAt%2C%0A%20%20name%2C%0A%20%20address%2C%0A%20%20city%2C%0A%20%20state%2C%0A%20%20zip%2C%0A%20%20geopoint%2C%0A%20%20distributor%2C%0A%20%20tags%5B%5D-%3E%7B%20...%20%7D%0A%7D"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        logger.info(f"{len(locations['result'])} found")
        for _ in locations["result"]:
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code="US",
                latitude=_["geopoint"]["lat"],
                longitude=_["geopoint"]["lng"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
