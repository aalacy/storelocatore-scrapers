from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import json
import time

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


days = {
    "Dimanche": "Sun",
    "Jeudi": "Thu",
    "Lundi": "Mon",
    "Mercredi": "Wed",
    "Samedi": "Sat",
    "Vendredi": "Fri",
    "Mardi": "Tue",
}


def fetch_data():
    locator_domain = "https://www.batonrouge.ca/"
    base_url = "https://www.batonrouge.ca/en/find-a-restaurant"
    json_url = "https://www.batonrouge.ca//service/search/branch"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url == json_url and rr.response:
                    exist = True
                    locations = json.loads(rr.response.body)
                    for _ in locations:
                        hours = []
                        for key, val in _["schedule"]["week"].items():
                            times = ["closed"]
                            if val["counter"]["range"]:
                                times = val["counter"]["range"][0].values()
                            hours.append(f"{days[key]}: {'-'.join(times)}")
                        yield SgRecord(
                            page_url=_["links"]["self"],
                            store_number=_["id"],
                            location_name=_["title"],
                            street_address=_["address"]["address"],
                            city=_["address"]["city"],
                            state=_["address"]["province"],
                            zip_postal=_["address"]["zip"],
                            country_code=_["address"]["country"],
                            phone=_["phone"],
                            latitude=_["lat"],
                            longitude=_["lng"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(hours),
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
