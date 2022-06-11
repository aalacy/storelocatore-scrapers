import csv
from lxml import html
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_data(zeep):
    rows = []
    locator_domain = "https://www.joann.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://hosted.where2getit.com/joann/mystore/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E53EDE5D6-8FC1-11E6-9240-35EF0C516365%3C/appkey%3E%3Cformdata%20id=%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C/dataview%3E%3Climit%3E250%3C/limit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%27{zeep}%27%3C/addressline%3E%3Clongitude%3E%3C/longitude%3E%3Clatitude%3E%3C/latitude%3E%3C/geoloc%3E%3C/geolocs%3E%3Csearchradius%3E30|50|100|250%3C/searchradius%3E%3Cwhere%3E%3Cnew_in_store_meet_up%3E%3Ceq%3E%3C/eq%3E%3C/new_in_store_meet_up%3E%3Cor%3E%3Ccustomframing%3E%3Ceq%3E%3C/eq%3E%3C/customframing%3E%3Cedu_demos%3E%3Ceq%3E%3C/eq%3E%3C/edu_demos%3E%3Cbusykids%3E%3Ceq%3E%3C/eq%3E%3C/busykids%3E%3Cbuyonline%3E%3Ceq%3E%3C/eq%3E%3C/buyonline%3E%3Cvikingsewinggallery%3E%3Ceq%3E%3C/eq%3E%3C/vikingsewinggallery%3E%3Cproject_linus%3E%3Ceq%3E%3C/eq%3E%3C/project_linus%3E%3Csewing_studio%3E%3Ceq%3E%3C/eq%3E%3C/sewing_studio%3E%3Cstore_features%3E%3Ceq%3E%3C/eq%3E%3C/store_features%3E%3Cpetfriendly%3E%3Ceq%3E%3C/eq%3E%3C/petfriendly%3E%3Cglowforge%3E%3Ceq%3E%3C/eq%3E%3C/glowforge%3E%3Ccustom_shop%3E%3Ceq%3E%3C/eq%3E%3C/custom_shop%3E%3C/or%3E%3C/where%3E%3C/formdata%3E%3C/request%3E",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    poi = tree.xpath("//poi")
    for p in poi:

        location_name = "".join(p.xpath(".//name/text()"))
        ad1 = "".join(p.xpath(".//address1/text()")).strip()
        ad2 = "".join(p.xpath(".//address2/text()")).strip()
        street_address = (ad1 + " " + ad2).strip()

        city = "".join(p.xpath(".//city/text()"))
        state = "".join(p.xpath(".//state/text()")).strip()
        postal = "".join(p.xpath(".//postalcode/text()")).strip()
        country_code = "".join(p.xpath(".//country/text()"))
        store_number = "".join(p.xpath(".//clientkey/text()"))
        phone = "".join(p.xpath(".//phone/text()")).strip() or "<MISSING>"
        slug = city
        if slug.find(" ") != -1:
            slug = slug.replace(" ", "-")
        page_url = (
            f"https://stores.joann.com/{state.lower()}/{slug.lower()}/{store_number}/"
        )

        latitude = "".join(p.xpath(".//latitude/text()")).strip()
        longitude = "".join(p.xpath(".//longitude/text()")).strip()
        location_type = "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d.capitalize()
            opens = "".join(p.xpath(f".//{d}open/text()")).strip()
            closes = "".join(p.xpath(f".//{d}close/text()")).strip()
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        cms = "".join(p.xpath(".//grandopening/text()")).strip()
        if cms.find("1") != -1:
            hours_of_operation = "Coming Soon"

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    zips = static_zipcode_list(radius=37, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, zeep): zeep for zeep in zips}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
