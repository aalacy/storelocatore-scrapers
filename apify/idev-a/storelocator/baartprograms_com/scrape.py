from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

logger = SgLogSetup().get_logger("baartprograms")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://baartprograms.com/"
    base_url = "https://baartprograms.com/locations/"
    with SgRequests(proxy_country="us") as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var baartSite = ")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )["locations"]
        for _ in locations:
            hours = []
            page_url = (
                _["location_extrafields"].get("url")
                if _["location_extrafields"]
                else ""
            )
            if page_url:
                logger.info(page_url)
                res = session.get(page_url, headers=_headers)
                if res.url.__str__() != "https://medmark.com/":
                    sp1 = bs(res.text, "lxml")
                    try:
                        ss = json.loads(
                            sp1.find_all("script", type="application/ld+json")[
                                -1
                            ].string
                        )
                        for hh in ss.get("openingHoursSpecification", []):
                            if type(hh["dayOfWeek"]) == list:
                                day = f"{hh['dayOfWeek'][0]} - {hh['dayOfWeek'][-1]}"
                            else:
                                day = hh["dayOfWeek"]
                            hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
                    except:
                        if sp1.select("div.treatment-work"):
                            for hh in sp1.select("div.treatment-work")[0].select(
                                "div.tw-item"
                            ):
                                if "Holiday" in hh.text:
                                    break
                                hours.append(" ".join(hh.stripped_strings))
                        else:
                            temp = list(
                                sp1.select("div.uabb-infobox-text.uabb-text-editor")[
                                    1
                                ].stripped_strings
                            )
                            hh = []
                            for hr in temp:
                                hh.append(hr)
                                if hr[0].isdigit():
                                    hours.append(hh)
                                    hh = []

            yield SgRecord(
                page_url=page_url,
                store_number=_["location_id"],
                location_name=_["location_title"],
                street_address=list(
                    bs(_["location_messages"], "lxml").stripped_strings
                )[0]
                .split("\n")[0]
                .strip(),
                city=_["location_address"].split(",")[-3],
                state=_["location_state"],
                zip_postal=_["location_postal_code"],
                latitude=_["location_latitude"],
                longitude=_["location_longitude"],
                country_code="US",
                phone=_["location_extrafields"].get("phone")
                if _["location_extrafields"]
                else "",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["location_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
