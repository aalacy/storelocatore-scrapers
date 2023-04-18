from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

logger = SgLogSetup().get_logger("baartprograms")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

locator_domain = "https://baartprograms.com/"
base_url = "https://baartprograms.com/locations/"


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var baartSite = ")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )["locations"]
        for _ in locations:
            hours = []
            info = bs(_["location_messages"], "lxml")
            page_url = info.a["href"].strip().split()[0]
            if page_url:
                logger.info(page_url)
                res = session.get(page_url, headers=_headers)
                try:
                    res.url
                except:
                    import pdb

                    pdb.set_trace()
                if res.url.__str__() != "https://medmark.com/":
                    page_url = res.url.__str__()
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
                        elif sp1.select_one("div.sidebar-info-time p"):
                            hours = list(
                                sp1.select_one(
                                    "div.sidebar-info-time p"
                                ).stripped_strings
                            )[1:]
                        elif sp1.find("span", string=re.compile(r"OPERATING HOURS")):
                            for hh in (
                                sp1.find("span", string=re.compile(r"OPERATING HOURS"))
                                .find_parent("p")
                                .find_next_siblings("p")
                            ):
                                if not hh.text.strip():
                                    continue
                                hours.append(hh.text.strip())
                        elif sp1.select("div.uabb-infobox-text.uabb-text-editor"):
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
                        else:
                            pass

            yield SgRecord(
                page_url=page_url,
                store_number=_["location_id"],
                location_name=_["location_title"],
                street_address=list(info.stripped_strings)[0].split("\n")[0].strip(),
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
