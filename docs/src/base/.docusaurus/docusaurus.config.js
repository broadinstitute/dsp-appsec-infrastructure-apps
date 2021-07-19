export default {
  "title": "Broad Institute Security Documentation Portal",
  "tagline": "Open Source Security ",
  "url": "https://broadinstitute.github.io/",
  "baseUrl": "/",
  "onBrokenLinks": "throw",
  "onBrokenMarkdownLinks": "warn",
  "favicon": "img/favicon.ico",
  "organizationName": "broadinstitute",
  "projectName": "dsp-appsec-infrastructure-apps",
  "themeConfig": {
    "navbar": {
      "title": "Broad Institute",
      "logo": {
        "alt": "SDARQ",
        "src": "img/tooling-logo.svg"
      },
      "items": [
        {
          "to": "/docs/SDARQ/Overview",
          "label": "SDARQ",
          "position": "left"
        },
        {
          "href": "https://github.com/broadinstitute/dsp-appsec-infrastructure-apps",
          "label": "GitHub",
          "position": "right"
        }
      ],
      "hideOnScroll": false
    },
    "footer": {
      "style": "dark",
      "links": [
        {
          "title": "SDARQ",
          "items": [
            {
              "label": "Overview",
              "to": "/docs/SDARQ/overview"
            },
            {
              "label": "Quickstart",
              "to": "/docs/SDARQ/quickstart"
            }
          ]
        },
        {
          "title": "Security Guidance",
          "items": [
            {
              "label": "Overview",
              "to": "/docs/Security_Guidance/overview"
            },
            {
              "label": "Cloud Security",
              "to": "/docs/Security_Guidance/Cloud_Security/overview"
            }
          ]
        },
        {
          "title": "Contact",
          "items": [
            {
              "label": "Email",
              "href": "mailto: appsec@broadinstitute.org"
            }
          ]
        }
      ],
      "copyright": "Copyright © 2021 Broad Institute. Developed by the Application Security Team."
    },
    "colorMode": {
      "defaultMode": "light",
      "disableSwitch": false,
      "respectPrefersColorScheme": false,
      "switchConfig": {
        "darkIcon": "🌜",
        "darkIconStyle": {},
        "lightIcon": "🌞",
        "lightIconStyle": {}
      }
    },
    "docs": {
      "versionPersistence": "localStorage"
    },
    "metadatas": [],
    "prism": {
      "additionalLanguages": []
    },
    "hideableSidebar": false
  },
  "presets": [
    [
      "@docusaurus/preset-classic",
      {
        "docs": {
          "sidebarPath": "/Users/ssymonds/projects/dsp-appsec-infrastructure-apps/docs/src/base/sidebars.js",
          "editUrl": "https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/external/docs"
        },
        "theme": {
          "customCss": "/Users/ssymonds/projects/dsp-appsec-infrastructure-apps/docs/src/base/src/css/custom.css"
        }
      }
    ]
  ],
  "baseUrlIssueBanner": true,
  "i18n": {
    "defaultLocale": "en",
    "locales": [
      "en"
    ],
    "localeConfigs": {}
  },
  "onDuplicateRoutes": "warn",
  "customFields": {},
  "plugins": [],
  "themes": [],
  "titleDelimiter": "|",
  "noIndex": false
};