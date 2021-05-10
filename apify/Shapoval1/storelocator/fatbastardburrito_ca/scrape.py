import csv
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    locator_domain = "https://www.fatbastardburrito.ca/"
    api_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.addressInputAtlasProvider%3Atrue%2Cspecs.thunderbolt.videobox_united%3Atrue%2Cspecs.thunderbolt.seoFriendlyDropDownMenu%3Atrue%2Cspecs.thunderbolt.stylableInteractions%3Atrue%2Cspecs.thunderbolt.image_placeholder%3Atrue%2Cspecs.thunderbolt.safari_sticky_fix%3Atrue%2Ctb_UploadButtonFixValidationNotRequired%3Atrue%2Cspecs.thunderbolt.tb_pinLayerDockedBottom%3Atrue%2Cspecs.thunderbolt.dontMergeAdvancedSeoDataForML%3Atrue%2Cspecs.thunderbolt.editor_elements_site_assets%3Atrue%2Cspecs.thunderbolt.tb_media_layout_by_effect%3Atrue%2Cspecs.thunderbolt.shouldRenderPinnedLayerAfterMeshContainer%3Atrue&contentType=application%2Fjson&deviceType=Desktop&dfCk=6&dfVersion=1.1248.0&experiments=bv_cartPageResponsiveLayoutFixer%2Cbv_migrateResponsiveLayoutToSingleLayoutData%2Cbv_migrateResponsiveToVariantsModels%2Cbv_removeMenuDataFromPageJson%2Cbv_remove_add_chat_viewer_fixer%2Cdm_removeMissingResponsiveRefs%2Csv_unquoteUsedFontsInDataFixer%2Csv_usedFontsDataFixer&externalBaseUrl=https%3A%2F%2Fwww.fatbastardburrito.ca&fileId=a33fe7f8.bundle.min&isHttps=true&isInSeo=false&isMultilingualEnabled=false&isPremiumDomain=true&isUrlMigrated=true&isWixCodeOnPage=false&isWixCodeOnSite=true&language=en&languageResolutionMethod=QueryParam&metaSiteId=a6505709-758d-45d7-b82c-3b144f4b6e4d&migratingToOoiWidgetIds=14cefc05-d163-dbb7-e4ec-cd4f2c4d6ddd&module=thunderbolt-features&originalLanguage=en&osType=Windows&pageId=19e956_c7140f3a907574f7ec3c1b226a134004_1074.json&quickActionsMenuEnabled=false&registryLibrariesTopology=%5B%7B%22artifactId%22%3A%22editor-elements%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.5150.0%22%2C%22manifestName%22%3A%22library-manifest%22%7D%2C%7B%22artifactId%22%3A%22editor-elements-design-systems%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.5150.0%22%2C%22manifestName%22%3A%22design-systems-manifest%22%7D%5D&remoteWidgetStructureBuilderVersion=1.226.0&siteId=9295f53f-274e-4eec-8240-4cb97a4798bd&siteRevision=1074&staticHTMLComponentUrl=https%3A%2F%2Fwww-fatbastardburrito-ca.filesusr.com%2F&tbElementsSiteAssets=siteAssets.07fb4d93.bundle.min.js&useSandboxInHTMLComp=false&viewMode=desktop"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js["structure"]["siteFeaturesConfigs"]["tpa"]["pagesData"].values():
        slug = j.get("pageUriSEO")
        page_url = f"{locator_domain}{slug}"
        if page_url.find("about") != -1:
            continue
        if page_url.find("my") != -1:
            continue
        if page_url.find("blank") != -1:
            continue
        if page_url.find("locations") != -1:
            continue
        if page_url.find("page") != -1:
            continue
        if page_url.find("checkout") != -1:
            continue
        if page_url.find("shop") != -1:
            continue
        if page_url.find("employ") != -1:
            continue
        if page_url.find("franchising") != -1:
            continue
        if page_url.find("copy-2-of-kingston") != -1:
            continue
        location_name = j.get("title")
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        ad = tree.xpath(
            "//div[.//span[contains(text(), 'address')]]/following-sibling::div[1]//text()"
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad).split("@")[0].strip()
        ad = " ".join(ad.split(" ​ ")[:-1])

        phone = ad.split("Tel:")[1].strip()
        ad = ad.split("Tel:")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city
        state = a.state
        postal = a.postcode
        country_code = "Canada"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = tree.xpath(
            "//div[.//span[contains(text(), 'hours')]]/following-sibling::div[1]//span[@class='color_12']//text() | //span[contains(text(), 'Sunday')]//text()"
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
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
