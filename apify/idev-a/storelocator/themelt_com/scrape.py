from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import json
import time

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.themelt.com/"
    base_url = "https://www.themelt.com/locations"
    json_url = "https://www.themelt.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url.startswith(json_url) and rr.response:
                    exist = True
                    locations = json.loads(rr.response.body)
                    for _ in locations["result"]["items"]:
                        hours = []
                        if _["days_01"]:
                            hours.append(f"{_['days_01']}: {_['hours_01']}")
                        if _["days_02"]:
                            hours.append(f"{_['days_02']}: {_['hours_02']}")
                        if _["days_03"]:
                            hours.append(f"{_['days_03']}: {_['hours_03']}")
                        yield SgRecord(
                            page_url=base_url,
                            location_name=_["title"],
                            street_address=_["address"],
                            city=_["city"],
                            state=_["state"],
                            country_code="US",
                            phone=_["phone_number"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(hours),
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
