/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// See https://docusaurus.io/docs/site-config for all the possible
// site configuration options.

// List of projects/orgs using your project for the users page.
const users = [
  {
    caption: 'broadinstitute',
    // You will need to prepend the image path with your baseUrl
    // if it is not '/', like: '/test-site/img/image.jpg'.
    image: '/img/broad-logo.jpg',
    infoLink: 'https://www.broadinstitute.org',
    pinned: true,
  },
  // Add another user here
];

const siteConfig = {
  title: 'AppSec Infrastructure Automation', // Title for your website.
  tagline: 'Broad Institute - DSP AppSec Team',
  url: 'https://docs.dsp-appsec.broadinstitute.org', // Your website URL
  baseUrl: '/', // Base URL for your project */
  // For github.io type URLs, you would set the url and baseUrl like:
  //   url: 'https://facebook.github.io',
  //   baseUrl: '/test-site/',

  // Used for publishing and more
  projectName: 'dsp-appsec-infrastructure-automation',
  organizationName: 'Data Sciences Platform - Broad Institute',
  // For top-level user or org sites, the organization is still the same.
  // e.g., for the https://JoelMarcey.github.io site, it would be set like...
  //   organizationName: 'JoelMarcey'



  // For no header links in the top nav bar -> headerLinks: [],
  headerLinks: [
    { doc: 'kubernetes-cluster', label: 'Docs' },
    { doc: 'security-apps', label: 'Apps' },
    { page: 'help', label: 'Help' },
    { blog: true, label: 'Blog' },
  ],

  // If you have users set above, you add it here:
  users,

  /* path to images for header/footer */
  headerIcon: 'img/broad-logo-white.png',
  footerIcon: 'img/broad-logo-white.png',
  favicon: 'img/broad-logo-white.png',

  /* Colors for website */
  colors: {
    primaryColor: '#396fc3',
    secondaryColor: '#fff6dd',
    backgroundColor: '#fff6dd',
  },


  // Search config through Algolia
  algolia: {
    apiKey: 'my-api-key',
    indexName: 'my-index-name',
    algoliaOptions: {} // Optional, if provided by Algolia
  },


  /* Custom fonts for website */
  /*
  fonts: {
    myFont: [
      "Times New Roman",
      "Serif"
    ],
    myOtherFont: [
      "-apple-system",
      "system-ui"
    ]
  },
  */

  // This copyright info is used in /core/Footer.js and blog RSS/Atom feeds.
  copyright: `Copyright © ${new Date().getFullYear()} DSP AppSec - Broad Institute`,

  highlight: {
    // Highlight.js theme to use for syntax highlighting in code blocks.
    theme: 'default',
  },

  // Add custom scripts here that would be placed in <script> tags.
  scripts: ['https://buttons.github.io/buttons.js'],

  // On page navigation for the current documentation page.
  onPageNav: 'separate',
  // No .html extensions for paths.
  cleanUrl: true,

  // Open Graph and Twitter card images.
  ogImage: 'img/undraw_online.svg',
  twitterImage: 'img/undraw_tweetstorm.svg',

  // For sites with a sizable amount of content, set collapsible to true.
  // Expand/collapse the links and subcategories under categories.
  // docsSideNavCollapsible: true,

  // Show documentation's last contributor's name.
  // enableUpdateBy: true,

  // Show documentation's last update time.
  // enableUpdateTime: true,

  // You may provide arbitrary config keys to be used as needed by your
  // template. For example, if you need your repo's URL...
  repoUrl: 'https://github.com/broadinstitute/dsp-appsec-infrastructure-apps',
};

module.exports = siteConfig;
