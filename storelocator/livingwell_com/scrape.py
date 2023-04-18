from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("livingwell")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.livingwell.com"
base_url = "https://www.livingwell.com/clubs/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("section.section-finder-alphabetical > a")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            hours = []
            if "www.livingwell.com" not in page_url:
                street_address = list(
                    sp1.select_one("div.street-block").stripped_strings
                )[1:]
                city = sp1.select_one("div.locality").text.strip()
                state = sp1.select_one("div.state").text.strip()
                zip_postal = sp1.select_one("div.postal-code").text.strip()

                addr = street_address + list(
                    sp1.select_one("div.addressfield-container").stripped_strings
                )
                if sp1.find("p", string=re.compile(r"^call", re.I)):
                    phone = (
                        sp1.find("p", string=re.compile(r"^call", re.I))
                        .text.replace(":", "")
                        .replace("Call", "")
                        .strip()
                    )
                hr = sp1.find("strong", string=re.compile(r"^Opening hours", re.I))
                if hr:
                    for pp in hr.find_parent().find_next_siblings("p"):
                        if "Health Club" in pp.text:
                            hours = list(pp.stripped_strings)[1:]
                            break
                coord = (
                    sp1.select_one("section.map-layout iframe")["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=" ".join(street_address),
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=addr[-1],
                    phone=phone,
                    latitude=coord[1],
                    longitude=coord[0],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )
            else:
                if sp1.select(
                    "section.section-club-visit div.col-md-offset-2 div.row div.col-md-6"
                )[0].p:
                    for hr in list(
                        sp1.select_one(
                            "section.section-club-visit div.col-md-offset-2 div.row div.col-md-6"
                        ).select("p")
                    ):
                        for hh in hr.stripped_strings:
                            _hh = hh.lower()
                            if "club" in _hh or "gym" in _hh or "fitness" in _hh:
                                continue
                            if (
                                "weekend" in _hh
                                or "holiday" in _hh
                                or "children" in _hh
                                or "spa" in _hh
                                or "please" in _hh
                                or "wellness" in _hh
                                or "will" in _hh
                                or "pool" in _hh
                                or "adult" in _hh
                                or "swimming" in _hh
                                or "booking" in _hh
                                or "prior" in _hh
                            ):
                                break
                            hours.append(
                                hh.split("If")[0].split("from")[0].replace("*", "")
                            )
                raw_address = " ".join(
                    list(
                        sp1.select(
                            "section.section-club-visit div.col-md-offset-2 div.row div.col-md-6"
                        )[1].p.stripped_strings
                    )
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if sp1.find("a", href=re.compile(r"tel:")):
                    phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=street_address.split("Hotel")[0]
                    .split("Hydro")[-1]
                    .split("Metropole")[-1]
                    .split("Airport")[-1]
                    .replace("Hilton Leeds City", "")
                    .replace("Hilton London Wembley", "")
                    .replace("Hilton Malta", "")
                    .replace("Hilton Newcastle Gateshead", "")
                    .replace("Hilton Nottingham", "")
                    .replace("Hilton Reading", "")
                    .replace("Hilton Watford", "")
                    .replace("Kallima Club & Spa Hilton London", "")
                    .replace("Livingwell Health Club Hilton Dublin Kilmainham", "")
                    .replace("The Caledonian", "")
                    .replace("Doubletree By Hilton Dartford Bridge", "")
                    .strip(),
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=addr.country,
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
