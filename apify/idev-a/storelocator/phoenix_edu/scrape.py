from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("phoenix")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.phoenix.edu"
loc_url = "https://www.phoenix.edu/campus-locations.html"
base_url = "https://www.phoenix.edu/api/plct/3/uopx/locations?type=site&page.size=500"


def fetch_data():
    with SgRequests() as session:
        g_hours = []
        sp1 = bs(session.get(loc_url, headers=_headers).text, "lxml")
        ss = json.loads(
            sp1.select_one("div.react-campusdetailhero-container")[
                "data-json-properties"
            ]
            .replace("&#34;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        if ss["campusData"].get("hours"):
            g_hours = list(bs(ss["campusData"]["hours"], "lxml").stripped_strings)
            if "temporarily closed" in " ".join(g_hours):
                g_hours = ["temporarily closed"]
        locations = session.get(base_url, headers=_headers).json()["results"]
        for loc in locations:
            _ = loc["attributes"]
            street_address = _["addressLine2"]
            if _.get("addressLine3"):
                street_address += " " + _["addressLine3"]
            phone = ""
            if _.get("phoneLocal"):
                phone = _.get("phoneLocal").replace(".", "").replace("-", "").strip()
            if not phone and _.get("phoneTollFree"):
                phone = _.get("phoneTollFree").replace(".", "").replace("-", "").strip()
            yield SgRecord(
                page_url=loc_url,
                location_name=_["altName"],
                street_address=street_address,
                city=_["city"],
                state=_["stateProvince"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=loc["countryCode"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(g_hours),
            )

        locs = sp1.select("div.campus-dir-item")
        for loc in locs:
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in loc.select("span.campus-dir-item__hours-day")
            ]
            phone = ""
            if loc.select_one("div.campus-dir-item__phone a"):
                phone = (
                    loc.select_one("div.campus-dir-item__phone a")
                    .text.replace(".", "")
                    .replace("-", "")
                    .strip()
                )
            addr = loc.select_one("div.campus-dir-item__location a").text.split(",")
            coord = ["", ""]
            href = loc.select_one("div.campus-dir-item__location a")["href"]
            try:
                coord = href.split("/@")[1].split("/data")[0].split(",")
            except:
                try:
                    coord = href.split("query=")[1].split("&")[0].split(",")
                except:
                    pass
            yield SgRecord(
                page_url="https://www.phoenix.edu/campus-locations.html#additional-campus-directory",
                location_name=loc.h4.text.strip(),
                street_address=addr[0].replace("\r\n", ""),
                city=addr[1],
                state=addr[-1].strip().split()[0],
                zip_postal=addr[-1].strip().split()[-1],
                latitude=coord[0],
                longitude=coord[1],
                country_code="us",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.CITY, SgRecord.Headers.PHONE}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
