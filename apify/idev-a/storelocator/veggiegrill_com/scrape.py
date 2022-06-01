from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("veggiegrill")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
}

locator_domain = "https://veggiegrill.com/"
base_url = "https://veggiegrill.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=headers).text, "lxml").select(
            "div.locations-details-sm"
        )
        for location in locations:
            page_url = location.select("a")[-1]["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=headers).text, "lxml")
            if "permanently closed" in sp1.h2.text.lower():
                continue
            days = sp1.select("dl.hours dt")
            times = sp1.select("dl.hours dd")
            hours = []
            for x in range(len(days)):
                hours.append(f"{days[x].text.strip()}: {times[x].text.strip()}")
            addr = list(sp1.select_one("address").stripped_strings)
            phone = sp1.find("a", href=re.compile("tel:")).text.strip()
            street_address = (
                " ".join(addr[:-1])
                .replace("Ackerman Student Union", "")
                .replace("New York, NY 10007", "")
                .strip()
            )
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = addr[-1].split(",")[0].strip()
            if city == "New Yor":
                city = "New York"
            link = sp1.find("a", string=re.compile(r"^Get directions"))
            coord = ["", ""]
            if link:
                try:
                    coord = link["href"].split("/@")[1].split("/")[0].split(",")
                except:
                    pass
            yield SgRecord(
                page_url=page_url,
                store_number=location["data-id"],
                location_name=sp1.h2.text.strip(),
                street_address=street_address,
                city=city,
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr).replace("Ackerman Student Union", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
