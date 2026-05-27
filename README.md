# Apollo Lead Enrichment Automation

An advanced B2B lead enrichment automation pipeline built using:

- n8n
- Apollo API
- MailMeteor Automation
- FastAPI
- Playwright
- Google Sheets
- Slack Webhooks
- ngrok
- Webhook-triggered frontend integration

This workflow automates:

- Organization discovery
- Decision-maker identification
- Apollo enrichment
- Duplicate prevention
- MailMeteor fallback email discovery
- Google Sheet persistence
- Slack notifications
- Frontend-triggered execution

---

# Architecture Overview

The workflow is fully webhook-driven.

Frontend Website
↓
n8n Webhook Trigger
↓
Google Sheets Input
↓
Apollo Organization Search
↓
Apollo Employee Search
↓
Unique Candidate Selection
↓
Deduplication Engine
↓
Apollo Single Enrichment
↓
MailMeteor Fallback API
↓
Google Sheets Output
↓
Slack Notifications

---

# Features

## Apollo Organization Search

Searches organizations using:
- company name
- cleaned domain

Uses:
- `/v1/organizations/search`

---

## High Value Employee Discovery

Prioritizes titles such as:
- Founder
- CEO
- CTO
- VP Engineering
- Engineering Manager

Uses:
- `/v1/mixed_people/api_search`

---

## Fallback Employee Discovery

If high-value roles are unavailable:
- performs a generic employee search
- retrieves fallback decision makers

---

## Unique Title Filtering

Ensures:
- no repeated titles
- no repeated people
- maximum candidate diversity

---

## Advanced Deduplication Engine

Checks duplicates using:
- Apollo Person ID
- LinkedIn URL
- Verified Email
- Name + Company Matching

Also maintains:
- workflow memory cache
- execution-level domain skipping

---

## Apollo Single Person Enrichment

Uses:
- `/v1/people/match`

Retrieves:
- verified email
- LinkedIn URL
- enrichment metadata

---

## MailMeteor Fallback System

If Apollo cannot retrieve email:

Workflow automatically calls a custom FastAPI microservice that:
- launches Playwright Chromium browser
- automates MailMeteor email discovery
- performs:
  - LinkedIn finder
  - Name + Domain finder

---

## FastAPI Microservice

Custom Python backend exposing:

```http
POST /find-email
```

Accepts:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "domain": "company.com",
  "linkedin_url": "https://linkedin.com/in/johndoe"
}
```

Returns:
```json
{
  "success": true,
  "email": "john@company.com",
  "source": "linkedin_finder"
}
```

---

## Google Sheets Integration

Input Sheet:
- target companies

Output Sheet:
- enriched leads
- enrichment status
- metadata

---

## Slack Notifications

Workflow sends alerts for:
- duplicates
- successful enrichments
- partial enrichments
- fallback scenarios

---

# Frontend Trigger System

A simple frontend website can trigger the workflow through n8n Webhooks.

Supports:
- full enrichment runs
- specific row processing

---

# Technologies Used

## Automation
- n8n

## APIs
- Apollo API
- MailMeteor

## Backend
- FastAPI
- Python

## Browser Automation
- Playwright
- Chromium

## Infrastructure
- ngrok

## Storage
- Google Sheets

## Notifications
- Slack Webhooks

## Frontend
- HTML
- JavaScript

---

# Workflow Logic

## Step 1 — Read Input Rows

Reads company data from Google Sheets.

---

## Step 2 — Optional Row Filtering

Frontend may send:
```json
{
  "targetRow": 6
}
```

Workflow filters execution to a specific row.

---

## Step 3 — Company Search

Apollo organization search retrieves:
- industry
- employee count
- organization metadata

---

## Step 4 — Employee Search

Searches for:
- high-value decision makers

Fallback search activates automatically if necessary.

---

## Step 5 — Candidate Ranking

Filters:
- unique titles
- duplicate employees
- best-fit candidates

---

## Step 6 — Deduplication

Skips:
- previously enriched leads
- already processed companies
- repeated LinkedIn profiles

---

## Step 7 — Apollo Enrichment

Attempts direct enrichment using Apollo.

---

## Step 8 — MailMeteor Fallback

If email missing:
- calls FastAPI endpoint
- Playwright automates MailMeteor
- retrieves email via browser automation

---

## Step 9 — Save Output

Updates Google Sheets using:
- append/update strategy

---

## Step 10 — Slack Notifications

Posts workflow status to Slack.

---

# Running the FastAPI Service

## Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## Start FastAPI Server

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Start ngrok Tunnel

```bash
ngrok http 8000
```

Example:
```text
https://your-ngrok-url.ngrok-free.dev
```

---

# Example Frontend Trigger

```javascript
const WEBHOOK_URL =
  "https://your-n8n-instance/webhook/start-enrichment";

await fetch(WEBHOOK_URL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    targetRow: 6
  })
});
```

---

# n8n Workflow Highlights

## Intelligent Looping

Uses:
- Split In Batches
- fallback routing
- early exit conditions

---

## Dynamic Webhook Triggering

Supports:
- frontend integration
- API-driven execution
- selective row processing

---

## Silent Skip Logic

Avoids:
- unnecessary Slack spam
- repeated enrichments
- wasted Apollo credits

---

# Repository Structure

```text
.
├── workflow.json
├── main.py
├── requirements.txt
|─── test.html
├── README.md
```

---

# Credits

Built using:
- Apollo
- MailMeteor
- n8n
- Playwright
- FastAPI
- Google Sheets
- Slack

---

# Workflow Documentation

Workflow JSON:
- `Webhook_apollo_v1.json`
