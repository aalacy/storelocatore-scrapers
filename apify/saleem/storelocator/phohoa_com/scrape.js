const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const $ = cheerio.load(await request.post({
    url: 'https://phohoa.com/wp-admin/admin-ajax.php',
    form:{
      'store_locatore_search_input':"San Jose, CA, USA",
      'store_locatore_search_lat':'37.3382082',
      'store_locatore_search_lng':'-121.88632860000001',
      'store_locatore_search_radius':'50000',
      'action':'make_search_request',
      'lat':'37.3382082',
      'lng':'-121.88632860000001'
    }
  }));
  const records = [];

  $('.store-locator-item').each((_, elem) => {
    const location_name = $('.wpsl-name', elem).text().trim();
    // Remove coming soon locations
    if (location_name.indexOf('Coming Soon') !== -1) {
      // console.log(location_name);
      return;
    }
    const addressMatch = $('.wpsl-city', elem).text().trim().match(/^(?<city>.*),\s(?<state>.*)\s(?<zip>[\dA-Z]{5,6})$/)
    // Remove non-US locations
    if (!addressMatch) {
      // console.log($('.wpsl-city', elem).text().trim())
      return;
    }
    let { city, state, zip } = addressMatch.groups;
    // Canadian addresses don't have state included
    if (state === "") {
      state = '<MISSING>';
    }
    const { latitude, longitude } = $('.store-direction', elem).attr('data-direction').match(
      /^(?<latitude>-?\d{1,3}\.\d*),(?<longitude>-?\d{1,3}\.\d*)$/
    ).groups
    let phone = $('.wpsl-phone', elem).text().trim();
    if (phone === '') {
      phone = '<MISSING>'
    }

    records.push({
      locator_domain: 'phohoa.com',
      location_name,
      street_address: $('.wpsl-address', elem).text().trim(),
      city,
      state,
      zip,
      country_code: '<MISSING>',
      store_number: $(elem).attr('data-store-id'),
      phone,
      location_type: '<MISSING>',
      latitude,
      longitude,
      hours_of_operation: '<MISSING>'  
    })
  })

	return records;

	// End scraper

}
