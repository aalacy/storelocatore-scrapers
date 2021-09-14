from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("kallkwik")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.kallkwik.co.uk"
base_url = "https://www.kallkwik.co.uk/home/contact/"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "select#choose_centre option"
    )
    for loc in locs:
        if not loc.get("value"):
            continue
        url = locator_domain + loc["value"]

        state.push_request(SerializableRequest(url=url, context={"name": loc.text}))

    return True


def _aa(_addr):
    addr = parse_address_intl(_addr)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return street_address, addr.city, addr.state, addr.postcode


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        sp1 = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        hours = (
            zip_postal
        ) = city = state = street_address = phone = _addr = latitude = longitude = ""
        if sp1.select_one("div.locationPageDetails"):
            _ = sp1.select_one("div.locationPageDetails")
            raw_address = list(_.p.stripped_strings)
            _addr = " ".join(raw_address).split(")")[-1].split("Please")[0].strip()
            street_address, city, state, zip_postal = _aa(_addr + ", UK")
            zip_postal = raw_address[-1].split("Please")[0]
            if "Tel" in _.select("p")[1].text:
                phone = _.select("p")[1].text.split(":")[-1].strip()
            _hr = list(_.select_one("div.right").stripped_strings)
            if _hr:
                hours = (
                    _hr[1]
                    .split("Office Hours")[-1]
                    .split("Leatherhead")[0]
                    .split("PLEASE")[0]
                    .split("However")[0]
                    .split("Currently")[0]
                    .split("excluding")[0]
                    .split("(")[0]
                    .split("- For")[0]
                    .replace("\n", "")
                    .replace("\r", " ")
                    .strip()
                )
        elif sp1.select_one("div.address-line"):
            raw_address = list(sp1.select_one("div.address-line p").stripped_strings)
            _addr = raw_address[0]
            street_address, city, state, zip_postal = _aa(_addr)
            if len(raw_address) > 1:
                phone = raw_address[1].split("number")[-1].strip()
        elif sp1.select_one("div#footerAddressDetails"):
            raw_address = sp1.select_one(
                "div#footerAddressDetails div.registered"
            ).text.split(":")
            phone = sp1.select_one("div.tel").text.strip()
            _addr = raw_address[1].replace("Registered number", "").strip()
            if "xx" in _addr.lower():
                _addr = ""
            street_address, city, state, zip_postal = _aa(_addr + ", UK")
        elif sp1.select_one("div.contact-map"):
            coord = (
                sp1.select_one("div.contact-map iframe")["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
            latitude = coord[1]
            longitude = coord[0]
            _addr = list(
                sp1.select_one("div.contact-map")
                .find_next_sibling("p")
                .stripped_strings
            )[0]
            street_address, city, state, zip_postal = _aa(_addr)
            _hr = sp1.find("h3", string=re.compile(r"Opening hours"))
            if _hr:
                temp = list(_hr.find_next_sibling().stripped_strings)
                hh = []
                for x in range(0, len(temp), 2):
                    hh.append(f"{temp[x]} {temp[x+1]}")
                hours = "; ".join(hh)
            phone = sp1.select_one("p.social a").text.split("ON")[-1].strip()
        elif sp1.select_one("div#mainfooter"):
            street_address = sp1.select_one('span[itemprop="streetAddress"]').text
            city = sp1.select_one('span[itemprop="addressLocality"]').text
            state = sp1.select_one('span[itemprop="addressRegion"]').text
            zip_postal = sp1.select_one('span[itemprop="postalCode"]').text
            _addr = " ".join(
                sp1.select_one('span[itemprop="name"]').find_parent().stripped_strings
            )
        else:
            continue

        if street_address:
            street_address = street_address.replace(",", " ").strip()
            if street_address.endswith("-"):
                street_address = street_address[:-1].strip()
        if phone:
            phone = phone.split("ring")[-1].split("t.")[-1].split("/")[0].strip()
        yield SgRecord(
            page_url=next_r.url,
            location_name=next_r.context.get("name"),
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code="uk",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours,
            raw_address=_addr,
        )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
