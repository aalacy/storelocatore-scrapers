import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.caferouge.com"
    api_url = "https://api.bigtablegroup.com/pagedata?brandKey=caferouge&path=/spaces/hlvdy7x28mmo/entries?access_token=bad26202af27c0f9ca3921ab7fb67bc6eea2b34ba73fe53168bf041548707f8c%26select=fields.title,fields.slug,fields.city,fields.heroTile,fields.description,fields.addressLocation,fields.deliverooLink,fields.email,fields.phoneNumber,fields.amenities,fields.miscellaneous,fields.metaTags,fields.metaTagsForBookNowTab,fields.imageGallery,fields.promotionStack,fields.offersTitle,fields.offersDescription,fields.showOffers,fields.eventSection,fields.takeawayCollectionService,fields.takeawayDeliveryServices,fields.storeId,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.hours,fields.alternativeHours,fields.takeATourUrl,fields.bookingProviderUrl,fields.priceBandId,fields.collectionMessage%26content_type=restaurant%26include=10%26limit=1000"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["items"]:
        ad = j.get("fields")
        location_name = ad.get("title")
        street_address = f"{ad.get('addressLine1')} {ad.get('addressLine2')}".strip()
        city = ad.get("city")
        slug = "".join(ad.get("slug"))
        page_url = f"https://www.caferouge.com/bistro-brasserie/{city}/{slug}"
        state = ad.get("county")
        country_code = "UK"
        store_number = "<MISSING>"
        latitude = ad.get("addressLocation").get("lat")
        longitude = ad.get("addressLocation").get("lon")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        phone = ad.get("phoneNumber")
        postal = ad.get("postCode")
        if location_name == "Center Parcs Sherwood Forest":
            for j in js["includes"]["Entry"]:
                aaa = j.get("fields").get("name")
                tmp = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                _tmp = []
                if aaa == "Center Parcs Sherwood":
                    for i in tmp:
                        days = i
                        Open = j.get("fields").get(f"{i}Open")
                        Close = j.get("fields").get(f"{i}Close")
                        line = f"{days} {Open} - {Close}"
                        _tmp.append(line)
                    hours_of_operation = " ; ".join(_tmp)
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
