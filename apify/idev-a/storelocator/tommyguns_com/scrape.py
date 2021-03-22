from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("tommyguns.com")


def fetch_data():
    locator_domain = "https://www.tommyguns.com"
    base_url = "https://www.tommyguns.com/ca/location/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container article")
        logger.info(f"{len(locations)} found!")
        for _ in locations:
            location_name = _.select_one("div h1").text.replace("*NOW OPEN*", "")
            page_url = _.select_one("div.store-location-link a")["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = list(soup1.select_one("div.location-hours p").stripped_strings)
            if hours[0].startswith("WE HAVE MERGED WITH"):
                continue
            del hours[0]
            phone = _.select_one("p.store-location-phone a").text
            street_address = soup1.select_one(
                "div.location-details .street-address"
            ).text
            city_state = soup1.select_one("div.location-details .mailing").text
            city = city_state.split(",")[0]
            state = city_state.split(",")[1].strip().split(" ")[0]
            zip_postal = city_state.split(",")[1].strip().split(" ")[1]

            logger.info(page_url)
            coord = ["", ""]
            try:
                coord = (
                    soup1.select_one("div.location-map-col a")["href"]
                    .split("!3d")[1]
                    .split("!4d")
                )
            except:
                try:
                    coord = (
                        soup1.select_one("div.location-map-col a")["href"]
                        .split("/@")[1]
                        .split("z/")[0]
                        .split(",")
                    )
                except:
                    pass

            yield SgRecord(
                page_url=page_url,
                store_number=_["id"].split("-")[-1],
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
