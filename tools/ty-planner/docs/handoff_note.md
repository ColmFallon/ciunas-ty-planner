# TY Planner Handoff Note

## Source repo

- `/Users/Colm/Library/CloudStorage/GoogleDrive-colm@projectonesky.com/My Drive/Ciunas/TY AI Assistant`

## Files copied

- `app/streamlit_app.py`
- `scripts/answer_query.py`
- `data/vectorstore/index.json`

## Dependency map

- Python files needed: `app/streamlit_app.py`, `scripts/answer_query.py`
- Data file needed: `data/vectorstore/index.json`
- Output folders used: `outputs/generated_plans/`, `outputs/leads/`
- Environment variables: `OPENAI_API_KEY`, optional `OPENAI_MODEL`
- Third-party packages: `streamlit`, `openai`, `python-docx`, `lxml`
- External system dependency for styled PDF: `lualatex` when available

## Path handling

The copied tool keeps the same relative app and script structure as the source repo, so the existing root-relative path logic now resolves inside `/tools/ty-planner/` rather than back to the source repository.

## Environment variables

- `OPENAI_API_KEY`
- optional `OPENAI_MODEL`

## Remaining deployment steps

1. Create a local venv inside `/tools/ty-planner/`.
2. Install `requirements.txt`.
3. Make sure `lualatex` is available on the host if the styled PDF path is required.
4. Run the Streamlit app locally or deploy it separately and embed it from its served URL.
