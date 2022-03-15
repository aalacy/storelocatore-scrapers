from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("quizclothing")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.rocklandtrust.com"
branch_url = (
    "https://www.rocklandtrust.com/_/api/branches/42.1112995/-70.92925370000002/5000"
)
atm_url = "https://www.rocklandtrust.com/_/api/atms/42.1112995/-70.92925370000002/50"


def HOO(_hr, hours):
    tt = _hr.find_next_siblings("div")
    if not tt:
        tt = _hr.find_parent("div").find_next_siblings("div")

    for hh in tt:
        if not hh.text.strip():
            break
        for _hh in hh.stripped_strings:
            if "Hour" in _hh or "Drive" in _hh:
                break
            hours.append(_hh)


def HOO1(desc, hours):
    _hr = desc.find("", string=re.compile(r"Hours$"))
    if not _hr:
        _hr = desc.find("", string=re.compile(r"Hours:$"))
    if _hr:
        tt = _hr.find_parent("div")
        if not tt:
            tt = _hr
        if not tt.find_next_siblings("div"):
            tt = tt.find_parent("b")
        try:
            for hh in tt.find_next_siblings("div"):
                if not hh.text.strip() or "Hours" in hh.text:
                    break
                hours.append(hh.text.strip())
        except:
            pass
    else:
        _hr = desc.find("", string=re.compile(r"^Hours of Operation"))
        if _hr:
            try:
                if _hr.find_parent("div"):
                    for hh in _hr.find_parent("div").find_next_siblings("div"):
                        if not hh.text.strip() or "Hours" in hh.text:
                            break
                        hours.append(hh.text.strip())
            except:
                pass


def _d(_, session, page_url=None):
    location_type = "Rockland Trust"
    hours_of_operation = ""
    if "Branch" in _["name"]:
        location_type = "branch"
    elif "ATM" in _["name"]:
        location_type = "atm"
    if _.get("description"):
        desc = bs(_["description"], "lxml")
        page_url = desc.a["href"]
        hours = []

        HOO1(desc, hours)

        if not hours and location_type != "atm":
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _hr = sp1.find("strong", string=re.compile(r"Hours"))
            if _hr:
                HOO1(sp1, hours)

                if not hours:
                    HOO(_hr, hours)

        temp = []
        for hh in hours:
            for _hr in hh.split("\n"):
                if not _hr.strip() or "schedule" in hh.lower():
                    break
                temp.append(_hr)

        hours_of_operation = "; ".join(temp)
        if "CLOSED ON" in hours_of_operation:
            hours_of_operation = "Closed"
        if hours_of_operation:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

    return SgRecord(
        page_url=page_url,
        location_name=_["name"],
        street_address=_["address"],
        city=_["city"],
        state=_["state"],
        zip_postal=_["zip"],
        latitude=_["lat"],
        longitude=_["long"],
        country_code="US",
        phone=_.get("phone"),
        locator_domain=locator_domain,
        location_type=location_type,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    with SgRequests() as session:
        locations = session.get(branch_url, headers=_headers).json()["branches"]
        for _ in locations:
            yield _d(_, session)

        locations = session.get(atm_url, headers=_headers).json()["atms"]
        for _ in locations:
            yield _d(
                _,
                session,
                "https://www.rocklandtrust.com/about-us/get-in-touch/locations",
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
