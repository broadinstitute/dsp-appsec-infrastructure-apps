/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'Broad Institute Application Security Documentation',
  tagline: 'Application Security Guidance and Tools',
  url: 'https://broadinstitute.github.io/', //GenericCo,
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'broadinstitute', // GenericCo
  projectName: 'dsp-appsec-infrastructure-apps', // GenericCo
  customFields: {
    sdarq_url: 'https://sdarq.dsp-appsec.broadinstitute.org',
    internal_url: 'https://dsp-security.broadinstitute.org/'
  },
  themeConfig: {
    navbar: {
      title: 'Broad Institute',
      logo: {
        alt: 'SDARQ',
        src: 'img/tooling-logo.svg',
      },
      items: [
        {to: '/docs/Overview', label: 'Overview', position: 'left'},
        {to: '/docs/Security_Guidance/Overview', label: 'Security Guidance', position: 'left'},
        {href: 'https://sdarq.dsp-appsec.broadinstitute.org', label: 'SDARQ', position: 'left'},
        {href: 'https://dsp-security.broadinstitute.org/', label: 'Internal', position: 'right'},
        {href: 'mailto: appsec@broadinstitute.org', label: 'Contact', position: 'right'},
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
            'https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/docs',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
