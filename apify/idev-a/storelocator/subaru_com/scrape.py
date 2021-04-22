from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("subaru")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.subaru.com/"
    base_url = "https://www.subaru.com/services/dealers/distances/by/bounded-location?latitude=90&longitude=-90&neLatitude=90&neLongitude=-90&swLatitude=33.977430203277436&swLongitude=-122.17336933998703&count=-1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations:
            _ = loc["dealer"]
            street_address = _["address"]["street"]
            if _["address"]["street2"]:
                street_address += " " + _["address"]["street2"]
            logger.info(_["siteUrl"])
            hours = []
            try:
                _hr = json.loads(
                    session.get(_["siteUrl"], headers=_headers)
                    .text.split("['ws-hours']['hours1'] = ")[1]
                    .split("DDC.WS.state")[0]
                    .strip()[:-1]
                )
                for hh in _hr["hours"]["DEALERSHIP"]:
                    hours.append(f"{hh['day']}: {hh['timings']}")
            except:
                pass
            yield SgRecord(
                page_url=_["siteUrl"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zipcode"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code="US",
                phone=_["phoneNumber"].strip(),
                location_type=_["address"]["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
