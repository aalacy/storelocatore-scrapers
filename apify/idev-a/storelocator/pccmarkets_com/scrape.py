from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.pccmarkets.com/"
base_url = "https://www.pccmarkets.com/stores/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        locations = soup.select("div.pcc-section-bleed div.pcc-billboard")
        for _ in locations:
            page_url = _.select_one("div.pcc-billboard-details h4 a")["href"]
            soup1 = bs(session.get(page_url).text, "lxml")
            markers = (
                soup1.select_one("picture.picture.mb-sm source")["data-srcset"]
                .split("markers=")[1]
                .split(",")
            )
            location_name = _.select_one("div.pcc-billboard-details h4 a").text
            addr = [
                _addr
                for _addr in _.select_one(
                    "div.pcc-billboard-details address"
                ).stripped_strings
            ]
            phone = _.select_one("div.pcc-billboard-details p").text.strip()
            hours_of_operation = (
                _.select_one("div.pcc-billboard-details strong.label")
                .next_sibling.next_sibling.text.strip()
                .replace("\xa0", " ")
            )
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[1].strip(),
                country_code="US",
                phone=phone,
                latitude=markers[0],
                longitude=markers[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
