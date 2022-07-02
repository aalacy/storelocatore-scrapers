import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt, wait_fixed

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.specsavers.co.uk"
base_url = "https://www.specsavers.co.uk/stores/full-store-list"

headers = {
    "Host": "www.specsavers.co.uk",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "PostmanRuntime/7.19.0",
    "Connection": "keep-alive",
}


@retry(wait=wait_fixed(10), stop=stop_after_attempt(5))
def get_url(url, session):
    soup = None
    try:
        response = session.get(url)
        soup = bs(response.text, "lxml")
    except:
        raise Exception

    return soup


def _d(page_url, res, soup, location_type, session):
    try:
        with open("index.html", "w") as file:
            file.write(str(soup))
        content = soup.find("script", type="application/ld+json").string
        data = json.loads(content)

        location_name = data["name"]
        phone = data["telephone"]

        address = data["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        postal = address["postalCode"]
        country_code = address["addressCountry"]

        geo = data["geo"]
        latitude = geo["latitude"]
        longitude = geo["longitude"]

        hours_of_operation = []
        for dayhour in data["openingHoursSpecification"]:
            opens = dayhour["opens"]
            closes = dayhour["closes"]
            for day in dayhour["dayOfWeek"]:
                hours_of_operation.append(f"{day}: {opens}-{closes}")

        hours_of_operation = ", ".join(hours_of_operation)

        return SgRecord(
            locator_domain="specsavers.co.uk",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )
    except:
        try:
            if soup.select_one("div.store p"):
                addr = list(soup.select_one("div.store p").stripped_strings)
            else:
                response = session.get(page_url)
                soup = bs(response.text, "lxml")
                addr = list(soup.select_one("div.store p").stripped_strings)

            raw_address = " ".join(addr).replace("\n", "").replace("\r", "")
            addr = raw_address.split(",")
            street_address = " ".join(addr[:-3]).strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            try:
                coord = json.loads(res.text.split("var position =")[1].split(";")[0])
            except:
                coord = {"lat": "", "lng": ""}
            hours = [
                tr["content"] for tr in soup.select("table.opening--day-and-time tr")
            ]
            try:
                location_name = soup.select_one("h1.store-header--title").text.strip()
            except:
                location_name = soup.select_one(
                    "h1.general-information__store-name"
                ).text.strip()
            return SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr[-3].replace(",", ""),
                state=addr[-2].replace(",", ""),
                zip_postal=addr[-1].replace(",", ""),
                phone=soup.select_one(
                    "span.contact--store-telephone--text"
                ).text.strip(),
                locator_domain=locator_domain,
                latitude=coord.get("lat"),
                longitude=coord.get("lng"),
                hours_of_operation="; ".join(hours),
                location_type=location_type,
                country_code="UK",
                raw_address=raw_address,
            )
        except Exception as e:
            logger.info(f"failed {page_url} {str(e)}")
            open("w", "a+").write(page_url + ": " + str(e) + "\n")


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        soup = bs(session.get(base_url, headers=headers).text, "lxml")
        store_links = soup.select("div.item-list ul li a")
        for link in store_links:
            page_url = "https://www.specsavers.co.uk/stores/" + link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=headers)
            if res.status_code == 200:
                soup = bs(res.text, "lxml")
                location_type = (
                    "Hearing Centre" if "hearing" in page_url else "Optician"
                )
                yield _d(page_url, res, soup, location_type, session)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
