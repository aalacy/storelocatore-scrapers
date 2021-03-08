from sgcrawler.helper_definitions import Any
from sgcrawler.sgcrawler_fun import (
    SgCrawlerUsingHttpAndDynamicSearchFun,
    ManualRecordTransformer,
)
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
import us

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


class MyManualTransformer(ManualRecordTransformer):
    """
    Manually transform your records to `SgRecord`, and uniquely-identify them.
    """

    def transform_record(self, raw: Any):
        """
        Given a `raw` record, normalise it and populate the fields of the SgRecord.
        """
        location = raw
        hours = []
        for _ in location["formatted_hours"]["primary"]["days"]:
            hours.append(f"{_['label']}: {_['content']}")
        return SgRecord(
            page_url=location["location_url"],
            locator_domain="https://locations.cinnaholic.com/",
            location_name=location["location_name"],
            street_address=location["street"],
            city=location["city"],
            state=location["state"],
            zip_postal=location["postal_code"],
            country_code="US",
            phone=location["phonemap"].get("phone"),
            latitude=location["lat"],
            longitude=location["lon"],
            hours_of_operation="; ".join(hours),
        )

    def uniq_id(self, record: SgRecord):
        """
        Returns the unique identifier of the record.
        Defaults to `store_number`, but if that's not the case, override to return the proper one.
        """
        return (
            record and record.page_url()
        )  # For illustrative purposes; normally, try to leave it at default and see if it
        # filters correctly.


if __name__ == "__main__":
    domain = "locations.cinnaholic.com"  # replace with your domain

    def fetch_raw_using(self, http, next_item, found_location_at):
        locations = http.get(
            f"https://locations.cinnaholic.com/modules/multilocation/?near_location={next_item.name}&services__in=&published=1&within_business=true"
        ).json()
        for raw in locations["objects"]:
            yield raw

    def search_states(self):
        for _ in us.states.STATES:
            yield _

    SgCrawlerUsingHttpAndDynamicSearchFun(
        crawler_domain=domain,
        transformer=MyManualTransformer(),  # OR: my_manual_transformer(...) OR: my_declarative_transformer(...)
        make_dynamic_search=search_states,
        make_http=SgRequests,
        fetch_raw_using=fetch_raw_using,
    ).run()
