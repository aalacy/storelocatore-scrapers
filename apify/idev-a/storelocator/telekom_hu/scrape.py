from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

headers1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.telekom.hu"
base_url = (
    "https://www.telekom.hu/lakossagi/ugyintezes/elerhetosegek/uzleteink/uzletkereso"
)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        regions = soup.select("select#selectRegion option")
        for region in regions:
            data = {
                "appid": "tpontkereso",
                "nextpage": "searchformwithresult",
                "selectedRegionID": str(region.get("value")),
                "selectedCity": "(Összes város)",
                "selectedTodo": "tm",
                "servicecategory_tm_1": "on",
                "servicecategory_tm_2": "on",
                "servicecategory_tm_4": "on",
            }
            locations = bs(
                session.post(base_url, headers=headers1, data=data).text, "lxml"
            ).select("table.makeClickable tr")
            logger.info(f"{region.text}, {len(locations)}")
            for _ in locations:
                if not _.th:
                    continue
                page_url = (
                    "https://www.telekom.hu/lakossagi/ugyintezes/elerhetosegek/uzleteink/"
                    + _.a["href"]
                )
                raw_address = (
                    _.select("td")[1]
                    .strong.text.split("(")[0]
                    .split("áruház")[-1]
                    .split("üzletház")[-1]
                    .split("bevásárlóközpont")[-1]
                    .split("Központ")[-1]
                    .strip()
                )
                addr = raw_address.split(",")
                coord = (
                    _.select("td")[1].a["href"].split("?q=")[1].split("&")[0].split("+")
                )
                phone = (
                    list(_.select("td")[1].stripped_strings)[1].split(")")[-1].strip()
                )
                if phone == "Térkép":
                    phone = ""
                hours = []
                for hh in _.select("td")[2].select("ul li"):
                    hours.append(" ".join(hh.stripped_strings))

                yield SgRecord(
                    page_url=page_url,
                    location_name=" ".join(list(_.th.stripped_strings)[:-1]),
                    street_address=" ".join(addr[1:]),
                    city=" ".join(addr[0].split()[1:]),
                    zip_postal=addr[0].split()[0].strip(),
                    location_type=", ".join(
                        _.select_one("ul.listSquareMag").stripped_strings
                    ),
                    country_code="Hungary",
                    latitude=coord[0],
                    longitude=coord[1],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
