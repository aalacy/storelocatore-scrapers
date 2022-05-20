from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("purehockey")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.purehockey.com"
base_url = "https://www.purehockey.com/storelocator.aspx"


def fetch_data():
    with SgRequests() as session:
        locations = (
            session.get(base_url, headers=_headers)
            .text.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#039;", '"')
            .replace("&quot;", '"')
            .split("addMarker(")[2:]
        )
        for loc in locations:
            _ = json.loads(
                loc.split(");")[0]
                .replace("new google.maps.LatLng(", '"')
                .replace("), type", '", type')
            )
            info = bs(_["content"], "lxml")
            addr = list(info.select_one("div.address").stripped_strings)
            coord = _["position"].split(",")
            page_url = locator_domain + info.select_one(".store-name").a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            days = sp1.select("div#hours dt")
            times = sp1.select("div#hours dd")
            for x in range(len(days)):
                if times[x].text.strip() == "Regular Hours":
                    for y in range(len(days[x + 1 :])):
                        hours.append(
                            f"{days[x+y+1].text.strip()}: {times[x+y+1].text.strip()}"
                        )
                    break
                else:
                    for y in range(len(days)):
                        hours.append(
                            f"{days[x+y].text.strip()}: {times[x+y].text.strip()}"
                        )
                    break

            yield SgRecord(
                page_url=page_url,
                store_number=_["loc_id"],
                location_name=info.select_one(".store-name").text.strip(),
                street_address=" ".join(addr[:-1]).replace(
                    "Centene Community Ice Center", ""
                ),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
                phone=info.select_one(".phone").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr).replace("Centene Community Ice Center", ""),
            )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
