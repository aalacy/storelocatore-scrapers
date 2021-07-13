from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("truefoodkitchen")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.truefoodkitchen.com/"
    base_url = "https://www.truefoodkitchen.com/locations/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var locations =")[1].split("var path =")[0].strip()[:-1]
        )
        for _ in locations:
            if _["status"] == "coming soon":
                continue
            res = session.get(_["link"], headers=_headers).text
            momentFeedID = (
                res.split("var momentFeedID = ")[1].split("</script>")[0].strip()[1:-2]
            )
            logger.info(_["link"])
            hours = []
            try:
                if momentFeedID:
                    detail_url = f"https://api.momentfeed.com/v1/lf/location/store-info/{momentFeedID}?auth_token=IFWKRODYUFWLASDC"
                    detail = session.get(detail_url, headers=_headers).json()
                    for x, hh in enumerate(detail["hours"].split(";")):
                        if not hh:
                            continue
                        start = hh.split(",")[1]
                        start = start[:2] + ":" + start[2:]
                        end = hh.split(",")[2]
                        end = end[:2] + ":" + end[2:]
                        hours.append(f"{days[x]}: {start}-{end}")
                else:
                    soup = bs(res, "lxml")
                    temp = list(soup.select_one("span.hours-card").stripped_strings)
                    for x in range(0, len(temp), 2):
                        day = temp[x]
                        start_end = temp[x + 1]
                        hours.append(f"{day}: {start_end}")

                hours_of_operation = "; ".join(hours)
                if _["status"] != "open":
                    hours_of_operation = "Closed"
                yield SgRecord(
                    page_url=_["link"],
                    store_number=_["post_id"],
                    location_name=_["title"].split("(")[0],
                    street_address=_["street"],
                    city=_["city"],
                    state=_["state"],
                    latitude=_["geo"][0],
                    longitude=_["geo"][1],
                    zip_postal=_["zip"],
                    country_code="US",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
