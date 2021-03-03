from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.woodmans-food.com/"
base_url = "https://www.woodmans-food.com/"


def fetch_data():
    data = []

    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        _tag = soup.find("span", string="Locations")
        links = _tag.next_sibling.next_sibling.findChildren("a")
        for link in links:
            page_url = link["href"]
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            block = [
                _.strip()
                for _ in soup1.select_one("div.store-content h4")
                .text.strip()
                .split("|")
            ]
            _split = block[1].split(",")
            hours_of_operation = "; ".join(
                soup1.select_one("div.store-content p")
                .text.strip()
                .split("|")[0]
                .split(": ")[1]
                .replace("++", "")
                .split(",")
            )
            record = SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=block[0].strip(),
                city=_split[0].strip(),
                state=_split[1].strip().split(" ")[0].strip(),
                zip_postal=_split[1].strip().split(" ")[1].strip(),
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            data.append(record)

    return data


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
