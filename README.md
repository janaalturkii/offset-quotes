# Offset Events — AI Quote Generator

A Django web application that turns a plain-language client brief into a structured, priced, branded quotation — built for **Offset Events**, my own brand activation and event company concept in Jeddah.

**Training context:** Week 7–8 capstone project, practical training at Backyard Symphony.

## The problem

Writing a quote for a new client currently means manually reading their request, figuring out what categories of service apply (venue, lighting, branding, staffing...), estimating realistic pricing for each, and formatting all of it into something professional to send back. For a small event company, this eats time that should go toward actually running events — and inconsistent, slow quotes cost credibility with clients.

## The idea

Instead of me doing that translation by hand every time, this app does it in seconds: paste in a client's message, get back a structured, itemized, branded PDF quote ready to send.

This isn't a hypothetical tool — it's built for a business I'm actually developing, so every design decision (categories, pricing realism, branding, VAT-inclusive language) reflects a real operational need, not just a coding exercise.

## What it does

1. **Dashboard** — paste a client's brief in plain language (e.g. *"120 guests, outdoor event, need lighting and branding, budget around 15000 SAR"*)
2. **Claude API call** — the brief is sent to Claude (Haiku model) with a system prompt trained on Offset Events' service categories, and returns structured JSON: a summary, 3–7 realistic priced line items, and clarifying notes
3. **Database storage** — every quote and its line items are saved, so nothing is lost and quotes can be revisited or edited
4. **Quote detail page** — view the full breakdown in-browser
5. **Branded PDF export** — one click generates a client-ready PDF matching Offset Events' navy branding, with a calculated total and VAT-inclusive note
6. **Django admin** — browse, edit, or manually correct any quote and its line items directly

## Why Claude API, and why this counts as meaningful use

The app doesn't just wrap Claude in a chat box — it uses it to do real structured business reasoning: inferring likely service categories from an unstructured request, estimating market-realistic Jeddah pricing, and flagging assumptions a human would want to double-check (e.g. *"catering not mentioned — confirm with client"*). That's the kind of judgment call that used to require me sitting down and thinking it through manually.

**Cost-consciousness (an entrepreneur's angle on this):** the app uses `claude-haiku-4-5`, the cheapest and fastest Claude model, since quote generation doesn't need heavy reasoning. Each quote costs a fraction of a cent to generate — margins matter even in a training project, and I wanted the tool to be something that could realistically run at low cost in a real small business.

## Tech stack

- Django 6.1
- Anthropic Python SDK (`claude-haiku-4-5-20251001`)
- ReportLab (PDF generation)
- SQLite (dev database)
- `python-decouple` for environment variable / API key management

## Models

- **Quote** — client name, raw brief, generated quote text, status (draft/sent/accepted), timestamp
- **QuoteLineItem** — individual priced items linked to a Quote: description, category, estimated price

## Setup

```bash
git clone https://github.com/janaalturkii/offset-quotes.git
cd offset-quotes
python -m venv venv
venv\Scripts\activate      # Windows
pip install django anthropic python-decouple reportlab
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-key-here
```

Then:

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

**Note:** `.env` is git-ignored and never committed — the API key must be supplied locally.

## Possible next steps

- Let users edit/regenerate individual line items instead of the whole quote
- Track quote status changes (draft → sent → accepted) with a simple workflow
- Add a lightweight cost dashboard showing total API spend across all quotes generated
- Support multiple currencies for events outside Saudi Arabiagit commit -m "Add README documenting the Offset Events capstone project"
