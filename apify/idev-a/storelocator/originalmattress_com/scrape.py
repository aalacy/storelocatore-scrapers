from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("originalmattress")


def _p(val):
    return val.strip().split(":")[-1].replace("Phone", "")


def fetch_data():
    locator_domain = "https://www.originalmattress.com/"
    base_url = "https://www.originalmattress.com/find-a-store"
    with SgRequests() as session:
        store_list = json.loads(
            bs(session.get(base_url).text, "lxml")
            .select_one("input#mapMarkers")["data-mapmarkers"]
            .replace("&quot;", '"')
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&#160;", " ")
            .replace("&amp;", "&")
            .replace("\xa0", " ")
        )
        for store in store_list:
            page_url = locator_domain + store["UrlSlug"]
            sp1 = bs(session.get(page_url).text, "lxml")
            if "coming soon" in sp1.select_one(".shop-full-description").text.lower():
                continue
            logger.info(page_url)
            location_name = store["Name"]
            location_type = (
                "Factory & Store" if "Factory & Store" in location_name else "Store"
            )

            _ = bs(
                store["ShortDescription"]
                .replace("NOW OPEN:", "")
                .replace("Next to Trader Joe’s", ""),
                "lxml",
            )
            content = list(_.stripped_strings)
            phone = ""
            _phone = _.select_one(".store-phone")
            if _phone and "hour" not in _phone.text.lower():
                phone = _phone.text
            else:
                _phone = _.find("", string=re.compile(r"Phone"))
                if _phone:
                    phone = _phone.find_parent().text
                else:
                    for x, aa in enumerate(content):
                        if "Phone" in aa:
                            phone = content[x + 1]
                            break
            hours = []
            for x, hh in enumerate(content):
                if "Mon" in hh:
                    hours = content[x:]
            if hours and hours[0] == ":":
                del hours[0]
            else:
                if "Temporarily closed." in _.text.strip():
                    hours = ["Temporarily closed."]

            if hours and "Phone" in hours[-1]:
                del hours[-1]
            _addr = []
            for aa in content:
                if "Phone" in aa or "hour" in aa.lower():
                    break
                _addr.append(aa)
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                store_number=store["Id"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_p(phone),
                latitude=store["Latitude"],
                longitude=store["Longitude"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
