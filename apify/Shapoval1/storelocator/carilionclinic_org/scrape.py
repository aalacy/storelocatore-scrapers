import csv
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

    locator_domain = "https://carilionclinic.org"
    api_url = "https://carilionclinic.org/solr/select"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://carilionclinic.org",
        "Connection": "keep-alive",
        "Referer": "https://carilionclinic.org/locations",
        "Cache-Control": "max-age=0",
    }
    datas = [
        '{"query":"hospitals OR hospitals*","rows":"2000","fields":["*_type","*_title","*_body_summary","*_en_url","*_field_given_name","*_field_surname","*_field_affiliations","*_en_provider_photo_uri","*_field_primaryphone_location","*_field_primaryphone","*_field_acceptsnewclients","*_field_acceptschildren","*_field_specialties","*_field_services","*_address_line1","*_locality","*_administrative_area","*_postal_code","*_en_location_hero_image_uri","*_field_service_areas","*_field_medical_categories","*_field_specialty_conditions","*_en_url","*_field_owned","*_latlon"],"sort":{},"queryfields":["searchfields","ts_title"],"type":"edismax","filterquery":{"index_id":{"query":"ss_type:location"}},"geofilt":{},"bq":"tm_X3b_en_field_specialties:hospitals*^0.00000001"}',
        '{"query":"primary care OR primary care*","rows":"2000","fields":["*_type","*_title","*_body_summary","*_en_url","*_field_given_name","*_field_surname","*_field_affiliations","*_en_provider_photo_uri","*_field_primaryphone_location","*_field_primaryphone","*_field_acceptsnewclients","*_field_acceptschildren","*_field_specialties","*_field_services","*_address_line1","*_locality","*_administrative_area","*_postal_code","*_en_location_hero_image_uri","*_field_service_areas","*_field_medical_categories","*_field_specialty_conditions","*_en_url","*_field_owned","*_latlon"],"sort":{},"queryfields":["searchfields","ts_title"],"type":"edismax","filterquery":{"index_id":{"query":"ss_type:location"}},"geofilt":{},"bq":"tm_X3b_en_field_specialties:primary care*^0.00000001"}',
        '{"query":"specialty care OR specialty care*","rows":"2000","fields":["*_type","*_title","*_body_summary","*_en_url","*_field_given_name","*_field_surname","*_field_affiliations","*_en_provider_photo_uri","*_field_primaryphone_location","*_field_primaryphone","*_field_acceptsnewclients","*_field_acceptschildren","*_field_specialties","*_field_services","*_address_line1","*_locality","*_administrative_area","*_postal_code","*_en_location_hero_image_uri","*_field_service_areas","*_field_medical_categories","*_field_specialty_conditions","*_en_url","*_field_owned","*_latlon"],"sort":{},"queryfields":["searchfields","ts_title"],"type":"edismax","filterquery":{"index_id":{"query":"ss_type:location"}},"geofilt":{},"bq":"tm_X3b_en_field_specialties:specialty care*^0.00000001"}',
        '{"query":"emergency care OR emergency care*","rows":"2000","fields":["*_type","*_title","*_body_summary","*_en_url","*_field_given_name","*_field_surname","*_field_affiliations","*_en_provider_photo_uri","*_field_primaryphone_location","*_field_primaryphone","*_field_acceptsnewclients","*_field_acceptschildren","*_field_specialties","*_field_services","*_address_line1","*_locality","*_administrative_area","*_postal_code","*_en_location_hero_image_uri","*_field_service_areas","*_field_medical_categories","*_field_specialty_conditions","*_en_url","*_field_owned","*_latlon"],"sort":{},"queryfields":["searchfields","ts_title"],"type":"edismax","filterquery":{"index_id":{"query":"ss_type:location"}},"geofilt":{},"bq":"tm_X3b_en_field_specialties:emergency care*^0.00000001"}',
        '{"query":"urgent care OR urgent care*","rows":"2000","fields":["*_type","*_title","*_body_summary","*_en_url","*_field_given_name","*_field_surname","*_field_affiliations","*_en_provider_photo_uri","*_field_primaryphone_location","*_field_primaryphone","*_field_acceptsnewclients","*_field_acceptschildren","*_field_specialties","*_field_services","*_address_line1","*_locality","*_administrative_area","*_postal_code","*_en_location_hero_image_uri","*_field_service_areas","*_field_medical_categories","*_field_specialty_conditions","*_en_url","*_field_owned","*_latlon"],"sort":{},"queryfields":["searchfields","ts_title"],"type":"edismax","filterquery":{"index_id":{"query":"ss_type:location"}},"geofilt":{},"bq":"tm_X3b_en_field_specialties:urgent care*^0.00000001"}',
    ]
    for dataa in datas:

        data = dataa
        r = session.post(api_url, headers=headers, data=data)
        js = r.json()["results"]

        for j in js:
            slug = j.get("tm_X3b_en_url")[0]

            page_url = f"{locator_domain}{slug}"
            location_name = "".join(j.get("ts_title"))
            if location_name.find("-") != -1:
                location_name = location_name.split("-")[0].strip()
            location_type = j.get("ss_type")
            if dataa == datas[0]:
                location_type = "hospitals"
            if dataa == datas[1]:
                location_type = "primary care"
            if dataa == datas[2]:
                location_type = "specialty care"
            if dataa == datas[3]:
                location_type = "emergency care"
            if dataa == datas[4]:
                location_type = "urgent care"
            street_address = j.get("ts_address_line1")
            state = j.get("ss_administrative_area")
            postal = j.get("ss_postal_code")
            country_code = "USA"
            city = j.get("ss_locality")
            store_number = "<MISSING>"
            ll = j.get("ss_latlon") or "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if ll != "<MISSING>":
                latitude = str(ll).split(",")[0]
                longitude = str(ll).split(",")[1]
            phone = j.get("ss_field_primaryphone")
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(tree.xpath('//meta[@name="description"]/@content'))
                or "<MISSING>"
            )
            if hours_of_operation.find("open") != -1:
                hours_of_operation = " ".join(
                    hours_of_operation.split("open")[1:]
                ).strip()
            if hours_of_operation == "|":
                hours_of_operation = "<MISSING>"
            if (
                hours_of_operation.find("|") != -1
                and hours_of_operation.find("AM") != -1
                and hours_of_operation.find("PM") != -1
            ):
                hours_of_operation = hours_of_operation.split("|")[0].strip()
            if hours_of_operation.find("Inpatient Visiting Hours:") != -1:
                hours_of_operation = (
                    hours_of_operation.split("Inpatient Visiting Hours:")[1]
                    .split("|")[0]
                    .strip()
                )
            if hours_of_operation.find("|") != -1:
                hours_of_operation = "<MISSING>"

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
