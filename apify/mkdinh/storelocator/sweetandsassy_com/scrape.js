const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

function formatHoursOfOperation(serializedHours) {
  const REPLACE_OPEN_BRACKET_REGEX = /\[/g;
  const REPLACE_CLOSE_BRACKET_REGEX = /\]/g;
  const REMOVE_TRAILING_COLON_REGEX = /,$/;
  const REMOVE_SECONDS_REGEX = /:\d\d$/;

  const cleaned = serializedHours
    .replace(REPLACE_OPEN_BRACKET_REGEX, '{')
    .replace(REPLACE_CLOSE_BRACKET_REGEX, '},')
    .replace(REMOVE_TRAILING_COLON_REGEX, '');

  const data = JSON.parse(`[${cleaned}]`);
  const hours = data.map((day) => ({
    day: day.Interval,
    open: day.OpenTime.replace(REMOVE_SECONDS_REGEX, ''),
    close: day.CloseTime.replace(REMOVE_SECONDS_REGEX, ''),
  }));

  return hours.length ? JSON.stringify(hours) : null;
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.sweetandsassy.com/locations',
    data: {
      type: 'html',
    },
  });

  const launchPuppeteerOptions = {
    headless: true,
    stealth: true,
    useChrome: true,
    useApifyProxy: false,
    groups: ['RESIDENTIAL'],
  };

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    launchPuppeteerOptions,
    async handlePageFunction({ page }) {
      const page_url = 'https://www.sweetandsassy.com/locations?CallAjax=GetLocations';
      const data = await page.evaluate(async (page) => {
        const response = await fetch(page); // eslint-disable-line
        const data = response.json();
        return data;
      }, page_url);

      const pois = data.map((location) => {
        return {
          locator_domain: 'sweetandsassy.com',
          page_url: page_url,
          location_name: getOrDefault(location.FranchiseLocationName),
          store_number: getOrDefault(location.FranchiseLocationID),
          street_address: getOrDefault(location.Address1),
          city: getOrDefault(location.City),
          state: getOrDefault(location.State),
          zip: getOrDefault(location.ZipCode),
          country_code: getOrDefault(location.Country),
          latitude: getOrDefault(location.Latitude),
          longitude: getOrDefault(location.Longitude),
          phone: getOrDefault(location.Phone),
          hours_of_operation: getOrDefault(formatHoursOfOperation(location.LocationHours)),
          location_type: MISSING,
        };
      });

      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
