from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.honestburgers.co.uk"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.honestburgers.co.uk/locations/")
        store_list = bs(res.text, "lxml").select("div.filterable-location")
        for store in store_list:
            page_url = store.select_one("a")["href"]
            location_name = store.select("a")[1].string.replace("–", "-")
            res = session.get(page_url)
            soup = bs(res.text, "lxml")
            try:
                detail = json.loads(
                    res.text.split('<script type="application/ld+json">')[1]
                    .split("</script>")[0]
                    .replace("\r\n", "")
                )
                zip = detail["address"]["postalCode"]
                city = detail["address"]["addressRegion"]
                street_address = detail["address"]["streetAddress"]
                country_code = detail["address"]["addressCountry"]
                phone = detail["telephone"]
                latitude = detail["geo"]["latitude"]
                longitude = detail["geo"]["longitude"]
                location_type = detail["@type"]
                if location_name == "St Albans":
                    phone = soup.select_one(
                        "div.hero-location > p a.cl-background"
                    ).string
            except:
                location_name = (
                    soup.select_one("div.hero-halftone-header")
                    .text.replace("\n", " ")
                    .strip()
                    .replace("–", "-")
                )
                try:
                    addr = soup.select_one("div.hero-location > p").contents
                    addr = [x for x in addr if x.string is not None]
                    zip_city = addr[1].split(" ")
                    zip_city = [x for x in zip_city if x != ""]
                    zip = " ".join(zip_city[-2:])
                    city = " ".join(zip_city[:-2])
                    street_address = addr[0].replace("\n", " ").strip()
                except:
                    zip = "<MISSING>"
                    city = "<MISSING>"
                    street_address = "<MISSING>"
                if location_name == "Waterloo - Honest Chicken":
                    addr = soup.select_one("div.hero-location > p").contents[0]
                    street_address = addr.split(", ")[0].replace("\n", " ").strip()
                    city = addr.split(", ")[1]
                    zip = addr.split(", ")[2]
                country_code = "<MISSING>"
                try:
                    phone = soup.select_one(
                        "div.hero-location > p a.cl-background"
                    ).string
                except:
                    phone = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                location_type = "<MISSING>"
            try:
                hours_of_operation = (
                    soup.select("dl")
                    .pop()
                    .text.replace("\n", " ")
                    .replace("–", "-")
                    .strip()
                )
            except:
                hours_of_operation = "Temporarily Closed"
            street_address = (
                "<MISSING>" if "Delivery" in street_address else street_address
            )
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                phone=phone,
                locator_domain=locator_domain,
                country_code=country_code,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
