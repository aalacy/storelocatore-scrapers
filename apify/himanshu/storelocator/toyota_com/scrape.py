# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com/service/tcom/dealerRefresh/zipCode/{}"
    domain = "toyota.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        if not data.get("showDealerLocatorDataArea"):
            continue
        if not data["showDealerLocatorDataArea"].get("dealerLocator"):
            continue
        all_locations = data["showDealerLocatorDataArea"]["dealerLocator"][0][
            "dealerLocatorDetail"
        ]
        for poi in all_locations:
            store_number = poi["dealerParty"]["partyID"]["value"]
            page_url = f"https://www.toyota.com/dealers/dealer/{store_number}/"
            hoo_clean = ""
            if poi.get("hoursOfOperation"):
                hoo = [
                    e for e in poi["hoursOfOperation"] if e["hoursTypeCode"] == "Sales"
                ]
                if hoo:
                    hoo_clean = []
                    for e in hoo[0]["daysOfWeek"]:
                        day = e["dayOfWeekCode"]
                        if e.get("availabilityStartTimeMeasure"):
                            opens = e["availabilityStartTimeMeasure"]["value"] // 60
                            closes = e["availabilityEndTimeMeasure"]["value"] // 60
                            hoo_clean.append(f"{day}: {str(opens)} - {str(closes)}")
                        else:
                            hoo_clean.append(f"{day}: closed")
                hoo_clean = " ".join(hoo_clean)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["dealerParty"]["specifiedOrganization"][
                    "companyName"
                ]["value"],
                street_address=poi["dealerParty"]["specifiedOrganization"][
                    "primaryContact"
                ][0]["postalAddress"]["lineOne"]["value"],
                city=poi["dealerParty"]["specifiedOrganization"]["primaryContact"][0][
                    "postalAddress"
                ]["cityName"]["value"],
                state=poi["dealerParty"]["specifiedOrganization"]["primaryContact"][0][
                    "postalAddress"
                ]["stateOrProvinceCountrySubDivisionID"]["value"],
                zip_postal=poi["dealerParty"]["specifiedOrganization"][
                    "primaryContact"
                ][0]["postalAddress"]["postcode"]["value"],
                country_code=poi["dealerParty"]["specifiedOrganization"][
                    "primaryContact"
                ][0]["postalAddress"]["countryID"],
                store_number=store_number,
                phone=poi["dealerParty"]["specifiedOrganization"]["primaryContact"][0][
                    "telephoneCommunication"
                ][0]["completeNumber"]["value"],
                location_type=poi["dealerParty"]["specifiedOrganization"][
                    "primaryContact"
                ][0]["departmentName"]["value"],
                latitude=poi["proximityMeasureGroup"]["geographicalCoordinate"][
                    "latitudeMeasure"
                ]["value"],
                longitude=poi["proximityMeasureGroup"]["geographicalCoordinate"][
                    "longitudeMeasure"
                ]["value"],
                hours_of_operation=hoo_clean,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
