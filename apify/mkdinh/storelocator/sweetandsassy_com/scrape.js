const Apify = require('apify');
const { difference } = require('lodash');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  return value || MISSING;
}

const Days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

function fillMissingDays(data) {
  const availableDays = data.map((x) => x.Interval);
  const diff = difference(Days, availableDays);

  if (diff.length === 1) {
    const dayLabel = diff[0];
    data.map((day) => {
      if (!day.Interval) {
        day.Interval = dayLabel;
      }
    });
  } else if (diff.length === Days.length) {
    data.map((day, idx) => {
      day.Interval = Days[idx];
    });
  } else if (diff.length > 1) {
    throw Error();
  }

  const ordered = [];
  Days.forEach((day) => {
    const found = data.find((x) => x.Interval === day);
    ordered.push(found);
  });

  if (ordered.length < 7) {
    throw new Error();
  }

  return ordered;
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
  const days = fillMissingDays(data);
  const hours = days.map((day) => {
    const interval = day.Interval;
    const open = day.OpenTime.replace(REMOVE_SECONDS_REGEX, '');
    const close = day.CloseTime.replace(REMOVE_SECONDS_REGEX, '');

    return `${interval}: ${open}-${close}`;
  });

  return hours.length ? hours.join(', ') : null;
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
