from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.lcegroup.co.uk"
base_url = "https://www.lcegroup.co.uk/Branch-Finder/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var locations")[1]
            .split("var map")[0]
            .strip()[1:-1]
        )
        for _ in locations:
            info = bs(_[0], "lxml")
            page_url = locator_domain + info.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(
                sp1.select_one("div.LblueBox > div> div> div > div").stripped_strings
            )
            addr_str = " ".join(addr)
            adr = " ".join(addr).split("tel")[0].strip()
            a = parse_address(International_Parser(), adr)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"

            if "click here" in addr[-1]:
                del addr[-1]

            if "mail" in addr[-1]:
                del addr[-1]

            phone = addr_str.split("tel:")[1].split("e-mail")[0].strip()
            hours = []
            temp = list(
                sp1.select("div.LblueBox > div> div> div > div")[1].stripped_strings
            )
            for x, hh in enumerate(temp):
                if (
                    hh.lower().startswith("opening times")
                    or hh == "Opening Hours"
                    or hh.lower() == "normal opening hours"
                ):
                    for hr in temp[x + 1 :]:
                        if (
                            "Holiday" in hr
                            or "Day" in hr
                            or "open" in hr
                            or "Christmas" in hr
                            or "Xmas" in hr
                            or "from" in hr
                        ):
                            break
                        if (
                            not hr.replace("Opening Hours", "")
                            .replace(":", "")
                            .replace("-", "")
                            .strip()
                        ):
                            continue
                        if "We're open" in hr:
                            continue
                        hours.append(hr.replace("Opening hours", ""))
                    break

            if not hours:
                for hh in temp:
                    _hh = hh.lower()
                    if (
                        "Please" in hh
                        or "Passport" in hh
                        or "years" in _hh
                        or "boxing" in _hh
                    ):
                        break
                    if "Normally" in hh or "Holiday" in hh:
                        break
                    if (
                        "december" in _hh
                        or "Dec" in hh
                        or "christmas" in _hh
                        or "xmas" in _hh
                        or "January" in hh
                        or "Day" in hh
                        or "th" in hh
                        or "seasonal" in _hh
                        or "31st" in _hh
                    ):
                        continue

                    if (
                        "Open:" in hh
                        or "Covid" in hh
                        or "Social" in hh
                        or "customer" in hh
                        or "Standard" in hh
                    ):
                        continue
                    if (
                        not hh.replace("Opening Hours", "")
                        .replace(":", "")
                        .replace("-", "")
                        .strip()
                    ):
                        continue
                    if "We're open" in hh or "We are now open" in hh or "Notice" in hh:
                        continue
                    hours.append(
                        hh.split("see")[-1]
                        .replace("Opening hours", "")
                        .replace("C L O S E D", "closed")
                    )
            hours_of_operation = "; ".join(hours)
            if phone.find("coming soon") != -1:
                hours_of_operation = "coming soon"
                phone = "<MISSING>"
            if hours_of_operation.find("; *Sunday") != -1:
                hours_of_operation = hours_of_operation.split("; *Sunday")[0].strip()
            if hours_of_operation.find("; Email") != -1:
                hours_of_operation = hours_of_operation.split("; Email")[0].strip()
            hours_of_operation = (
                hours_of_operation.replace(
                    "; Thursday 2/6/22 11:00-16:00; Friday 3/6/22 11:00-16:00", ""
                )
                .replace("; WE ARE CLOSED ON BANK HOLIDAYS", "")
                .replace("; BANK HOLIDAYS - CLOSED", "")
                .strip()
            )
            if hours_of_operation.find("; Platinum") != -1:
                hours_of_operation = hours_of_operation.split("; Platinum")[0].strip()
            if hours_of_operation.find("; Thursday 2nd June") != -1:
                hours_of_operation = hours_of_operation.split("; Thursday 2nd June")[
                    0
                ].strip()
            if hours_of_operation.find("; Thursday 2/6/22") != -1:
                hours_of_operation = hours_of_operation.split("; Thursday 2/6/22")[
                    0
                ].strip()
            if hours_of_operation.find("; We are open") != -1:
                hours_of_operation = hours_of_operation.split("; We are open")[
                    0
                ].strip()

            yield SgRecord(
                page_url=page_url,
                location_name=info.strong.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="UK",
                phone=phone,
                latitude=_[-3],
                longitude=_[-2],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=adr,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
