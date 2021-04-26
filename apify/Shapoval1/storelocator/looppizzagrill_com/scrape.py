import csv
import usaddress
from lxml import html
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
    locator_domain = "https://www.thelooprestaurant.com"
    api_url = "https://www.powr.io/wix/map/public.json?pageId=rrcup&compId=comp-kiespl6j3&viewerCompId=comp-kiespl6j3&siteRevision=753&viewMode=site&deviceType=desktop&locale=en&tz=America%2FNew_York&width=455&height=544&instance=Lfl7ze0je2ZLRYoU5k7QLSjcH9Fe2VpDPMQCszgrUmg.eyJpbnN0YW5jZUlkIjoiMDA3ZGU4OWUtNjdjNC00ZWM5LWEwMDktYzdkMjI5YzA1YjEyIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDMtMDdUMTE6Mjg6MDEuMzkwWiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI0NjM5N2Q5ZC1lMTYzLTRjNzMtYWIzOS05MTA3YTc2MjAxZjQiLCJzaXRlT3duZXJJZCI6ImZkMjE4YmNjLTU5NjUtNGVkNC1hY2E5LTdkYjRiNWUzOTQxMSJ9&currency=USD&currentCurrency=USD&vsi=67acc5b7-0def-4cc0-b3e8-6a1704fbf80b&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22cb096e66-5b78-40af-9913-b2c7f9d2b707%7C3%22%2C%22BSI%22%3A%22cb096e66-5b78-40af-9913-b2c7f9d2b707%7C3%22%7D&url=https://www.thelooprestaurant.com/durham-nc"

    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    r = session.get(api_url)
    js = r.json()

    for j in js["content"]["locations"]:
        ad = "".join(j.get("address"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("postal")
        state = a.get("state")

        country_code = a.get("CountryName")
        store_number = "<MISSING>"
        location_name = f"{j.get('name').replace('<p>','').replace('</p>','')} - {j.get('description').replace('<p>','').replace('</p>','')}"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        page_url = "<MISSING>"

        if street_address.find("116") != -1:
            page_url = "https://www.thelooprestaurant.com/durham-nc"
        if street_address.find("125") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/durham-duke-nc-thelooprestaurant"
            )
        if street_address.find("320") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-13-of-avondale-jacksonville-fl"
            )
        if street_address.find("1800") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-12-of-avondale-jacksonville-fl"
            )
        if street_address.find("1030") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-14-of-avondale-jacksonville-fl"
            )
        if street_address.find("14035") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-6-of-avondale-jacksonville-flo"
            )
        if street_address.find("4591") != -1:
            page_url = "https://www.thelooprestaurant.com/copy-of-locations"
        if street_address.find("869") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-of-avondale-jacksonville-flori"
            )
        if street_address.find("8221") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-2-of-avondale-jacksonville-flo"
            )
        if street_address.find("4413") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-3-of-avondale-jacksonville-flo"
            )
        if street_address.find("2014") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-4-of-avondale-jacksonville-flo"
            )
        if street_address.find("550") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-5-of-avondale-jacksonville-flo"
            )
        if street_address.find("9965") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-7-of-avondale-jacksonville-flo"
            )
        if street_address.find("211") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-8-of-avondale-jacksonville-flo"
            )
        if street_address.find("1960") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-9-of-avondale-jacksonville-flo"
            )
        if street_address.find("450") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-10-of-avondale-jacksonville-fl"
            )
        if street_address.find("101") != -1:
            page_url = (
                "https://www.thelooprestaurant.com/copy-11-of-avondale-jacksonville-fl"
            )
        session = SgRequests()
        subr = session.get(page_url)
        tree = html.fromstring(subr.text)

        phone = "".join(tree.xpath("//a[contains(@href, 'tel')]//text()"))

        hours_of_operation = " ".join(
            tree.xpath(
                "//span[contains(text(), 'pm')]//text() | //span[contains(text(), 'PM')]//text() | //span[contains(text(), 'Hours')]/text() | //p[contains(text(), 'Hours')]/text()"
            )
        ).replace("\n", "")
        if hours_of_operation.find("Hours of Operation:") != -1:
            hours_of_operation = hours_of_operation.split("Hours of Operation:")[
                1
            ].strip()
        if hours_of_operation.find("Hours of Operation") != -1:
            hours_of_operation = hours_of_operation.split("Hours of Operation")[
                1
            ].strip()
        if hours_of_operation.find("Last") != -1:
            hours_of_operation = hours_of_operation.split("Last")[0].strip()
        if street_address.find("211") != -1:
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[contains(text(), "Hours")]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
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
