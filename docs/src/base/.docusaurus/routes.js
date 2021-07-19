
import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';
export default [
{
  path: '/',
  component: ComponentCreator('/','deb'),
  exact: true,
},
{
  path: '/__docusaurus/debug',
  component: ComponentCreator('/__docusaurus/debug','3d6'),
  exact: true,
},
{
  path: '/__docusaurus/debug/config',
  component: ComponentCreator('/__docusaurus/debug/config','914'),
  exact: true,
},
{
  path: '/__docusaurus/debug/content',
  component: ComponentCreator('/__docusaurus/debug/content','c28'),
  exact: true,
},
{
  path: '/__docusaurus/debug/globalData',
  component: ComponentCreator('/__docusaurus/debug/globalData','3cf'),
  exact: true,
},
{
  path: '/__docusaurus/debug/metadata',
  component: ComponentCreator('/__docusaurus/debug/metadata','31b'),
  exact: true,
},
{
  path: '/__docusaurus/debug/registry',
  component: ComponentCreator('/__docusaurus/debug/registry','0da'),
  exact: true,
},
{
  path: '/__docusaurus/debug/routes',
  component: ComponentCreator('/__docusaurus/debug/routes','244'),
  exact: true,
},
{
  path: '/markdown-page',
  component: ComponentCreator('/markdown-page','be1'),
  exact: true,
},
{
  path: '/docs',
  component: ComponentCreator('/docs','6bc'),
  
  routes: [
{
  path: '/docs/SDARQ/How_It_Works/kubernetes-cluster',
  component: ComponentCreator('/docs/SDARQ/How_It_Works/kubernetes-cluster','9d5'),
  exact: true,
},
{
  path: '/docs/SDARQ/How_It_Works/sdarq-apps',
  component: ComponentCreator('/docs/SDARQ/How_It_Works/sdarq-apps','62f'),
  exact: true,
},
{
  path: '/docs/SDARQ/Overview',
  component: ComponentCreator('/docs/SDARQ/Overview','c69'),
  exact: true,
},
{
  path: '/docs/SDARQ/Quickstart',
  component: ComponentCreator('/docs/SDARQ/Quickstart','402'),
  exact: true,
},
{
  path: '/docs/Security_Guidance/Cloud_Security/Overview',
  component: ComponentCreator('/docs/Security_Guidance/Cloud_Security/Overview','898'),
  exact: true,
},
{
  path: '/docs/Security_Guidance/Overview',
  component: ComponentCreator('/docs/Security_Guidance/Overview','11f'),
  exact: true,
},
]
},
{
  path: '*',
  component: ComponentCreator('*')
}
];
