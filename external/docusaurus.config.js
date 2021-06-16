/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'Broad Institute Security Documentation Portal',
  tagline: 'Open Source Security ',
  url: 'https://broadinstitute.github.io/', //GenericCo
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'broadinstitute', // GenericCo
  projectName: 'dsp-appsec-infrastructure-apps', // GenericCo
  themeConfig: {
    navbar: {
      title: 'Broad Institute',
      logo: {
        alt: 'SDARQ',
        src: 'img/tooling-logo.svg',
      },
      items: [
        {to: '/docs/SDARQ/Overview', label: 'SDARQ', position: 'left'},
        {
          href: 'https://github.com/broadinstitute/dsp-appsec-infrastructure-apps',
          label: 'GitHub',
          position: 'right'
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'SDARQ',
          items: [
            {
              label: 'Overview',
              to: '/docs/SDARQ/overview',
            },
            {
              label: 'Quickstart',
              to: '/docs/SDARQ/quickstart',
            }
          ],
        },
        {
          title: 'Security Guidance',
          items: [
            {
              label: 'Overview',
              to: '/docs/Security_Guidance/overview',
            },
            {
              label: 'Cloud Security',
              to: '/docs/Security_Guidance/Cloud_Security/overview',
            }
          ],
        },
        {
          title: 'Contact',
          items: [
            {
              label: 'Email',
              href: 'mailto: appsec@broadinstitute.org',
            },
          ],
        },
      ],
      copyright: `Copyright © 2021 Broad Institute. Developed by the Application Security Team.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/external/docs',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
