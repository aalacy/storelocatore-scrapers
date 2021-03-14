"""
This is the set of succinct templates for a scraper. For Object Oriented templates, see: `../../object_oriented/`

Choose the functionality you need, populate/change what you need, but remember we consider these to be best practices.
"""
from typing import Any
from sgcrawler.sgcrawler_fun import SgCrawlerUsingHttpAndStaticCoordsFun
from sgcrawler.helper_definitions import ManualRecordTransformer
from sgcrawler.helper_definitions import ManualRecordTransformerFun
from sgcrawler.helper_definitions import DeclarativeTransformerAndFilter
from sgcrawler.helper_definitions import DeclarativePipeline
from sgscrape.sgrecord import SgRecord
from sgscrape.simple_scraper_pipeline import SSPFieldDefinitions
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgzip.dynamic import SearchableCountries
from sgrequests import SgRequests

########################################################################################################################
#
#               [ SECTION 1 ]
#
# Raw record transformation and record identity.
# Choose your transformer & filter type/style. They are all functionally equivalent, but (3) is strongly encouraged.
# Erase the others, when you have.
#
# 1. Extend `ManualRecordTransformer` - - - - - - - - - - - (line 25)
# 2. Use the more succinct `ManualRecordTransformerFun` - - (line 48)
# 3. [ RECOMMENDED ] Use a declarative transformer/filter - (line 59)
#                    (`pip install sgscrape`, and see `sgscrape.simple_scraper_pipeline.py` for details)


class MyManualTransformer(ManualRecordTransformer):
    """
    Manually transform your records to `SgRecord`, and uniquely-identify them.
    """

    def transform_record(self, raw: Any):
        """
        Given a `raw` record, normalise it and populate the fields of the SgRecord.
        """
        return SgRecord(
            locator_domain="example.com"
        )  # Empty, for illustration purposes.

    def uniq_id(self, record: SgRecord):
        """
        Returns the unique identifier of the record.
        Defaults to `store_number`, but if that's not the case, override to return the proper one.
        """
        return (
            record.page_url()
        )  # For illustrative purposes; normally, try to leave it at default and see if it
        # filters correctly.


def my_manual_transformer(crawler_domain: str):
    """
    Instead of extending `ManualRecordTransformer`, you can use the more succinct form.
    If the transformations are long, use helper methods instead of lambdas.
    """
    return ManualRecordTransformerFun(
        uniq_id=lambda record: record.store_number(),
        transform_record=lambda raw: SgRecord(
            locator_domain=crawler_domain
        ),  # Empty, for illustration purposes.
    )


def my_declarative_transformer(crawler_domain: str):
    """
    Using a declarative approach to indicate where fields can be found.
    """
    return DeclarativeTransformerAndFilter(
        pipeline=DeclarativePipeline(
            crawler_domain=crawler_domain,
            field_definitions=SSPFieldDefinitions(
                locator_domain=ConstantField(crawler_domain),
                page_url=MappingField(mapping=["url_slug"]),
                location_name=MappingField(mapping=["name"], is_required=False),
                street_address=MultiMappingField(
                    mapping=[["location", "address"], ["location", "address2"]]
                ),
                city=MappingField(mapping=["location", "city"]),
                state=MappingField(mapping=["location", "state"]),
                zipcode=MappingField(mapping=["location", "zip"], is_required=False),
                country_code=MappingField(
                    mapping=["location", "country_code"], is_required=False
                ),
                store_number=MappingField(
                    mapping=["external_id"], part_of_record_identity=True
                ),
                phone=MappingField(mapping=["phone"], is_required=False),
                location_type=MappingField(mapping=["legal"], is_required=False),
                latitude=MappingField(
                    mapping=["location", "latitude"], is_required=False
                ),
                longitude=MappingField(
                    mapping=["location", "longitude"], is_required=False
                ),
                hours_of_operation=MissingField(),
            ),
            fail_on_outlier=False,
        )
    )


########################################################################################################################
#
#               [ SECTION 2]
#
# Basic capabilities include:
# 1. Efficiently de-duplicating records based on their unique ids.
# 2. Logging statistics and important events.
# 3. Writing records to file.
# 4. Using multi-threading whenever it makes sense.
# 5. Manage all resources efficiently.
# 6. Avoid common bugs and speed up implementation!
#

if __name__ == "__main__":
    domain = "example.com"  # replace with your domain

    def fetch_raw_using(self, http, coord):
        # The `http` argument is `SgRequests` because that's what `make_http()` returns.
        # The `coord` argument gives you the next (lat, long) coordinate from the static list.
        # Use `self` to access `crawler_domain()` and `logger()`

        # Example:
        latitude, longitude = coord[0], coord[1]
        locations = http.get(
            f"http://{self.crawler_domain()}/locations?lat={latitude}&long={longitude}"
        ).json()
        for raw in locations:
            self.logger().debug(
                f"Something fishy here: {raw}"
            )  # you can access the logger like so.
            yield raw  # always yield each raw location you find.

    SgCrawlerUsingHttpAndStaticCoordsFun(
        crawler_domain=domain,
        transformer=MyManualTransformer(),  # OR: my_manual_transformer(...) OR: my_declarative_transformer(...)
        radius=10,  # see input to `sgzip.static.static_coordinate_list`
        country_code=SearchableCountries.USA,  # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        parallel_threads=4,  # Defaults to `1`. If 2 or more, will use `sgscrape.simple_utils.parallelize(...)`
        make_http=SgRequests(),
        fetch_raw_using=fetch_raw_using,
    ).run()
