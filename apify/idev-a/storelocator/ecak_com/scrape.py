from sgcrawler.sgcrawler_fun import (
    SgCrawlerUsingHttpAndStaticCoordsFun,
    ManualRecordTransformer,
)
from sgcrawler.helper_definitions import Any
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from bs4 import BeautifulSoup as bs
import json

domain = "www.clarksoneyecare.com"  # replace with your domain


class MyManualTransformer(ManualRecordTransformer):
    """
    Manually transform your records to `SgRecord`, and uniquely-identify them.
    """

    def transform_record(self, raw: Any):
        """
        Given a `raw` record, normalise it and populate the fields of the SgRecord.
        """
        data = [_ for _ in raw]
        if data:
            location = data[0]["json"]
            hours = []
            for _ in location.get("openingHoursSpecification", []):
                time = f"{_['opens']}-{_['closes']}"
                if _["opens"] == "Closed":
                    time = "closed"
                hours.append(f"{_['dayOfWeek']}: {time}")
            return SgRecord(
                page_url=location["url"],
                location_type=location["@type"],
                locator_domain="https://www.clarksoneyecare.com/",
                location_name=data[0]["name"],
                street_address=location["address"]["streetAddress"],
                city=location["address"]["addressLocality"],
                state=location["address"]["addressRegion"],
                zip_postal=location["address"]["postalCode"],
                country_code=location["address"]["addressCountry"],
                phone=location["telephone"],
                latitude=location["geo"]["latitude"],
                longitude=location["geo"]["longitude"],
                hours_of_operation="; ".join(hours),
            )

    def uniq_id(self, record: SgRecord):
        """
        Returns the unique identifier of the record.
        Defaults to `store_number`, but if that's not the case, override to return the proper one.
        """
        return (
            record and record.page_url()
        )  # For illustrative purposes; normally, try to leave it at default


if __name__ == "__main__":
    domain = "www.clarksoneyecare.com"

    def fetch_raw_using(self, http, coord):
        latitude, longitude = coord[0], coord[1]
        locations = http.get(
            f"https://{self.crawler_domain()}/wp-json/352inc/v1/locations/coordinates?lat={latitude}&lng={longitude}"
        )
        if locations.status_code == 200:
            try:
                for raw in locations.json():
                    self.logger().debug("Something fishy here: ")
                    soup = bs(http.get(raw["permalink"]).text, "lxml")
                    yield {
                        "json": json.loads(
                            soup.findAll("script", type="application/ld+json")[1].string
                        ),
                        "name": soup.select_one("h1#prgmTitle").text,
                    }
            except Exception as err:
                self.logger().debug(str(err))

    SgCrawlerUsingHttpAndStaticCoordsFun(
        crawler_domain=domain,
        transformer=MyManualTransformer(),
        radius=10,
        country_code=SearchableCountries.USA,
        parallel_threads=4,
        make_http=SgRequests,
        fetch_raw_using=fetch_raw_using,
    ).run()
