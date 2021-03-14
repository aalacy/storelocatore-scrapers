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


def get_coords_hours():
    coords = []
    hours = []

    session = SgRequests()
    url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.addressInputAtlasProvider%3Atrue%2Cspecs.thunderbolt.videobox_united%3Atrue%2Cspecs.thunderbolt.seoFriendlyDropDownMenu%3Atrue%2Cspecs.thunderbolt.stylableInteractions%3Atrue%2Cspecs.thunderbolt.image_placeholder%3Atrue%2Cspecs.thunderbolt.tb_omitInlineContent%3Atrue%2Cspecs.thunderbolt.safari_sticky_fix%3Atrue%2Ctb_UploadButtonFixValidationNotRequired%3Atrue%2Cspecs.thunderbolt.dontMergeAdvancedSeoDataForML%3Atrue%2Cspecs.thunderbolt.editor_elements_site_assets%3Atrue%2Cspecs.thunderbolt.tb_media_layout_by_effect%3Atrue%2Cspecs.thunderbolt.shouldRenderPinnedLayerAfterMeshContainer%3Atrue&contentType=application%2Fjson&deviceType=Desktop&dfCk=6&dfVersion=1.1235.0&experiments=bv_migrateResponsiveLayoutToSingleLayoutData%2Cbv_migrateResponsiveToVariantsModels%2Cbv_remove_add_chat_viewer_fixer%2Cdm_removeMissingResponsiveRefs%2Csv_unquoteUsedFontsInDataFixer%2Csv_usedFontsDataFixer&externalBaseUrl=https%3A%2F%2Fwww.chochosan.com&fileId=62bf79f4.bundle.min&isHttps=true&isInSeo=false&isMultilingualEnabled=false&isPremiumDomain=true&isUrlMigrated=true&isWixCodeOnPage=false&isWixCodeOnSite=false&language=en&languageResolutionMethod=QueryParam&metaSiteId=680ef2d7-b12f-412f-945a-0ad3164683b5&module=thunderbolt-features&originalLanguage=en&osType=Windows&pageId=329900_0ac8a3c01be23c1c23da45a9ee8d3128_290.json&quickActionsMenuEnabled=false&registryLibrariesTopology=%5B%7B%22artifactId%22%3A%22editor-elements%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.4972.0%22%2C%22manifestName%22%3A%22library-manifest%22%7D%2C%7B%22artifactId%22%3A%22editor-elements-design-systems%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.4972.0%22%2C%22manifestName%22%3A%22design-systems-manifest%22%7D%5D&remoteWidgetStructureBuilderVersion=1.226.0&siteId=ce06b00c-2b28-4b9c-9bea-b223d6fa1297&siteRevision=305&staticHTMLComponentUrl=https%3A%2F%2Fwww-chochosan-com.filesusr.com%2F&tbElementsSiteAssets=siteAssets.6f27bc6d.bundle.min.js&useSandboxInHTMLComp=false&viewMode=desktop"
    r = session.get(url)
    js = r.json()
    for j in js["props"]["render"]["compProps"].values():
        skin = j.get("skin") or ""
        if "GoogleMapSkin" in skin:
            j = j["mapData"]["locations"][0]
            lat = j.get("latitude")
            lng = j.get("longitude")
            coords.append((lat, lng))
        if "WRichTextNewSkin" in skin:
            source = j.get("html") or "<html></html>"
            if "Mon" in source:
                _tmp = []
                tree = html.fromstring(source)
                text = tree.xpath(".//text()")
                for t in text:
                    if not t.strip() or "Teppan" in t:
                        continue
                    if ":" in t:
                        if "(" in t:
                            t = t.split("(")[0].strip()
                        _tmp.append(t.strip())

                hours.append(";".join(_tmp))

    return coords, hours


def fetch_data():
    out = []
    i = 0
    locator_domain = "https://www.chochosan.com/"
    page_url = "https://www.chochosan.com/location"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    coords, hours = get_coords_hours()
    divs = tree.xpath(
        "//div[./a[contains(@href, 'sushi-dining-menu')]]/preceding-sibling::div[1]"
    )

    for d in divs:
        _tmp = []
        cnt = 0
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        for l in line:
            if l.startswith("(") and not l[1].isdigit():
                break
            cnt += 1

        location_name = " ".join(line[:cnt])
        line = line[cnt + 1 :]
        if line[-1].startswith("("):
            phone = line[-1]
            line = line[:-1]
        else:
            phone = "<MISSING>"

        street_address = " ".join(line[:-1]).replace(")", "").strip()
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        latitude, longitude = coords[i]
        location_type = "<MISSING>"
        hours_of_operation = hours[i]

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
        i += 1

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
