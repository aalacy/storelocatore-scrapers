from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re

locator_domain = "https://www.charterfitness.com/"
json_url = "https://www.charterfitness.com/wp-admin/admin-ajax.php?action=store_search&lat=41.762354&lng=-87.914687&max_results=1000&search_radius=5000"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locations = session.get(json_url).json()
        for location in locations:
            location[
                "page_url"
            ] = f"http://www.charterfitness.com/location/charter-fitness-of-{'-'.join(location['city'].lower().split(' '))}"

        locations.append(
            {
                "page_url": "https://www.charterfitness.com/location/charter-fitness-of-mishawaka/"
            }
        )
        for location in locations:
            phone = ""
            hours_of_operation = ""
            soup1 = None
            try:
                r1 = session.get(location["page_url"])
                soup1 = bs(r1.text, "lxml")
                if not soup1.select_one(".entry-title") or not soup1.select_one(
                    ".entry-title"
                ).text.startswith("The page can"):
                    phone = (
                        soup1.find(string=re.compile("Phone Number:"))
                        .split(":")[1]
                        .strip()
                    )
                    hours_of_operation = "; ".join(
                        [
                            _.text
                            for _ in soup1.select("div.elementor-text-editor p")[1:]
                        ]
                    )
            except:
                pass

            page_url = location.get("page_url")
            location_name = location.get("store")
            street_address = f'{location.get("address")} {location.get("address2")}'
            city = location.get("city")
            state = location.get("state")
            zip_postal = location.get("zip")
            country_code = location.get("country", "USA")
            if not location.get("store"):
                if soup1:
                    block = " ".join(
                        [
                            _
                            for _ in soup1.select_one(
                                "div.elementor-text-editor.elementor-clearfix h5"
                            ).stripped_strings
                        ]
                    )
                    addr = parse_address_intl(block.split("located at ")[-1])
                    street_address = addr.street_address_1
                    city = addr.city
                    state = addr.state
                    zip_postal = addr.postcode
                    location_name = f"Charter Fitness {city}"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid1(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
