# Master Reference

## Format Rules

- Contact line format: `phone | email | city, ST | linkedin.com/in/alexrivera`
- Resume max 2 pages
- Skills/Core Competencies at bottom, after Education
- Professional summary in narrative paragraph format
- Headline mirrors target role title + positioning

---

## Professional Summary

Customer obsessed technology leader who builds platforms that simplify complexity and improve user outcomes. 12 years leading product and engineering teams across e-commerce, fintech, and SaaS, with a track record of scaling organizations from startup to enterprise maturity. Gets in the work alongside the team; leads from the front.

---

## Core Strengths & Skills

### Leadership & Management
Team building (8-40 person orgs), P&L ownership ($5M-$20M), vendor management, executive stakeholder alignment, cross-functional program delivery, M&A technology integration

### Product & Strategy
Product roadmap development, OKR frameworks, market analysis, go-to-market strategy, customer research, competitive intelligence, pricing strategy

### Technical & Domain Expertise
Cloud architecture (AWS, GCP), data pipeline design, API platform development, payment systems, fraud detection, identity and access management, HIPAA/SOC2 compliance

### Tools & Technologies
AWS (Lambda, ECS, S3, RDS, DynamoDB, CloudFormation), GCP (BigQuery, Cloud Run), Terraform, Kubernetes, Python, TypeScript, React, PostgreSQL, Redis, Kafka, Snowflake, dbt, Datadog, PagerDuty, Salesforce, Jira, Confluence, Figma, Amplitude, LaunchDarkly

---

## Career History

### Meridian Financial Technologies | San Francisco, CA | March 2021 - Present
**VP of Product & Engineering**

- Built and scaled the product engineering organization from 12 to 38 across five cross-functional teams
- Led migration from monolithic Rails app to microservices architecture, reducing deploy time from 4 hours to 15 minutes
- Launched real-time fraud detection platform processing 2M+ transactions/day with 99.97% accuracy
- Drove annual recurring revenue from $8M to $24M through platform expansion and enterprise sales enablement
- Established OKR framework and quarterly planning cadence adopted across all 150-person engineering org

### Beacon Commerce | Portland, OR | June 2018 - February 2021
**Director of Engineering**

- Owned the e-commerce platform serving 4M monthly active users and $180M annual GMV
- Reduced checkout abandonment by 23% through A/B tested UX improvements and payment flow optimization
- Built real-time inventory sync system across 200+ retail locations, eliminating oversell incidents
- Led SOC2 Type II certification, establishing security practices for enterprise client acquisition
- Managed $4.5M annual technology budget; negotiated vendor contracts saving $600K/year

### Launchpad SaaS | Seattle, WA | January 2015 - May 2018
**Senior Product Manager**

- Defined and shipped the analytics dashboard used by 85% of enterprise customers
- Conducted 200+ customer interviews to identify top pain points; prioritized roadmap that reduced churn by 18%
- Partnered with engineering to build API platform generating $2.1M in partner revenue within first year
- Led cross-functional team of 8 (engineering, design, data science) through agile delivery cadence

### TechStart Consulting | Seattle, WA | August 2012 - December 2014
**Software Engineer / Technical Lead**

- Delivered client projects across healthcare, retail, and financial services verticals
- Built patient scheduling system for regional hospital network serving 150K patients/year
- Promoted to tech lead within 18 months; managed team of 4 engineers

---

## STAR Projects

### Real-Time Fraud Detection Platform (Meridian)

- **Situation**: Meridian processed $500M+ annually in transactions but relied on batch-processed fraud rules with a 6-hour detection lag. Chargebacks were costing $2.4M/year and growing 15% quarter over quarter.
- **Task**: Design and ship a real-time fraud detection system that could score transactions in under 200ms while maintaining low false-positive rates to avoid blocking legitimate customers.
- **Action**: Assembled a cross-functional team of 6 (ML engineers, backend, data). Evaluated vendor solutions (Sift, Sardine) but built in-house for cost control and model customization. Architected a streaming pipeline with Kafka, feature store on Redis, and ML scoring service on ECS. Implemented shadow mode for 4 weeks before going live. Built an ops dashboard for the fraud team to tune thresholds in real time.
- **Result**: Reduced fraud losses by 72% ($1.7M annual savings). Mean scoring latency of 45ms. False positive rate of 0.03%, well below the 0.1% target. System now processes 2M+ transactions/day.
- **Key Metrics**: "$1.7M annual fraud reduction", "72% loss decrease", "45ms latency", "2M+ daily transactions", "0.03% false positive rate"
- **Keywords**: real-time fraud detection, ML pipeline, Kafka, streaming architecture, risk management, payment systems

### Monolith to Microservices Migration (Meridian)

- **Situation**: The core platform was a 7-year-old Rails monolith. Deploys took 4 hours, test suites ran 90 minutes, and a single bad deploy could take down the entire platform. Engineering velocity had stalled.
- **Task**: Decompose the monolith into independently deployable services without disrupting the existing $24M revenue stream or the 38-person engineering team's velocity.
- **Action**: Defined domain boundaries using event storming workshops with the full engineering team. Prioritized extraction by business risk and team pain points. Introduced a strangler fig pattern with API gateway routing. Migrated authentication, payments, and notifications as the first three services. Established CI/CD standards (GitHub Actions, Terraform, ECS Fargate) that became the template for all subsequent services.
- **Result**: Deploy time reduced from 4 hours to 15 minutes. Test suite from 90 minutes to 8 minutes per service. Zero-downtime deploys became standard. Engineering velocity (PRs merged/week) increased 3x within 6 months.
- **Key Metrics**: "4hr to 15min deploys", "90min to 8min test suite", "3x engineering velocity", "zero-downtime deploys"
- **Keywords**: microservices migration, strangler fig pattern, CI/CD, Terraform, ECS Fargate, domain-driven design

### E-Commerce Checkout Optimization (Beacon)

- **Situation**: Beacon's checkout flow had a 67% abandonment rate, significantly above the industry benchmark of 55%. The CEO identified checkout conversion as the top priority for the upcoming fiscal year.
- **Task**: Reduce checkout abandonment by at least 15% within two quarters through data-driven UX improvements and payment flow optimization.
- **Action**: Instrumented the full checkout funnel with Amplitude. Identified three major drop-off points: account creation wall, shipping cost surprise, and payment method limitations. Ran 12 A/B tests over 8 weeks. Shipped guest checkout, transparent shipping calculator, and Apple Pay/Google Pay integration. Partnered with the payments team to add buy-now-pay-later through Affirm.
- **Result**: Checkout abandonment dropped from 67% to 51.6% (23% relative reduction). Conversion rate improved 31%. Annual GMV impact estimated at $12M. Guest checkout alone drove 40% of the improvement.
- **Key Metrics**: "23% abandonment reduction", "31% conversion improvement", "$12M GMV impact", "12 A/B tests"
- **Keywords**: checkout optimization, A/B testing, conversion rate, payment integration, Amplitude, e-commerce

---

## Proven Narrative Framings

- "Built and scaled a product engineering organization from 12 to 38, establishing the OKR framework and cross-functional team structure that drove ARR from $8M to $24M"
- "Led a zero-downtime migration from monolith to microservices, reducing deploy cycles from 4 hours to 15 minutes and tripling engineering velocity"
- "Drove a data-informed checkout optimization initiative across 12 A/B tests, reducing abandonment by 23% and generating an estimated $12M in incremental GMV"
- "Established real-time fraud detection capabilities that reduced losses by 72% while maintaining a 0.03% false positive rate across 2M+ daily transactions"

---

## Education & Certifications

### MBA | University of Washington Foster School of Business | Seattle, WA
### B.S. Computer Science | Oregon State University | Corvallis, OR

### Certifications
- AWS Solutions Architect, Professional
- Certified Scrum Master (CSM)

---

## Applications Tracker

| Date | Company | Role | Status | Folder |
|---|---|---|---|---|
| 2026-03-15 | Stripe | Director of Engineering, Payments | Applied | 2026-03-15_Stripe_Director-Engineering-Payments |
| 2026-03-20 | Coinbase | VP Engineering | Applied | 2026-03-20_Coinbase_VP-Engineering |
