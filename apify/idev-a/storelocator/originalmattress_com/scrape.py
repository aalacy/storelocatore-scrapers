from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


def fetch_data():
    locator_domain = "https://www.originalmattress.com/"
    base_url = "https://www.originalmattress.com/find-a-store"
    with SgRequests() as session:
        store_list = json.loads(
            session.get(base_url)
            .text.split('type="hidden" data-mapmarkers="')[1]
            .split('" />')[0]
            .replace("&quot;", '"')
        )
        for store in store_list:
            page_url = locator_domain + store["UrlSlug"]
            store_number = store["Id"]
            location_name = store["Name"].replace("&amp;", "&")
            location_type = (
                "Factory & Store" if "Factory & Store" in location_name else "Store"
            )

            _ = bs(
                store["ShortDescription"]
                .replace("&gt;", ">")
                .replace("&lt;", "<")
                .replace("NOW OPEN:", "")
                .replace("Next to Trader Joe’s", ""),
                "lxml",
            )
            _phone = _.select_one("div.store-phone a")
            if _phone:
                phone = _phone.text.strip()
            content = list(_.stripped_strings)
            hours = []
            for x, hh in enumerate(content):
                if "Mon" in hh:
                    hours = content[x:]
            if hours and hours[0] == ":":
                del hours[0]
            else:
                if "Temporarily closed." in _.text.strip():
                    hours = ["Temporarily closed."]

            _addr = []
            for aa in content:
                if "Phone" in aa or "Hours" in aa:
                    break
                _addr.append(aa)
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
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
