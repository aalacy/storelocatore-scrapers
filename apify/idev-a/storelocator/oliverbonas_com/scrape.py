from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from datetime import datetime

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oliverbonas.com"
base_url = "https://www.oliverbonas.com/us/api/n/bundle?requests=%5B%7B%22type%22%3A%22block%22%2C%22filter%22%3A%7B%22url%22%3A%22meta-block%40page_1248%22%7D%2C%22verbosity%22%3A1%2C%22action%22%3A%22find%22%2C%22children%22%3A%5B%7B%22_reqId%22%3A0%7D%5D%7D%2C%7B%22type%22%3A%22store%22%2C%22verbosity%22%3A1%2C%22filter%22%3A%7B%22verbosity%22%3A1%2C%22id%22%3A%7B%22%24nin%22%3A%5B%5D%7D%7D%2C%22action%22%3A%22find%22%2C%22children%22%3A%5B%7B%22_reqId%22%3A1%7D%5D%7D%5D"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        locations = session.get(base_url, headers=_headers).json()["catalog"]
        for _ in locations:
            hours = []
            temp = {}
            for key, hh in _.get("days", {}).items():
                day = datetime.strptime(key, "%Y-%m-%d").strftime("%A")
                if hh["status"] == 2:
                    times = "close"
                elif hh.get("open"):
                    times = f"{hh['open']} - {hh['close']}"
                else:
                    times = "-"
                temp[day] = times
            for day in days:
                hours.append(f"{day}: {temp.get(day)}")

            if (
                "We’re keeping this store closed" in _["store_name"]
                or "currently closed" in _["store_name"]
            ):
                hours = ["temporarily_closed"]
            street_address = _["address"].split("London")[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=locator_domain + "/us" + _["url"],
                store_number=_["id"],
                location_name=_["store_name"].split("-")[0].strip(),
                street_address=street_address,
                city=_["city"],
                state=_.get("state"),
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country_id"],
                phone=_["phone"],
                location_type=_["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
