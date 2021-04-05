import csv
import json
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "kw.com"
    start_url = "https://api-endpoint.cons-prod-us-central1.kw.com/graphql"

    headers = {"x-shared-secret": "MjFydHQ0dndjM3ZAI0ZHQCQkI0BHIyM="}
    query = """{
        ListOfficeQuery {
            id
            name
            address
            subAddress
            phone
            fax
            lat
            lng
            url
            contacts {
            name
            email
            phone
            __typename
            }
            __typename
        }
        }
    """
    payload = {"operationName": None, "variables": {}, "query": query}
    response = session.post(start_url, headers=headers, json=payload)
    all_poi = response.json()
    all_poi = all_poi["data"]["ListOfficeQuery"]

    for poi in all_poi:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        if store_url != "<MISSING>":
            session.get(store_url)
            site_id = session.get_session().cookies.get_dict()["site_id"]
            det_query = """query siteOptionsQuery($siteId: String, $kwuid: Int) {  SiteOptionsQuery(siteId: $siteId, kwuid: $kwuid) {    id    type    kw_uid    org_id    domain    compliance {      links {        display_key        url        __typename      }      __typename    }    config {      theme {        theme_color        header_text        header_sub_text        search_header_text        hero_images        __typename      }      analytics {        facebook_pixel_id        google_analytics_account_id        google_analytics_tracking_id        __typename      }      seo {        seo_keywords        seo_description        __typename      }      __typename    }    pages {      name      label      slug      url      description      config_id      template_id      __typename    }    profile {      id      type      type_id      profile {        __typename        ... on MarketBusinessCenterProfileType {          org_info {            org_key            org_name            org_address {              address_1              address_2              city              state              postal_code              __typename            }            doing_business_in            org_phone            org_fax            contact_email            website_country            __typename          }          logo {            dba_logos            __typename          }          site_info {            about_info {              header_text              body_text              photo_url              photo_redirect_url              __typename            }            area_info {              header_text              body_text_1              body_text_2              __typename            }            footer_links {              link              title              __typename            }            legal_disclaimer            neighborhoods {              boundary_id              name              __typename            }            __typename          }          association {            brokers {              kwuid              first_name              last_name              email              __typename            }            team_leaders {              kwuid              first_name              last_name              email              __typename            }            parent_org {              org_type              org_id              org_info {                org_name                org_address {                  address_1                  address_2                  city                  state                  postal_code                  __typename                }                doing_business_in                org_phone                org_fax                __typename              }              __typename            }            child_org {              org_type              orgs {                org_id                org_info {                  org_name                  __typename                }                __typename              }              __typename            }            __typename          }          branding_enabled          __typename        }      }      __typename    }    deleted_by    created_at    updated_at    deleted_at    __typename  }}"""
            payload = {
                "operationName": "siteOptionsQuery",
                "variables": {"siteId": site_id},
                "query": det_query,
            }
            store_response = session.post(start_url, headers=headers, json=payload)
            store_data = json.loads(store_response.text)

            city = store_data["data"]["SiteOptionsQuery"]["profile"]["profile"][
                "org_info"
            ]["org_address"]["city"]
            if city == "Yuba City":
                city = "<MISSING>"
                state = "<MISSING>"
                zip_code = "<MISSING>"
            else:
                state = store_data["data"]["SiteOptionsQuery"]["profile"]["profile"][
                    "org_info"
                ]["org_address"]["state"]
                zip_code = store_data["data"]["SiteOptionsQuery"]["profile"]["profile"][
                    "org_info"
                ]["org_address"]["postal_code"]
                country_code = store_data["data"]["SiteOptionsQuery"]["profile"][
                    "profile"
                ]["org_info"]["website_country"]
                if store_data["data"]["SiteOptionsQuery"]["profile"]["profile"][
                    "org_info"
                ]["org_address"]["address_2"]:
                    street_address += (
                        ", "
                        + store_data["data"]["SiteOptionsQuery"]["profile"]["profile"][
                            "org_info"
                        ]["org_address"]["address_2"]
                    )

        zip_code = zip_code if zip_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["__typename"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
