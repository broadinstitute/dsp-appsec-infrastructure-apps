import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

const FeatureList = [
  {
    title: 'Security Automation Tools',
    Svg: require('../../static/img/tooling-logo.svg').default,
    description: (
      <>
        Broad Institute provides a number of open source tools to
        make security simpler, including SDARQ, our integrated security solution.
      </>
    ),
  },
  {
    title: 'Open Source Security',
    Svg: require('../../static/img/tooling-logo.svg').default,
    description: (
      <>
        Docusaurus lets you focus on your docs, and we&apos;ll do the chores. Go
        ahead and move your docs into the <code>docs</code> directory.
      </>
    ),
  },
  {
    title: 'Internal Documentation for Broadies',
    Svg: require('../../static/img/tooling-logo.svg').default,
    description: (
      <>
        Click here if you are a Broad member looking for more information on
        internal security tools and processes.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
