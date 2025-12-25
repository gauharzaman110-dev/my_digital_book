import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
// import { useBlogPostData } from '@docusaurus/plugin-content-blog/client'; // Import blog data hook (COMMENTED OUT)

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">
          Explore the fascinating intersection of Artificial Intelligence and Embodied Systems.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Your Journey 🚀
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageSection({ children, title, description, isLight = false }) {
  return (
    <section className={clsx(styles.homepageSection, { [styles.lightBackground]: isLight })}>
      <div className="container">
        {title && <h2 className="text--center margin-bottom--lg">{title}</h2>}
        {description && <p className="text--center margin-bottom--lg">{description}</p>}
        {children}
      </div>
    </section>
  );
}




export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive guide to Physical AI and Humanoid Robotics.">
      <HomepageHeader />
      <main>
        <HomepageSection title="What You'll Discover" description="Dive deep into the core concepts and cutting-edge advancements.">
          <div className="row">
            <div className="col col--4 margin-bottom--md">
              <div className={clsx('card', styles.featureCard)}>
                <div className="card__header"><h3>Foundational AI</h3></div>
                <div className="card__body">
                  <p>Understand the AI principles that drive intelligent physical systems, from learning algorithms to decision-making processes.</p>
                </div>
              </div>
            </div>
            <div className="col col--4 margin-bottom--md">
              <div className={clsx('card', styles.featureCard)}>
                <div className="card__header"><h3>Robotics Mechanics</h3></div>
                <div className="card__body">
                  <p>Explore kinematics, dynamics, and the engineering marvels behind robot locomotion, manipulation, and physical interaction.</p>
                </div>
              </div>
            </div>
            <div className="col col--4 margin-bottom--md">
              <div className={clsx('card', styles.featureCard)}>
                <div className="card__header"><h3>Human-Robot Synergy</h3></div>
                <div className="card__body">
                  <p>Delve into the complexities of human-robot interaction, ethical considerations, and collaborative intelligence in shared environments.</p>
                </div>
              </div>
            </div>
          </div>
        </HomepageSection>

        <HomepageSection title="Why This Book?" description="Your essential guide to the future of intelligent machines." isLight={true}>
          <div className="row">
            <div className="col col--6 margin-bottom--md">
              <div className="card">
                <div className="card__header"><h3>Comprehensive Coverage</h3></div>
                <div className="card__body"><p>From theoretical foundations to real-world applications and future trends, get a holistic view of the field.</p></div>
              </div>
            </div>
            <div className="col col--6 margin-bottom--md">
              <div className="card">
                <div className="card__header"><h3>Academic Rigor</h3></div>
                <div className="card__body"><p>Authored with academic precision, suitable for students, researchers, and professionals.</p></div>
              </div>
            </div>
          </div>
        </HomepageSection>

        {/* <LatestBlogPosts /> */} {/* COMMENTED OUT */}
      </main>
    </Layout>
  );
}
