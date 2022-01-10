from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("coffeetime")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.coffeetime.com"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=YDGUJSNDOUAFKPRL&center=43.696891,-79.371536&coordinates=43.06810520271273,-78.26878331445297,44.31915170663851,-80.47428868554653&multi_account=false&page={}&pageSize=300"
days = ["", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            links = session.get(base_url.format(page), headers=_headers).json()
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")

            for _ in links:
                page_url = "https://locations.coffeetime.com" + _["llp_url"]
                if _["open_or_closed"] == "coming soon":
                    continue
                hours = []
                for hh in _["store_info"]["hours"].split(";"):
                    if not hh:
                        continue
                    time1 = hh.split(",")[1][:2] + ":" + hh.split(",")[1][2:]
                    time2 = hh.split(",")[2][:2] + ":" + hh.split(",")[2][2:]
                    hours.append(f"{days[int(hh.split(',')[0])]}: {time1}-{time2}")

                if not hours:
                    hours = ["Mon-Sun: Closed"]

                info = _["store_info"]
                location_name = ""
                for nn in _["custom_fields"]:
                    if nn["name"] == "StoreName":
                        location_name = nn["data"]
                        break
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=f"{info['address']} {info.get('address_extended', '')} {info.get('address3', '')}".strip(),
                    city=info["locality"],
                    state=info["region"],
                    zip_postal=info["postcode"],
                    country_code=info["country"],
                    phone=info["phone"],
                    latitude=info["latitude"],
                    longitude=info["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
