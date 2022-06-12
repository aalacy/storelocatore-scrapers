from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "current_date=2021-1-18 13:53:0; _ga=GA1.2.496098882.1610959724; _gid=GA1.2.1745264377.1610959724; _fbp=fb.1.1610959729860.990200720; btpdb.1PR3l09.dGZjLjc0ODMzMDQ=U0VTU0lPTg; btpdb.1PR3l09.dGZjLjc0ODMxOTQ=U0VTU0lPTg; calltrk_referrer=direct; calltrk_landing=https%3A//formanmills.com/; calltrk_session_id=d3a45bc4-5218-48e3-b1ab-d8c1f57c5edc; __gads=ID=c90326b73e6bfce1-225c8791adc500c3:T=1610959802:RT=1610959802:S=ALNI_MbBXVkok7VDPpYeT1YkVWgv4bmcAQ; _gat_gtag_UA_11589974_2=1; __atuvc=3%7C3; __atuvs=6005d90beed699d7000",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}
locator_domain = "https://formanmills.com"
base_url = "https://formanmills.com/stores/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=headers)
        store_list = eval(
            res.text.split("var loc =")[1]
            .split("var locations")[0]
            .replace("\n", "")
            .strip()[:-1]
        )
        for store in store_list:
            detail = bs(store[0], "lxml")
            page_url = detail.select_one("h3 a")["href"]
            logger.info(page_url)
            location_name = detail.select_one("h3 a").text.strip()
            location_name = (
                location_name.split(":")[0]
                if ":" in location_name
                else location_name.split("*")[0]
            )
            addr = list(detail.select_one("ul").stripped_strings)
            soup = bs(session.get(page_url, headers=headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings) for hh in soup.select("div.hours ul li")
            ]
            location_type = ""
            lt = soup.select_one("p.notes")
            if lt:
                if "Temporarily Closed" in lt.text:
                    location_type = "Temporarily Closed"
                elif "Permanently Closed" in lt.text:
                    location_type = "Permanently Closed"
            yield SgRecord(
                page_url=page_url,
                store_number=store[3],
                location_name=location_name,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=detail.select_one("div.telephone").text.strip(),
                latitude=store[1],
                longitude=store[2],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\t", "")
                .replace("\n", " ")
                .replace("\r", ""),
                location_type=location_type,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
