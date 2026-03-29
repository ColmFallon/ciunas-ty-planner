from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
SCRIPTS_DIR = ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


fake_streamlit = types.ModuleType("streamlit")
for name in (
    "caption",
    "write",
    "markdown",
    "info",
    "warning",
    "error",
    "subheader",
    "title",
    "set_page_config",
    "radio",
    "text_area",
    "form_submit_button",
    "text_input",
    "selectbox",
    "download_button",
    "button",
    "rerun",
):
    setattr(fake_streamlit, name, lambda *args, **kwargs: None)
fake_streamlit.session_state = {}
sys.modules.setdefault("streamlit", fake_streamlit)


from answer_query import normalise_template_context, requested_output_language, answer_question  # noqa: E402
import streamlit_app  # noqa: E402


def build_prompt(
    *,
    school_name: str,
    cohort_size: str,
    school_type: str,
    school_ethos: str,
    priorities: str,
    existing_modules: str,
    work_experience: str,
    additional_context: str,
    language: str,
) -> str:
    return (
        "Create a Transition Year annual plan.\n\n"
        "Use the following context:\n"
        f"School name: {school_name}\n"
        f"Cohort size: {cohort_size}\n"
        f"School type: {school_type}\n"
        f"School ethos: {school_ethos}\n"
        f"Main priorities: {priorities}\n"
        f"Existing modules: {existing_modules}\n"
        f"Work experience timing: {work_experience}\n"
        f"Additional context: {additional_context}\n"
        f"Language: {language}\n\n"
        "Generate a full structured TY annual plan."
    )


class PlannerHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prompt_en_gaelscoil = build_prompt(
            school_name="mary's college",
            cohort_size="68 students",
            school_type="gaelcholaiste, deis school",
            school_ethos="catholic",
            priorities="wellbeing and attendance",
            existing_modules="leadership, enterprise",
            work_experience="1 day per week",
            additional_context="small rural school with strong community links",
            language="ENGLISH",
        )
        cls.prompt_ga_english_medium = build_prompt(
            school_name="st patricks college",
            cohort_size="72 students",
            school_type="mixed secondary school",
            school_ethos="Catholic",
            priorities="wellbeing and attendance",
            existing_modules="leadership, financial literacy",
            work_experience="weekly",
            additional_context="urban setting with strong community links",
            language="Gaeilge",
        )
        cls.prompt_ga_context = build_prompt(
            school_name="st mary's college",
            cohort_size="68 students",
            school_type="gaelscoil, DEIS school",
            school_ethos="Catholic",
            priorities="wellbeing and attendance",
            existing_modules="leadership, enterprise",
            work_experience="Fridays",
            additional_context="small rural school with strong community links",
            language="Irish",
        )

        cls.result_en_gaelscoil = answer_question(cls.prompt_en_gaelscoil)
        cls.text_en_gaelscoil = str(cls.result_en_gaelscoil.get("answer", ""))
        cls.result_ga_english_medium = answer_question(cls.prompt_ga_english_medium)
        cls.text_ga_english_medium = str(cls.result_ga_english_medium.get("answer", ""))
        cls.result_ga_context = answer_question(cls.prompt_ga_context)
        cls.text_ga_context = str(cls.result_ga_context.get("answer", ""))

    def test_requested_output_language_variants(self) -> None:
        self.assertEqual(requested_output_language("ENGLISH"), "en")
        self.assertEqual(requested_output_language("english"), "en")
        self.assertEqual(requested_output_language("Irish"), "ga")
        self.assertEqual(requested_output_language("Gaeilge"), "ga")
        self.assertEqual(requested_output_language("gaelic"), "ga")

    def test_display_normalisation_variants(self) -> None:
        context = normalise_template_context(
            {
                "school_name": "mary's college",
                "school_type": "gaelcholaiste, deis school",
                "school_ethos": "catholic",
                "work_experience": "1 day per week",
                "priorities": "wellbeing and attendance",
            },
            "en",
        )
        self.assertEqual(context["school_name"], "Mary's College")
        self.assertIn("Gaelcholáiste", context["school_type"])
        self.assertIn("DEIS", context["school_type"])
        self.assertEqual(context["school_ethos"], "catholic")
        self.assertEqual(context["work_experience"], "one day a week")

    def test_display_normalisation_irish_variants(self) -> None:
        context = normalise_template_context(
            {
                "school_type": "gaelic, deis school",
                "school_ethos": "catholic",
                "work_experience": "Fridays",
                "priorities": "wellbeing and attendance",
            },
            "ga",
        )
        self.assertIn("DEIS", context["school_type"])
        self.assertIn("lán-Ghaeilge", context["school_type"])
        self.assertEqual(context["school_ethos"], "Caitliceach")
        self.assertEqual(context["work_experience"], "Dé hAoine")
        self.assertIn("folláine", context["priorities"])

    def test_english_output_with_gaelscoil_context_stays_english(self) -> None:
        self.assertIn("Programme Overview", self.text_en_gaelscoil)
        self.assertNotIn("Forbhreathnú ar an gClár", self.text_en_gaelscoil)
        self.assertIn("Mary's College", self.text_en_gaelscoil)
        self.assertIn("gaelscoil or gaelcholáiste context", self.text_en_gaelscoil)

    def test_irish_output_with_english_medium_context_stays_irish(self) -> None:
        self.assertIn("Forbhreathnú ar an gClár", self.text_ga_english_medium)
        self.assertNotIn("Programme Overview", self.text_ga_english_medium)
        self.assertIn("gach seachtain", self.text_ga_english_medium)

    def test_deis_rural_catholic_context_is_reflected(self) -> None:
        self.assertIn("DEIS", self.text_ga_context)
        self.assertIn("folláine", self.text_ga_context)
        self.assertIn("pobail", self.text_ga_context)
        self.assertIn("Caitliceach", self.text_ga_context)

    def test_preview_sections_english(self) -> None:
        _title, _subtitle, preview_text, matched_names = streamlit_app.extract_preview_payload(self.text_en_gaelscoil)
        self.assertEqual(matched_names, ["Programme Overview", "Rationale", "Aims"])
        self.assertIn("#### Programme Overview", preview_text)
        self.assertIn("#### Rationale", preview_text)
        self.assertIn("#### Aims", preview_text)
        self.assertIn("This annual TY plan sets out the structure", preview_text)

    def test_preview_sections_irish(self) -> None:
        _title, _subtitle, preview_text, matched_names = streamlit_app.extract_preview_payload(self.text_ga_context)
        self.assertEqual(matched_names, ["Forbhreathnú ar an gClár", "Réasúnaíocht", "Aidhmeanna"])
        self.assertIn("#### Forbhreathnú ar an gClár", preview_text)
        self.assertIn("#### Réasúnaíocht", preview_text)
        self.assertIn("#### Aidhmeanna", preview_text)
        self.assertIn("Tá an leagan seo den phlean", preview_text)

    def test_docx_generation_is_structurally_valid(self) -> None:
        docx_bytes = streamlit_app.build_docx_bytes(
            self.text_en_gaelscoil,
            context=streamlit_app.parse_template_context(self.prompt_en_gaelscoil),
        )
        self.assertEqual(docx_bytes[:2], b"PK")
        self.assertGreater(len(docx_bytes), 1000)

    def test_pdf_generation_is_valid(self) -> None:
        pdf_bytes = streamlit_app.build_pdf_bytes(
            self.text_ga_context,
            "Plean Bliantúil na hIdirbhliana",
            context=streamlit_app.parse_template_context(self.prompt_ga_context),
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", pdf_bytes[-2048:])
        self.assertGreater(len(pdf_bytes), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
