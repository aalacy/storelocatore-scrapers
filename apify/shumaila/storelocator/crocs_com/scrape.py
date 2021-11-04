from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    mylist = static_coordinate_list(10, SearchableCountries.USA)

    for lat, lng in mylist:

        url = (
            "https://crocs.locally.com/stores/conversion_data?has_data=true&company_id=1762&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat="
            + str(lat)
            + "&map_center_lng="
            + str(lng)
            + "&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=new"
        )
        loclist = session.get(url, headers=headers).json()["markers"]
        for loc in loclist:

            store = loc["id"]
            title = loc["name"]
            lat = loc["lat"]
            longt = loc["lng"]
            street = loc["address"]
            state = loc["state"]
            city = loc["city"]
            pcode = loc["zip"]
            phone = loc["phone"]
            ccode = loc["country"]
            check = loc["disclaimer"]
            ltype = "Store"

            link = "<MISSING>"
            hours = ""
            if "Dealer" in check:
                ltype = "Dealer"
                hours = "<MISSING>"
            else:
                link = "https://locations.crocs.com/shop/" + loc["slug"]
                hourslist = loc["display_dow"]
                for hr in hourslist:
                    noww = hourslist[hr]
                    hours = hours + noww["label"] + " " + noww["bil_hrs"] + " "
            if len(hours) < 3:
                hours = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.crocs.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
