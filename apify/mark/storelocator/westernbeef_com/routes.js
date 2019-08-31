const Apify = require('apify');

const enqueueDetailPages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a.Button',
  pseudoUrls: [
    'http://westernbeef.com/western-beef---[.*].html',
  ],
  userData: {
    urlType: 'detail',
  },
});

module.exports = {
  enqueueDetailPages,
};
