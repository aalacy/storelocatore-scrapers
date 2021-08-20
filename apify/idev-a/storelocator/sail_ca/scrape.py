from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.sail.ca/en/our-stores",
    "x-newrelic-id": "VgQGUVZSCBACV1JVBQcOX1A=",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sail.ca/"
    base_url = "https://www.sail.ca/en/store/locator/ajaxlist/?loaded=0&_=1617736439840"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["list"]:
            hours = []
            for hh in json.loads(_["opening_hours"]):
                time = f"{hh['open']}-{hh['close']}"
                if not hh["open"] and not hh["close"]:
                    hours = ["Temporarily closed"]
                    break
                hours.append(f"{hh['dayLabel']}: {time}")

            yield SgRecord(
                page_url=_["additional_attributes"]["url_key"],
                location_name=_["name"],
                street_address=_["address"][0],
                city=_["city"],
                state=_["region"],
                zip_postal=_["postcode"],
                country_code=_["country_id"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
