from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("hamricks")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hamricks.com"
base_url = "https://www.hamricks.com/store-locator"


def fetch_data():
    with SgRequests() as session:
        links = (
            session.get(base_url, headers=_headers)
            .text.split("var infowindow =")[0]
            .split("contentString[")
        )
        logger.info(f"{len(links)} found")
        for link in links:
            _ = bs(link.split("]")[1].split(";")[0], "lxml")
            if "=" not in _.text:
                continue
            page_url = _.a["href"]
            logger.info(page_url)
            addr = list(_.select_one("div#bodyContent p").stripped_strings)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            if sp1.select_one("div.StoreInfo.FGothamBold"):
                phone = sp1.select_one("div.StoreInfo.FGothamBold").text.strip()
            temp = list(sp1.select("div.StoreInfo")[-1].stripped_strings)
            hours = []
            for hh in temp:
                if "please shop" in hh:
                    break
                hours.append(hh)
            coord = (
                sp1.select_one("div.CommercialBtn a")["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.h5.text.strip().replace("\\'", "'"),
                street_address=addr[-2].replace("•", " "),
                city=addr[-1].split(",")[0].strip(),
                state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=": ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
