from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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
        links = []
        for link in locations:
            page_url = f"http://www.charterfitness.com/location/charter-fitness-of-{'-'.join(link['city'].lower().split(' '))}"
            links.append(page_url)

        links.append(
            "https://www.charterfitness.com/location/charter-fitness-of-mishawaka/"
        )
        for page_url in links:
            phone = ""
            hours_of_operation = ""
            try:
                r1 = session.get(page_url)
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
            yield SgRecord(
                page_url=page_url,
                location_name=link["store"],
                street_address=f'{link["address"]} {link["address2"]}',
                city=link["city"],
                state=link["state"],
                zip_postal=link["zip"],
                country_code=link["country"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid1(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
