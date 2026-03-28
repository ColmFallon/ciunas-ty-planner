# TY Planner Website Module

This folder contains the lightweight website module for the Ciunas TY Planning Tool.

Contents:

- `template.php`
  WordPress-ready landing page structure for the TY planner page.
- `ty-planner.css`
  Minimal page-level styling that should sit alongside the existing Ciunas site styles.

Expected embed flow:

1. The Streamlit app is loaded in an iframe with `?embed_mode=1`.
2. All plan generation, tailoring, email capture, and downloads remain inside the Streamlit app.
3. The website only provides the surrounding landing page copy, layout, and embed container.

This module is intentionally lightweight. It does not duplicate app logic or interfere with the Streamlit interface.
