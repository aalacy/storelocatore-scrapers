from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("amplehills")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.amplehills.com/"
    page_url = "https://www.amplehills.com/in-stores"
    base_url = "https://1v8tcmfe.apicdn.sanity.io/v1/data/query/production?query=*%5B_type%20%3D%3D%20%27location%27%5D%20%7B%0A%20%20_id%2C%0A%20%20_createdAt%2C%0A%20%20name%2C%0A%20%20slug%2C%0A%20%20hours%2C%0A%20%20region%2C%0A%20%20address1%2C%0A%20%20address2%2C%0A%20%20city%2C%0A%20%20state%2C%0A%20%20zip%2C%0A%20%20phone%2C%0A%20%20longitude%2C%0A%20%20latitude%2C%0A%20%20seasonal%2C%0A%20%20delivery%2C%0A%20%20offersParties%2C%0A%20%20offersCakes%2C%0A%20%20order%2C%0A%20%20image%7B%0A%20%20%20%20%27src%27%3A%20asset-%3Eurl%0A%20%20%7D%2C%0A%20%20description%2C%0A%20%20blocks%5B%5D%7B%0A%20%20...%2C%0A%20%20%27image%27%3A%20image%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%27images%27%3A%20images%5B%5D%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%27image1%27%3A%20image1%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%27image2%27%3A%20image2%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%27products%27%3A%20products%5B%5D-%3E%7B%0A%20%20_id%2C%0A%20%20_createdAt%2C%0A%20%20title%2C%0A%20%20productHandle%2C%0A%20%20price%2C%0A%20%20flavorDescription%2C%0A%20%20heroImage%7B%0A%20%20%20%20%27src%27%3A%20asset-%3Eurl%0A%20%20%7D%2C%0A%20%20gridImage%7B%0A%20%20%20%20%27src%27%3A%20asset-%3Eurl%0A%20%20%7D%2C%0A%20%20pintImage%7B%0A%20%20%20%20%27src%27%3A%20asset-%3Eurl%0A%20%20%7D%2C%0A%20%20description%2C%0A%20%20availableInBYO%2C%0A%20%20exclusiveToBYO%2C%0A%20%20order%2C%0A%7D%2C%0A%20%20%27pressItems%27%3A%20pressItems%5B%5D%7B%0A%20%20%20%20...%2C%0A%20%20%20%20%27logo%27%3A%20logo%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%0A%20%20%7D%2C%0A%20%20%27items%27%3A%20items%5B%5D-%3E%7B%0A%20%20%20%20_type%20%3D%3D%20%27flavor%27%20%3D%3E%20%7B%0A%20%20_id%2C%0A%20%20_createdAt%2C%0A%20%20name%2C%0A%20%20slug%2C%0A%20%20filters%2C%0A%20%20labelColor%2C%0A%20%20image%7B%0A%20%20%20%20%27src%27%3A%20asset-%3Eurl%0A%20%20%7D%0A%7D%0A%20%20%7D%2C%0A%20%20%27tabs%27%3A%20tabs%5B%5D%7B%0A%20%20%20%20_type%20%3D%3D%20%27tab%27%20%3D%3E%20%7B%0A%20%20%20%20%20%20...%2C%0A%20%20%20%20%20%20%27image%27%3A%20image%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%20%20%20%20%27image1%27%3A%20image1%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%20%20%20%20%27image2%27%3A%20image2%7B%0A%20%20%27src%27%3A%20asset-%3Eurl%2C%0A%20%20alt%2C%0A%20%20credit%2C%0A%20%20caption%2C%0A%20%20crop%2C%0A%20%20hotspot%2C%0A%20%20%27id%27%3A%20asset-%3E_id%2C%0A%20%20%27metadata%27%3A%20asset-%3Emetadata%0A%7D%2C%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D%2C%0A%20%20seoTitle%2C%0A%20%20seoDescription%2C%0A%20%20seoImage%0A%7D"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        logger.info(f"{len(locations['result'])} found")
        for _ in locations["result"]:
            page_url = f"https://www.amplehills.com/location/{_['slug']}"
            hours = []
            for day in days:
                day = day.lower()
                hours.append(f"{day}: {_.get('hours', {}).get(day)}")
            street_address = _["address1"].strip()
            if _.get("address2"):
                street_address += " " + _["address1"].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"].strip(),
                state=_["state"].strip(),
                zip_postal=_["zip"].strip(),
                country_code="US",
                phone=_["phone"].strip(),
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
