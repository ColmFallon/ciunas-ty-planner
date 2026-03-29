# TY Planner Tool

This folder contains the current self-contained copy of the Ciunas TY Planning Tool for website-side running, embedding, or separate deployment. The TY AI Assistant repository remains the source of truth for active development.

## Runtime structure

- `app/streamlit_app.py`
- `scripts/answer_query.py`
- `data/vectorstore/index.json`
- `outputs/generated_plans/`
- `outputs/leads/`

## Python dependencies

Install from `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Required environment variables

- `OPENAI_API_KEY`
- optional `OPENAI_MODEL`
- optional `MAILCHIMP_API_KEY`
- optional `MAILCHIMP_AUDIENCE_ID`

If OpenAI is unavailable, the app falls back to the local generator.
If Mailchimp secrets are present, planner lead submissions are also synced to Mailchimp and tagged as `TY Planner Lead`. Local CSV lead backup remains in place either way.

## Running locally

```bash
source .venv/bin/activate
python -m streamlit run app/streamlit_app.py
```

## Running the hardening checks

Run the local planner test pass before pushing changes:

```bash
source .venv/bin/activate
python -m unittest discover -s tools/ty-planner/tests -v
```

This test pass covers:

- output-language selection across English and Irish variants
- school-name and structured-input normalisation
- preview slicing for English and Irish plans
- DOCX structural generation
- PDF generation and validity checks
- common context combinations such as DEIS, rural context, Catholic ethos, and work-experience timing variants

## Outputs

- generated plans are written to `outputs/generated_plans/`
- email leads are written to `outputs/leads/ty_planner_leads.csv`

## Notes

- This app is intended to be embedded on the TY planner landing page, typically via iframe.
- Email capture remains inside the Streamlit app.
- Downloads remain inside the Streamlit app.
- PDF export uses the system `lualatex` command when available, with a basic fallback if LaTeX is unavailable.
