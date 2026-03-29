#!/usr/bin/env python3
"""Assemble a grounded local TY planning answer from retrieved chunks."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "vectorstore" / "index.json"

OFFICIAL_KEYWORDS = {
    "purpose",
    "policy",
    "expectation",
    "expectations",
    "inclusive",
    "inclusion",
    "support",
    "supports",
    "planning",
    "plan",
    "achieve",
    "achievement",
    "voice",
}
FRAMEWORK_KEYWORDS = {
    "idea",
    "ideas",
    "module",
    "modules",
    "theme",
    "themes",
    "structure",
    "design",
    "module",
    "wellbeing",
    "resilience",
    "growth",
    "mindset",
}

DEFAULT_OPENAI_MODEL = "gpt-5.4"


EN_TEMPLATE_SECTIONS = [
    (
        "Programme Overview",
        "This annual TY plan sets out the structure, purpose, and organisation of the school's Transition Year programme for September 2026 to May 2027. It is intended to act as a working planning document for school leadership, the TY coordinator, and the wider TY teaching team. It should be adapted in line with the ethos, context, and priorities of the school so that the final version reflects the students, staffing, and opportunities available locally.",
    ),
    (
        "Rationale",
        "The school provides TY as a broad educational year that supports maturity, independence, reflection, and readiness for senior cycle and life beyond school. The programme is intended to give students a distinct year of growth, variety, and preparation rather than a reduced version of exam-focused provision. In practice, this means creating space for students to try new roles, take part in projects, and develop responsibility in ways that are not always possible in an examination year.",
    ),
    (
        "Aims",
        "The programme aims to support personal growth, strengthen learning habits, widen student experience, and help students make more informed choices about senior cycle and future pathways. It also aims to balance academic continuity with active learning, reflection, and broader participation in school and community life. A strong TY plan should help students grow in confidence, communication, organisation, and self-awareness across the year.",
    ),
    (
        "Programme Structure",
        "The programme is organised as a balanced mix of core subjects, subject sampling, TY-specific modules, experiential learning, and reflective work. A weekly structure should include room for academic continuity, pastoral support, portfolio work, and practical experiences that give the year a clear identity. Planning should also take account of staffing, time, and available financial resources so that the programme remains realistic and sustainable across the full year. In many schools, subject sampling is concentrated early in the year and then supported by rotation blocks of roughly six to eight weeks so that students experience variety without losing continuity.",
    ),
    (
        "Key Strands",
        "The main strands of the programme are personal development, active learning, community and citizenship, creativity, and future pathways. These strands should run across the year so that modules and activities feel connected rather than isolated. For example, student leadership, work experience, and portfolio reflection should all support the same broader TY aims rather than operating as separate add-ons.",
    ),
    (
        "Year Structure",
        "Term 1 should focus on induction, relationship building, subject sampling, and early reflection. Term 2 should deepen student engagement through sustained modules, practical experiences, and mid-year review. Term 3 should consolidate the year through portfolio completion, final reflection, celebration of learning, and preparation for the move into senior cycle. This progression should help students move from orientation and participation towards greater independence and ownership of their learning.",
    ),
    (
        "Core Modules",
        "Core modules should combine academic continuity with TY-specific learning. Schools may include modules such as Wellbeing and Personal Development, Enterprise or Mini-Company, Leadership, Financial Literacy, RSA or road-safety education, Language Tasters, Practical Life Skills, and Careers and Future Pathways, alongside subject sampling where appropriate. In practice, this might include a short enterprise cycle with a mini-company pitch, a practical budgeting task, a road-safety workshop, or a language-and-culture taster linked to school events. The final selection should reflect the school context, staffing, student needs, and available resources rather than trying to include too many strands at once. Any associated costs, budget allocation across modules and activities, and accessibility for all students should be considered at planning stage. Time allocation should be noted clearly for each module, including weekly hours, duration, or block timing.",
    ),
    (
        "Teaching and Learning Approach",
        "Teaching and learning should emphasise active participation, collaboration, reflection, creativity, and practical application. The programme should use a varied mix of discussion, project work, presentations, workshops, and learning beyond the classroom so that students experience TY as an active and developmental year. Short project deadlines, review points, and presentation opportunities can help students to stay engaged and to see progress across the year.",
    ),
    (
        "Student Voice",
        "Student voice should be built into the programme through consultation, reflection, feedback, and choice. Students should have meaningful opportunities to shape aspects of themes, projects, activities, and review across the year. This may include student surveys, TY committees, feedback after key events, or choices within modules and project themes, such as helping to select a guest speaker theme or proposing an end-of-term showcase idea.",
    ),
    (
        "Wellbeing",
        "Wellbeing should be visible across planned modules, pastoral supports, reflective routines, and positive school experiences. The programme should support confidence, relationships, belonging, resilience, and healthy habits in a structured way rather than through occasional one-off events only. A weekly wellbeing slot, tutor check-in, or regular reflective journal routine can help this strand to remain visible and consistent, particularly when linked to simple routines such as goal-setting or short reflection after major activities.",
    ),
    (
        "Experiential Learning",
        "Experiential learning should include work experience, community engagement, trips, guest speakers, projects, and practical tasks linked to the wider aims of TY. This could include a local employer visit, a community clean-up project, or a skills workshop with an outside facilitator, depending on the school context. Students should be prepared for these experiences in advance and supported to reflect on what they learned afterwards. Trips, activities, and any external providers should align with budget, access, and inclusion considerations so that participation remains realistic for the full TY group. Where possible, these experiences should be linked back into portfolio work, careers reflection, or presentation tasks so that the learning is captured clearly.",
    ),
    (
        "Inclusion",
        "The programme should be planned so that all students can participate meaningfully and experience success. Activities, modules, trips, and placements should be reviewed with access, flexibility, support, and reasonable adjustment in mind. This includes practical consideration of cost, confidence, literacy demands, organisation, and the level of support students may need in unfamiliar settings.",
    ),
    (
        "Assessment",
        "Assessment should reflect the nature of TY and use a suitable range of approaches such as project work, presentations, reflection, participation, practical tasks, teacher feedback, and review. Progress should be recognised in a way that matches the aims of the programme and gives students clear feedback. Simple common expectations across modules can help students and parents to understand how progress is being recognised during the year.",
    ),
    (
        "Portfolio",
        "The TY portfolio should capture student learning, reflection, evidence, and progress across the year. Portfolio work should be timetabled regularly and supported through clear expectations, structured reflection, and teacher review. In practice, it is often most manageable when students update the portfolio at set review points rather than leaving it until the end of term.",
    ),
    (
        "Parent Communication",
        "Parents and guardians should receive clear information before and during the year about the aims, structure, expectations, placements, events, and review points within the programme. Communication should be planned rather than reactive and should support confidence in the value of TY. A parent information evening, a written overview, and short updates at key points in the year can make this communication more consistent.",
    ),
    (
        "Review",
        "The annual plan should be reviewed during and after the year so that the programme can improve over time. Review should draw on student feedback, staff reflection, attendance patterns, module outcomes, and the quality of portfolio and experiential learning evidence. A short mid-year review and a more formal end-of-year review can help the school make realistic adjustments for the following cycle.",
    ),
    (
        "Summary Calendar",
        "September\nSeptember 2026 should be used for induction, programme launch, student voice, portfolio setup, and the start of any early subject-sampling rotation so that students begin the year with clear expectations.\nOctober-December\nOctober to December 2026 should focus on establishing core modules, six- to eight-week rotation blocks, early practical activities, and the first review point while routines are still being built.\nJanuary-March\nJanuary to March 2027 should carry the main weight of sustained modules, work experience or community activity, and mid-year review so that the year has a clear centre of gravity.\nApril-May\nApril to May 2027 should focus on consolidation, portfolio completion, final reflection, reporting, and celebration of learning so that the transition into Senior Cycle is purposeful rather than rushed.",
    ),
]


GA_TEMPLATE_SECTIONS = [
    (
        "Forbhreathnú ar an gClár",
        "Leagann an plean bliantúil seo amach struchtúr, cuspóir, agus eagrúchán chlár Idirbhliana na scoile do Mheán Fómhair 2026 go Bealtaine 2027. Tá sé i gceist go bhfeidhmeodh sé mar dhoiciméad oibre do cheannaireacht na scoile, do chomhordaitheoir na hIdirbhliana, agus d'fhoireann teagaisc chlár na hIdirbhliana. Ba chóir an leagan deiridh a oiriúnú d'éiteas, do chomhthéacs, agus do thosaíochtaí na scoile ionas go mbeidh sé ag teacht leis an bhfíorchur chuige áitiúil.",
    ),
    (
        "Réasúnaíocht",
        "Cuireann an scoil an Idirbhliain ar fáil mar bhliain leathan oideachais a chothaíonn aibíocht, neamhspleáchas, machnamh, agus ullmhacht don tsraith shinsearach agus don saol lasmuigh den scoil. Tá sé i gceist go dtabharfadh an clár bliain shainiúil fáis, éagsúlachta, agus ullmhúcháin do scoláirí seachas leagan laghdaithe de sholáthar atá dírithe ar scrúduithe. Go praiticiúil, ciallaíonn sé seo spás a chruthú do róil nua, do thionscadail, agus do fhreagracht nach mbíonn chomh feiceálach i mbliain scrúdaithe.",
    ),
    (
        "Aidhmeanna",
        "Tá sé mar aidhm ag an gclár tacú le fás pearsanta, nósanna foghlama a neartú, taithí na scoláirí a leathnú, agus cabhrú leo roghanna níos eolaí a dhéanamh faoin tsraith shinsearach agus faoi bhealaí amach anseo. Tá sé mar aidhm aige freisin cothromaíocht a chruthú idir leanúnachas acadúil, foghlaim ghníomhach, machnamh, agus rannpháirtíocht níos leithne i saol na scoile agus an phobail. Ba chóir go gcuideodh an clár le scoláirí fás i muinín, cumarsáid, eagrúchán, agus féin-eolas i rith na bliana.",
    ),
    (
        "Struchtúr an Chláir",
        "Tá an clár eagraithe mar mheascán cothrom de chroí-ábhair, blaiseadh ábhar, modúil shonracha don Idirbhliain, foghlaim ó thaithí, agus obair mhachnamhach. Ba chóir go mbeadh spás sa struchtúr seachtainiúil do leanúnachas acadúil, do thacaíocht thréadach, d'obair phunainne, agus d'eispéiris phraiticiúla a thugann féiniúlacht shoiléir don bhliain. Ba chóir don phleanáil acmhainní foirne, am, agus acmhainní airgeadais atá ar fáil a chur san áireamh freisin ionas go mbeidh an clár indéanta i gcaitheamh na bliana. I go leor scoileanna, cabhraíonn blaiseadh ábhar go luath sa bhliain agus bloic rothlacha idir sé agus ocht seachtaine le cothromaíocht mhaith a chruthú idir éagsúlacht agus leanúnachas.",
    ),
    (
        "Príomhshnáitheanna",
        "Is iad príomhshnáitheanna an chláir forbairt phearsanta, foghlaim ghníomhach, pobal agus saoránacht, cruthaitheacht, agus bealaí amach anseo. Ba chóir go rithfeadh na snáitheanna seo tríd an mbliain ionas go mbraithfidh modúil agus gníomhaíochtaí mar chuid de chlár comhleanúnach. Mar shampla, ba chóir go dtacódh guth an scoláire, taithí oibre, agus obair phunainne leis na haidhmeanna céanna ar fud na bliana.",
    ),
    (
        "Struchtúr na Bliana",
        "Ba chóir do Théarma 1 díriú ar ionduchtú, tógáil caidrimh, blaiseadh ábhar, agus machnamh luath. Ba chóir do Théarma 2 rannpháirtíocht na mac léinn a dhoimhniú trí mhodúil leanúnacha, foghlaim ó thaithí, agus athbhreithniú lárbhliana. Ba chóir do Théarma 3 an bhliain a thabhairt le chéile trí chríochnú na punainne, machnamh deiridh, ceiliúradh foghlama, agus ullmhú don aistriú go dtí an tsraith shinsearach. Ba chóir go gcuideodh an dul chun cinn seo le scoláirí bogadh ó threoshuíomh agus rannpháirtíocht go dtí níos mó neamhspleáchais agus úinéireachta ar a gcuid foghlama.",
    ),
    (
        "Croí-Mhodúil",
        "Ba chóir do na croí-mhodúil leanúnachas acadúil a chothromú le foghlaim shonrach don Idirbhliain. D'fhéadfadh modúil ar nós Folláine agus Forbairt Phearsanta, Fiontraíocht nó Mini-Company, Ceannaireacht, Litearthacht Airgeadais, RSA nó sábháilteacht ar bhóithre, blaiseadh teangacha, scileanna praiticiúla saoil, agus Gairmeacha agus Bealaí Amach Anseo a bheith san áireamh, chomh maith le blaiseadh ábhar nuair is cuí. Go praiticiúil, d'fhéadfadh sé seo a bheith le feiceáil i dtionscadal gairid fiontraíochta, i dtasc buiséadaithe, i gceardlann sábháilteachta bóthair, nó i mblas teanga agus cultúir bunaithe ar imeacht scoile. Ba chóir go léireodh an rogha deiridh comhthéacs na scoile, an fhoireann, riachtanais na scoláirí, agus na hacmhainní atá ar fáil seachas iarracht a dhéanamh an iomarca a chur isteach sa chlár. Ba chóir costais a bhaineann le modúil, leithdháileadh an bhuiséid ar ghníomhaíochtaí, agus inrochtaineacht do gach scoláire a mheas ag céim na pleanála. Ba chóir leithdháileadh ama gach modúil a bheith soiléir, lena n-áirítear uaireanta seachtainiúla, fad, nó bloc-am.",
    ),
    (
        "Cur Chuige Teagaisc agus Foghlama",
        "Ba chóir do theagasc agus d'fhoghlaim béim a leagan ar rannpháirtíocht ghníomhach, comhoibriú, machnamh, cruthaitheacht, agus cur i bhfeidhm sa bhfíorshaol. Ba chóir meascán d'obair thionscadail, plé, cur i láthair, ceardlanna, agus foghlaim lasmuigh den seomra ranga a úsáid ionas go mbraithfidh scoláirí an Idirbhliain mar bhliain ghníomhach agus fhorbartha. Is féidir le spriocdhátaí gearra, pointí athbhreithnithe, agus deiseanna cur i láthair cabhrú le rannpháirtíocht agus dul chun cinn a choinneáil soiléir.",
    ),
    (
        "Guth na Mac Léinn",
        "Ba chóir guth na mac léinn a bheith fite isteach sa chlár trí chomhairliúchán, machnamh, aiseolas, agus rogha. Ba chóir deiseanna fiúntacha a bheith ag scoláirí gnéithe de théamaí, de thionscadail, de ghníomhaíochtaí, agus den athbhreithniú a mhúnlú. D'fhéadfadh sé seo a bheith le feiceáil trí shuirbhéanna gearra, coistí TY, aiseolas i ndiaidh imeachtaí, nó rogha laistigh de mhodúil agus de théamaí tionscadail, mar shampla roghnú téama aoichainteora nó smaoineamh do thaispeántas ag deireadh téarma.",
    ),
    (
        "Folláine",
        "Ba chóir go mbeadh folláine le feiceáil i modúil phleanáilte, i dtacaíochtaí tréadacha, i ngnáthaimh mhachnamhacha, agus in eispéiris dhearfacha scoile. Ba chóir go dtacódh an clár le muinín, le caidrimh, le muintearas, le teacht aniar, agus le nósanna folláine ar bhealach struchtúrtha seachas trí imeachtaí aonuaire amháin. Is féidir le sliotán seachtainiúil folláine, seiceáil isteach le teagascóir, nó gnáthamh machnaimh cuidiú leis an snáithe seo fanacht le feiceáil go rialta, go háirithe nuair a nascann sé le socrú spriocanna simplí nó le machnamh gairid i ndiaidh mórghníomhaíochtaí.",
    ),
    (
        "Foghlaim ó thaithí",
        "Ba chóir go n-áireofaí sa fhoghlaim ó thaithí taithí oibre, rannpháirtíocht phobail, turais, aoichainteoirí, tionscadail, agus tascanna praiticiúla a bhaineann le haidhmeanna níos leithne na hIdirbhliana. D'fhéadfadh cuairt ar fhostóir áitiúil, tionscadal pobail, nó ceardlann scileanna le héascaitheoir seachtrach a bheith oiriúnach, ag brath ar chomhthéacs na scoile. Ba chóir scoláirí a ullmhú do na heispéiris seo roimh ré agus tacú leo machnamh a dhéanamh ar a bhfoghlaim ina ndiaidh. Ba chóir turais, gníomhaíochtaí, agus soláthraithe seachtracha a phleanáil ar bhealach a thagann le cúrsaí buiséid, rochtana, agus cuimsithe ionas go mbeidh siad réadúil don ghrúpa ar fad. Nuair is féidir, ba chóir na heispéiris seo a nascadh le hobair phunainne, machnamh gairme, nó cur i láthair ionas go mbeidh an fhoghlaim le feiceáil go soiléir.",
    ),
    (
        "Cuimsiú",
        "Ba chóir an clár a phleanáil ionas gur féidir le gach scoláire páirt bhríoch a ghlacadh ann agus rath a bhaint amach. Ba chóir gníomhaíochtaí, modúil, turais, agus socrúcháin a athbhreithniú agus rochtain, solúbthacht, tacaíocht, agus coigeartuithe réasúnta san áireamh. Áirítear leis seo smaoineamh go praiticiúil ar chostas, ar mhuinín, ar éilimh litearthachta, ar eagrúchán, agus ar an tacaíocht a d'fhéadfadh a bheith ag teastáil i suíomhanna nua.",
    ),
    (
        "Measúnú",
        "Ba chóir don mheasúnú teacht le nádúr na hIdirbhliana agus réimse cur chuige a úsáid, mar shampla obair thionscadail, cur i láthair, machnamh, rannpháirtíocht, tascanna praiticiúla, aiseolas ó mhúinteoirí, agus athbhreithniú. Ba chóir dul chun cinn a aithint ar bhealach a thagann le haidhmeanna an chláir agus a thugann aiseolas soiléir do scoláirí. Is féidir le hionchais choitianta simplí ar fud modúl cuidiú le scoláirí agus le tuismitheoirí tuiscint níos fearr a fháil ar an dul chun cinn i rith na bliana.",
    ),
    (
        "Punann",
        "Ba chóir go ngabhfadh punann na hIdirbhliana foghlaim, machnamh, fianaise, agus dul chun cinn an scoláire i rith na bliana. Ba chóir obair na punainne a bheith ar an gclár ama go rialta agus í a thacú le hionchais shoiléire, le machnamh struchtúrtha, agus le hathbhreithniú múinteora. Go praiticiúil, bíonn sé níos soláimhsithe de ghnáth nuair a dhéanann scoláirí nuashonrú ar an bpunann ag pointí athbhreithnithe seasta seachas gach rud a fhágáil go dtí deireadh téarma.",
    ),
    (
        "Cumarsáid le Tuismitheoirí",
        "Ba chóir go bhfaigheadh tuismitheoirí agus caomhnóirí eolas soiléir roimh an mbliain agus lena linn faoi aidhmeanna, struchtúr, ionchais, socrúcháin, imeachtaí, agus pointí athbhreithnithe an chláir. Ba chóir an chumarsáid a phleanáil roimh ré ionas go gcothaítear muinín i luach na hIdirbhliana. Is féidir le hoíche eolais do thuismitheoirí, achoimre scríofa, agus nuashonruithe gearra ag pointí tábhachtacha den bhliain an chumarsáid seo a dhéanamh níos comhsheasmhaí.",
    ),
    (
        "Athbhreithniú",
        "Ba chóir an plean bliantúil a athbhreithniú i rith na bliana agus ina diaidh ionas gur féidir an clár a fheabhsú le himeacht ama. Ba chóir don athbhreithniú tarraingt ar aiseolas scoláirí, ar mhachnamh foirne, ar phatrúin tinrimh, ar thorthaí modúl, agus ar cháilíocht na punainne agus na foghlama ó thaithí. Is féidir le hathbhreithniú gearr lárbhliana agus athbhreithniú níos foirmiúla ag deireadh na bliana cuidiú leis an scoil athruithe réalaíocha a phleanáil don chéad timthriall eile.",
    ),
    (
        "Féilire Achomair",
        "Meán Fómhair\nBa chóir Meán Fómhair 2026 a úsáid le haghaidh ionduchtaithe, tús an chláir, guth an scoláire, socrú na punainne, agus tús aon bhloc luath de bhlaiseadh ábhar ionas go mbeidh ionchais shoiléire ann ón tús.\nDeireadh Fómhair-Nollaig\nBa chóir Deireadh Fómhair go Nollaig 2026 díriú ar na croí-mhodúil, ar bhlocanna rothlacha idir sé agus ocht seachtaine, ar ghníomhaíochtaí praiticiúla luatha, agus ar an gcéad phointe athbhreithnithe agus gnáthaimh na bliana fós á mbunú.\nEanáir-Márta\nBa chóir Eanáir go Márta 2027 an phríomhualach a thabhairt do mhodúil leanúnacha, do thaithí oibre nó d'obair phobail, agus d'athbhreithniú lárbhliana ionas go mbeidh croílár soiléir ag an mbliain.\nAibreán-Bealtaine\nBa chóir Aibreán go Bealtaine 2027 díriú ar chomhdhlúthú, ar chríochnú na punainne, ar mhachnamh deiridh, ar thuairisciú, agus ar cheiliúradh foghlama ionas go mbeidh an t-aistriú go dtí an tsraith shinsearach réidh agus fóinteach.",
    ),
]


def detect_template_language(question: str) -> str:
    lowered = question.lower()
    if any(
        term in lowered
        for term in (
            "irish",
            "gaeilge",
            "as gaeilge",
            "i ngaeilge",
            "cruthaigh",
            "plean idirbhliana",
            "idirbhliana",
        )
    ):
        return "ga"
    return "en"


def is_template_generation_request(question: str) -> bool:
    lowered = question.lower()
    has_action = any(term in lowered for term in ("create", "generate", "cruthaigh"))
    has_plan = any(
        term in lowered
        for term in ("annual plan", "ty plan", "transition year plan", "plean idirbhliana", "plean bliantuil")
    )
    if has_action and "plan" in lowered:
        return True
    if has_action and "plean" in lowered:
        return True
    return has_plan


def infer_school_context(question: str, language: str) -> str:
    context = parse_template_context(question)
    school_name = tidy_context_phrase(context.get("school_name", ""))
    cohort_size = tidy_context_phrase(context.get("cohort_size", ""))
    school_type = tidy_context_phrase(context.get("school_type", ""))
    school_ethos = tidy_context_phrase(context.get("school_ethos", ""))
    priorities = tidy_context_phrase(context.get("priorities", ""))
    existing_modules = tidy_context_phrase(context.get("existing_modules", ""))
    work_experience = tidy_context_phrase(context.get("work_experience", ""))
    additional_context = tidy_context_phrase(context.get("additional_context", ""))
    ethos_context = ", ".join(part for part in (school_ethos, additional_context) if part)
    has_ethos = context_mentions_ethos(ethos_context)

    if any((school_name, cohort_size, school_type, school_ethos, priorities, existing_modules, work_experience, additional_context)):
        if language == "ga":
            opening = "Tá an plean bliantúil seo ceaptha mar bhunús oibre"
            if school_name and school_type:
                opening += f" do {school_name}, {school_type}"
            elif school_name:
                opening += f" do {school_name}"
            elif school_type:
                opening += f" do scoil sa chomhthéacs seo mar {school_type}"
            opening += "."

            parts = [opening]
            if cohort_size:
                parts.append(f"Ba chóir méid an chohóirt, {cohort_size}, a chur san áireamh agus modúil, maoirseacht, agus taithí oibre á bpleanáil.")
            if school_ethos and not has_ethos:
                parts.append(f"Ba chóir ton agus béim an phlean a ailíniú le carachtar na scoile seo mar {school_ethos}.")
            if priorities:
                parts.append(f"Ba chóir go léireodh sé fócas na scoile ar {priorities}.")
            if existing_modules:
                parts.append(f"Is féidir leanúint le gnéithe atá ann cheana, amhail {existing_modules}, nuair a thacaíonn siad leis na haidhmeanna bliantúla.")
            if work_experience:
                parts.append(f"Ba chóir socrú na taithí oibre a ailíniú le {work_experience}.")
            if additional_context and not has_ethos:
                parts.append(f"Ba chóir sonraí áitiúla ar nós {additional_context} a chur san áireamh nuair is cuí.")
            return " ".join(parts)

        opening = "This annual plan is designed as a working starting point"
        if school_name and school_type:
            opening += f" for {school_name}, a {school_type}"
        elif school_name:
            opening += f" for {school_name}"
        elif school_type:
            opening += f" for a school context such as {school_type}"
        opening += "."

        parts = [opening]
        if cohort_size:
            parts.append(f"The cohort context of {cohort_size} should be taken into account when planning grouping, supervision, and the scale of activities.")
        if school_ethos and not has_ethos:
            parts.append(f"The tone and emphasis of the plan should also align with the school's character as {school_ethos}.")
        if priorities:
            parts.append(f"It should reflect the school's emphasis on {priorities}.")
        if existing_modules:
            parts.append(f"Existing provision such as {existing_modules} can continue where it supports the overall direction of the programme.")
        if work_experience:
            parts.append(f"Work experience should be aligned with {work_experience}.")
        if additional_context and not has_ethos:
            parts.append(f"Local details such as {additional_context} should also shape the school version where relevant.")
        return " ".join(parts)

    if language == "ga":
        return "Tá an plean bliantúil seo ceaptha mar bhunús oibre do chlár Idirbhliana atá soiléir, praiticiúil, agus in-oiriúnaithe do chomhthéacs na scoile."
    return "This annual plan is designed as a practical working draft for a clear, usable, and adaptable Transition Year programme."


def parse_template_context(question: str) -> dict[str, str]:
    patterns = {
        "school_name": r"(?:School name|Ainm na scoile):\s*(.+)",
        "cohort_size": r"(?:Cohort size|Approximate TY cohort size|Méid an chohóirt):\s*(.+)",
        "ty_coordinator": r"(?:TY Coordinator|Comhordaitheoir TY):\s*(.+)",
        "school_type": r"(?:School type|Cineál scoile):\s*(.+)",
        "school_ethos": r"(?:School ethos|School ethos or character|Éiteas na scoile):\s*(.+)",
        "priorities": r"(?:Main priorities|Príomhthosaíochtaí):\s*(.+)",
        "existing_modules": r"(?:Existing modules|Modúil atá ann cheana):\s*(.+)",
        "work_experience": r"(?:Work experience timing|Amchlár na taithí oibre):\s*(.+)",
        "additional_context": r"(?:Additional context|Comhthéacs breise):\s*(.+)",
        "language": r"(?:Language|Teanga):\s*(.+)",
    }
    context: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            value = match.group(1).splitlines()[0].strip()
            if value.lower() != "not specified":
                context[key] = value
    return context


def context_mentions_ethos(additional_context: str) -> bool:
    lowered = additional_context.lower()
    ethos_terms = (
        "catholic",
        "faith",
        "christian",
        "religious",
        "gospel",
        "parish",
        "ethos",
        "caitliceach",
        "creideamh",
        "críostaí",
        "criostai",
        "spioradálta",
        "spioradalta",
        "eitos",
    )
    return any(term in lowered for term in ethos_terms)


def tidy_context_phrase(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip().strip(" ."))
    return cleaned


def detect_context_signals(context: dict[str, str]) -> set[str]:
    combined = " ".join(
        tidy_context_phrase(context.get(key, ""))
        for key in ("school_type", "school_ethos", "priorities", "existing_modules", "additional_context")
    ).lower()

    signal_terms = {
        "rural": ("rural", "small rural", "tuaithe", "thuaithe", "rural school"),
        "urban": ("urban", "city", "large urban", "uirbeach", "cathrach"),
        "small_school": ("small school", "small rural", "beag", "small", "scoil bheag"),
        "large_school": ("large school", "large urban", "mór", "mor", "large", "scoil mhór", "scoil mhor"),
        "community_links": (
            "community links",
            "community partnership",
            "parish links",
            "local community",
            "community-based",
            "pobal",
            "phobal",
            "phobail",
            "paróiste",
            "paroiste",
        ),
        "deis": ("deis",),
        "gaelscoil": ("gaelscoil", "gaelcholáiste", "gaelcholaiste", "irish-medium", "gaeilge"),
        "catholic_ethos": ("catholic", "faith", "christian", "religious", "gospel", "parish", "caitliceach", "creideamh"),
        "inclusion_context": ("additional needs", "sen", "inclusion", "attendance", "engagement", "cuimsiú", "cuimsiu", "riachtanais"),
        "gaisce": ("gaisce",),
        "musical": ("musical", "drama production", "show", "ceoldráma", "ceoldrama", "ceol", "léiriú ceoil", "leiriu ceoil"),
        "sport": ("sport", "sports", "gaa", "rugby", "soccer", "camogie", "athletics", "spórt", "spoirt", "spóirt", "sporting"),
    }

    signals: set[str] = set()
    for signal, terms in signal_terms.items():
        if any(term in combined for term in terms):
            signals.add(signal)
    return signals


def build_context_plan(context: dict[str, str], language: str) -> dict[str, list[str]]:
    school_name = tidy_context_phrase(context.get("school_name", ""))
    cohort_size = tidy_context_phrase(context.get("cohort_size", ""))
    priorities = tidy_context_phrase(context.get("priorities", ""))
    school_ethos = tidy_context_phrase(context.get("school_ethos", ""))
    existing_modules = tidy_context_phrase(context.get("existing_modules", ""))
    work_experience = tidy_context_phrase(context.get("work_experience", ""))
    school_type = tidy_context_phrase(context.get("school_type", ""))
    additional_context = tidy_context_phrase(context.get("additional_context", ""))
    ethos_context = ", ".join(part for part in (school_ethos, additional_context) if part)
    has_ethos = context_mentions_ethos(ethos_context)
    signals = detect_context_signals(context)

    plan: dict[str, list[str]] = {}

    def add(heading: str, sentence: str) -> None:
        if sentence:
            plan.setdefault(heading, []).append(sentence)

    if language == "ga":
        if school_name:
            add(
                "Forbhreathnú ar an gClár",
                f"Tá an leagan seo den phlean dírithe ar chomhthéacs {school_name} agus ba chóir go mbeadh sé úsáideach mar dhoiciméad oibre don fhoireann TY.",
            )
        if cohort_size:
            add(
                "Forbhreathnú ar an gClár",
                f"Ba chóir méid an chohóirt, {cohort_size}, a chur san áireamh agus scála na ngníomhaíochtaí, na ngrúpaí, agus na maoirseachta á leagan amach.",
            )
        if priorities:
            add(
                "Réasúnaíocht",
                f"Sa chomhthéacs seo, ba chóir béim faoi leith a chur ar {priorities} mar chuid de chuspóir agus de threo an chláir.",
            )
            add(
                "Aidhmeanna",
                f"Léiríonn sé seo fócas na scoile ar {priorities} agus ba chóir na haidhmeanna bliantúla a chur in ord leis sin.",
            )
        if school_type:
            add(
                "Struchtúr an Chláir",
                f"Ba chóir struchtúr an chláir a oiriúnú do réaltachtaí na scoile seo mar {school_type}.",
            )
        if school_ethos and not has_ethos:
            add(
                "Réasúnaíocht",
                f"Ba chóir ton agus béim an phlean a ailíniú le carachtar na scoile seo mar {school_ethos}.",
            )
        if existing_modules:
            add(
                "Croí-Mhodúil",
                f"Ba chóir modúil atá ann cheana, amhail {existing_modules}, a úsáid mar chuid den struchtúr bliantúil nuair a thacaíonn siad le haidhmeanna an chláir.",
            )
        if work_experience:
            add(
                "Foghlaim ó thaithí",
                f"Ba chóir taithí oibre a eagrú ar bhealach atá ag teacht leis an socrú seo: {work_experience}.",
            )
        if additional_context:
            if has_ethos:
                add(
                    "Réasúnaíocht",
                    f"Ba chóir don phlean freisin teacht le héiteas na scoile mar atá le sonrú sa chomhthéacs seo: {ethos_context}.",
                )
                add(
                    "Folláine",
                    "Sa snáithe folláine, ba chóir go mbeadh cúram, meas, machnamh, agus forbairt phearsanta le sonrú ar bhealach a thagann le héiteas na scoile.",
                )
                add(
                    "Foghlaim ó thaithí",
                    "Ba chóir deis a thabhairt do scoláirí páirt a ghlacadh i ngníomhaíochtaí pobail agus seirbhíse a léiríonn an t-éiteas sin go nádúrtha.",
                )
                add(
                    "Príomhshnáitheanna",
                    "Ba chóir go mbeadh teanga an phobail, na seirbhíse, agus an chúraim le feiceáil mar chuid de shnáithe an tsaoránachta agus an fháis phearsanta.",
                )
            else:
                add(
                    "Forbhreathnú ar an gClár",
                    f"Ba chóir sonraí áitiúla ar nós {additional_context} a léiriú sa leagan scoile den phlean nuair is cuí.",
                )
                add(
                    "Athbhreithniú",
                    "Ba chóir athbhreithniú na bliana a úsáid chun a mheas cé chomh maith agus a cuireadh na tosca áitiúla san áireamh ar fud an chláir.",
                )
        if "rural" in signals:
            add(
                "Foghlaim ó thaithí",
                "D'fhéadfadh foghlaim áitiúil, comhpháirtíochtaí pobail, tionscadail bunaithe ar an gceantar, agus blocanna socrúcháin le fostóirí áitiúla a bheith an-oiriúnach sa chomhthéacs seo.",
            )
            add(
                "Guth na Mac Léinn",
                "Is féidir guth na scoláirí a neartú freisin trí ionchur i dtionscadail áitiúla nó i ngníomhaíochtaí pobail a bhfuil tábhacht leo sa cheantar.",
            )
        if "urban" in signals:
            add(
                "Foghlaim ó thaithí",
                "D'fhéadfadh cuairteanna, comhpháirtíochtaí seachtracha, agus deiseanna a bhaineann leis an gcathair cur leis an gclár ar bhealach praiticiúil.",
            )
            add(
                "Guth na Mac Léinn",
                "Is féidir rogha agus ionchur na scoláirí a úsáid chun cuairteanna, imeachtaí, nó téamaí tionscadail a roghnú i gcomhthéacs níos uirbí.",
            )
        if "community_links" in signals:
            add(
                "Príomhshnáitheanna",
                "Ba chóir pobal agus saoránacht a bheith le feiceáil trí naisc áitiúla, rannpháirtíocht phobail, agus foghlaim a bhfuil bunús áitiúil léi.",
            )
            add(
                "Folláine",
                "Is féidir leis an snáithe folláine leas a bhaint as gníomhaíochtaí a chothaíonn muintearas agus ceangal leis an bpobal scoile agus leis an gceantar.",
            )
        if "deis" in signals or "inclusion_context" in signals:
            add(
                "Cuimsiú",
                "Sa chomhthéacs seo, ba chóir aird faoi leith a thabhairt ar inrochtaineacht, ar rannpháirtíocht, agus ar bhealaí praiticiúla chun scoláirí a choinneáil páirteach agus muiníneach.",
            )
            add(
                "Folláine",
                "Ba chóir don snáithe folláine tacú go soiléir le muintearas, tinreamh, féinmhuinín, agus gnáthaimh sheasta a chuidíonn le rannpháirtíocht leanúnach.",
            )
        if "gaelscoil" in signals:
            add(
                "Forbhreathnú ar an gClár",
                "Sa chomhthéacs seo, ba chóir go mbeadh an Ghaeilge le feiceáil go nádúrtha i dteanga an chláir, i machnamh na scoláirí, agus i gcur i láthair poiblí na foghlama.",
            )
            add(
                "Cur Chuige Teagaisc agus Foghlama",
                "Is fiú a chinntiú go dtacaíonn tascanna, plé, agus taispeántais le húsáid nádúrtha agus mhuiníneach na Gaeilge ar fud na bliana.",
            )
        module_examples: list[str] = []
        if "gaisce" in signals:
            module_examples.append("Gaisce")
        if "musical" in signals:
            module_examples.append("dramaíocht nó léiriú ceoil")
        if "sport" in signals:
            module_examples.append("ceannaireacht spóirt nó imeachtaí folláine gníomhacha")
        if module_examples:
            joined = ", ".join(module_examples)
            add(
                "Croí-Mhodúil",
                f"Sa chomhthéacs seo, d'fhéadfadh modúil nó tionscadail ar nós {joined} suí go nádúrtha taobh leis an gclár níos leithne.",
            )
        return plan

    if school_name:
        add(
            "Programme Overview",
            f"This version of the plan is written with the context of {school_name} in mind and should operate as a practical working document for the TY team.",
        )
    if cohort_size:
        add(
            "Programme Overview",
            f"The cohort context of {cohort_size} should inform the scale of grouping, supervision, portfolio support, and practical activities across the year.",
        )
    if priorities:
        add(
            "Rationale",
            f"In this context, particular emphasis should be placed on {priorities} as part of the overall purpose and direction of the programme.",
        )
        add(
            "Aims",
            f"This reflects the school's focus on {priorities}, and the annual aims should be framed accordingly.",
        )
    if school_type:
        add(
            "Programme Structure",
            f"The overall structure should be practical for a school context such as {school_type}.",
        )
    if school_ethos and not has_ethos:
        add(
            "Rationale",
            f"The overall tone of the plan should also reflect the school's character as {school_ethos}.",
        )
    if existing_modules:
        add(
            "Core Modules",
            f"Existing provision such as {existing_modules} should be retained or adapted where it supports the aims of the programme.",
        )
    if work_experience:
        add(
            "Experiential Learning",
            f"Work experience should be organised in a way that fits this pattern: {work_experience}.",
        )
    if additional_context:
        if has_ethos:
            add(
                "Rationale",
                f"The plan should also reflect the school's ethos, as seen in its {ethos_context}.",
            )
            add(
                "Wellbeing",
                "Within the wellbeing strand, this should be visible in an emphasis on care, dignity, reflection, respectful relationships, and service.",
            )
            add(
                "Experiential Learning",
                "Community and service opportunities should be chosen in ways that reflect that ethos in a practical and authentic manner.",
            )
            add(
                "Key Strands",
                "Community and citizenship should be framed in language that reflects service, care for others, and contribution to the wider school and local community.",
            )
        else:
            add(
                "Programme Overview",
                f"Local features such as {additional_context} should be reflected in the school version of the plan where they shape the year in practice.",
            )
            add(
                "Review",
                "Review points should check whether those local features have been reflected clearly enough across the programme.",
            )
    if "rural" in signals:
        add(
            "Experiential Learning",
            "Local placements, community partnerships, area-based projects, and practical visits linked to local employers or services may be especially suitable in this context.",
        )
        add(
            "Student Voice",
            "Student voice may also be strengthened through input into local projects or community-based activity that feels relevant to the area.",
        )
    if "urban" in signals:
        add(
            "Experiential Learning",
            "City-based visits, external partnerships, and access to local organisations may offer useful practical opportunities in this setting.",
        )
        add(
            "Student Voice",
            "Choice and feedback can also be used to shape visits, events, or project themes that make best use of local opportunities.",
        )
    if "community_links" in signals:
        add(
            "Key Strands",
            "Community and citizenship can be strengthened through local partnerships, service activity, and visible links between school life and the wider area.",
        )
        add(
            "Wellbeing",
            "The wellbeing strand may also benefit from activities that build belonging and connection across the school and wider community.",
        )
    if "deis" in signals or "inclusion_context" in signals:
        add(
            "Inclusion",
            "In this setting, particular care should be taken to keep participation manageable, accessible, and encouraging for all students across the year.",
        )
        add(
            "Wellbeing",
            "The wellbeing strand should also support belonging, confidence, attendance, and steady routines so that students experience TY as encouraging and achievable.",
        )
    if "gaelscoil" in signals:
        add(
            "Programme Overview",
            "In a gaelscoil or gaelcholáiste context, Irish should remain visible in the tone of the programme, in reflection tasks, and in how learning is presented publicly.",
        )
        add(
            "Teaching and Learning Approach",
            "Where appropriate, activities and presentations should help students use Irish confidently in practical, creative, and reflective settings.",
        )
    module_examples = []
    if "gaisce" in signals:
        module_examples.append("Gaisce")
    if "musical" in signals:
        module_examples.append("a musical or performance project")
    if "sport" in signals:
        module_examples.append("sports leadership or active wellbeing projects")
    if module_examples:
        joined = ", ".join(module_examples)
        add(
            "Core Modules",
            f"In this context, modules or projects such as {joined} may sit naturally alongside the wider programme.",
        )
    return plan


def tailor_section_body(heading: str, body: str, context: dict[str, str], language: str) -> str:
    additions = build_context_plan(context, language).get(heading, [])
    if not additions:
        return body
    return f"{body} {' '.join(additions)}"


def build_template_plan(question: str, language: str) -> str:
    sections = GA_TEMPLATE_SECTIONS if language == "ga" else EN_TEMPLATE_SECTIONS
    context_line = infer_school_context(question, language)
    context = parse_template_context(question)

    if language == "ga":
        title = "Plean Bliantúil na hIdirbhliana"
        subtitle = "Meán Fómhair 2026 go Bealtaine 2027"
    else:
        title = "Transition Year Annual Plan"
        subtitle = "September 2026 to May 2027"

    parts = [title, subtitle, "", context_line]
    for heading, body in sections:
        parts.append("")
        parts.append(heading)
        parts.append(tailor_section_body(heading, body, context, language))
    return "\n".join(parts).strip()


def template_headings(language: str) -> list[str]:
    sections = GA_TEMPLATE_SECTIONS if language == "ga" else EN_TEMPLATE_SECTIONS
    return [heading for heading, _ in sections]


def heading_aliases(language: str) -> dict[str, list[str]]:
    if language == "ga":
        return {
            "Forbhreathnú ar an gClár": ["forbhreathnu ar an gclar", "forbhreathnu", "overview"],
            "Réasúnaíocht": ["reasunaiocht"],
            "Aidhmeanna": ["aidhmeanna", "cuspóirí", "cuspoiri"],
            "Struchtúr an Chláir": ["struchtur an chláir", "struchtur an ghlar", "struchtur"],
            "Príomhshnáitheanna": ["priomhshnaitheanna", "snaitheanna"],
            "Struchtúr na Bliana": ["struchtur na bliana", "struchtur bliana"],
            "Croí-Mhodúil": ["croi-mhoduil", "croi moduil", "moduil"],
            "Cur Chuige Teagaisc agus Foghlama": ["cur chuige teagaisc agus foghlama", "cur chuige foghlama"],
            "Guth na Mac Léinn": ["guth na mac leinn", "guth na ndaltai", "guth na scolairi"],
            "Folláine": ["follaine"],
            "Foghlaim ó thaithí": ["foghlaim o thaithi", "foghlaim thaithiuil", "taithi phraiticiuil"],
            "Cuimsiú": ["cuimsiu", "ionchuimsiu"],
            "Measúnú": ["measunu"],
            "Punann": ["punann", "portfoilio"],
            "Cumarsáid le Tuismitheoirí": ["cumarsaíd le tuismitheoirí", "cumarsaid le tuismitheoiri", "cumarsaid le tuismitheoirí"],
            "Athbhreithniú": ["athbhreithniu", "athbhreithniu an chláir"],
            "Féilire Achomair": ["feilire achomair", "achoimre ama", "feilire"],
        }
    return {
        "Programme Overview": ["programme overview", "overview"],
        "Rationale": ["rationale", "programme rationale"],
        "Aims": ["aims", "programme aims"],
        "Programme Structure": ["programme structure", "structure of the programme"],
        "Key Strands": ["key strands", "programme strands", "main strands"],
        "Year Structure": ["year structure", "structure of the year"],
        "Core Modules": ["core modules", "modules"],
        "Teaching and Learning Approach": ["teaching and learning approach", "approach to teaching and learning"],
        "Student Voice": ["student voice", "learner voice"],
        "Wellbeing": ["wellbeing"],
        "Experiential Learning": ["experiential learning", "practical learning"],
        "Inclusion": ["inclusion", "inclusive practice"],
        "Assessment": ["assessment"],
        "Portfolio": ["portfolio"],
        "Parent Communication": ["parent communication", "communication with parents"],
        "Review": ["review", "programme review"],
        "Summary Calendar": ["summary calendar", "calendar", "annual calendar"],
    }


def find_heading_position(text: str, variants: list[str], start_index: int) -> int:
    next_positions = [text.find(variant, start_index) for variant in variants]
    valid_positions = [position for position in next_positions if position != -1]
    return min(valid_positions) if valid_positions else -1


def build_openai_template_instructions(language: str) -> str:
    if language == "ga":
        headings = "\n".join(f"{idx}. {heading}" for idx, heading in enumerate(template_headings("ga"), start=1))
        return (
            "Write a full Transition Year annual plan as a professional school planning document. "
            "The output must be complete, realistic, editable, and suitable for a TY coordinator. "
            "Use clear, natural, school-appropriate Irish. Keep the Irish clear rather than elaborate. "
            "Return plain text only. Do not return JSON. Do not add meta commentary. Do not skip any section. "
            "Add light concrete anchors where useful so the plan feels school-usable rather than generic. "
            "In the Core Modules section, include three to five realistic example modules where they fit the school context. "
            "In the Student Voice, Wellbeing, and Experiential Learning sections, include one or two concrete school-realistic examples where useful, without adding long lists or repeating the same examples across sections. "
            "In relevant sections, acknowledge practical constraints such as staffing, time, available resources, budget, and access, but do so lightly and without adding calculations or pricing detail. "
            "Make the Summary Calendar practical and planning-oriented, with clear progression across the year. "
            "Include one explicit sentence stating that the plan should be adapted to the ethos, context, and priorities of the school. "
            "Integrate school-specific context naturally into the narrative. Avoid repeating the same context sentence across multiple sections. "
            "Allow major priorities or ethos to appear strongly once and then only lightly where relevant. "
            "Use these exact section headings and this exact order:\n"
            f"{headings}\n"
            "Include all seventeen sections. Use placeholders only where school-specific information is missing."
        )
    headings = "\n".join(f"{idx}. {heading}" for idx, heading in enumerate(template_headings("en"), start=1))
    return (
        "Write a full Transition Year annual plan as a professional school planning document. "
        "The output must be complete, realistic, editable, and suitable for a TY coordinator. "
        "Use a professional school-document tone. Return plain text only. Do not return JSON. "
        "Do not add meta commentary. Do not skip any section. "
        "Add light concrete anchors where useful so the plan feels school-usable rather than generic. "
        "In the Core Modules section, include three to five realistic example modules where they fit the school context. "
        "In the Student Voice, Wellbeing, and Experiential Learning sections, include one or two concrete school-realistic examples where useful, without adding long lists or repeating the same examples across sections. "
        "In relevant sections, acknowledge practical constraints such as staffing, time, available resources, budget, and access, but do so lightly and without adding calculations or pricing detail. "
        "Make the Summary Calendar practical and planning-oriented, with clear progression across the year. "
        "Include one explicit sentence stating that the plan should be adapted to the ethos, context, and priorities of the school. "
        "Integrate school-specific context naturally into the narrative. Avoid repeating the same context sentence across multiple sections. "
        "Allow major priorities or ethos to appear strongly once and then only lightly where relevant. "
        "Use these exact section headings and this exact order:\n"
        f"{headings}\n"
        "Include all seventeen sections. Use placeholders only where school-specific information is missing."
    )


def build_openai_template_prompt(question: str, language: str) -> str:
    context = parse_template_context(question)
    school_name = context.get("school_name", "Not specified")
    cohort_size = context.get("cohort_size", "Not specified")
    school_type = context.get("school_type", "Not specified")
    school_ethos = context.get("school_ethos", "Not specified")
    priorities = context.get("priorities", "Not specified")
    existing_modules = context.get("existing_modules", "Not specified")
    work_experience = context.get("work_experience", "Not specified")
    additional_context = context.get("additional_context", "Not specified")
    language_label = "Irish" if language == "ga" else context.get("language", "English")

    if language == "ga":
        return (
            "Cruthaigh plean bliantúil iomlán don Idirbhliain.\n\n"
            "Úsáid an comhthéacs seo más ábhartha:\n"
            f"Ainm na scoile: {school_name}\n"
            f"Méid an chohóirt: {cohort_size}\n"
            f"Cineál scoile: {school_type}\n"
            f"Éiteas na scoile: {school_ethos}\n"
            f"Príomhthosaíochtaí: {priorities}\n"
            f"Modúil atá ann cheana: {existing_modules}\n"
            f"Amchlár na taithí oibre: {work_experience}\n"
            f"Comhthéacs breise: {additional_context}\n"
            f"Teanga: {language_label}\n\n"
            "Caithfidh an plean:\n"
            "- comhthéacs na scoile a léiriú nuair atá sé ar fáil\n"
            "- ainm na scoile agus méid an chohóirt a úsáid go nádúrtha nuair is cuí\n"
            "- tosaíochtaí luaite a chur chun tosaigh\n"
            "- modúil atá ann cheana a chur san áireamh nuair is cuí\n"
            "- taithí oibre a eagrú go praiticiúil\n"
            "- comhthéacs breise nó éiteas a fhí isteach go nádúrtha seachas é a athrá mar abairt ar leith\n"
            "- a bheith inchreidte i gcomhthéacs chleachtas fíor na hIdirbhliana in Éirinn\n"
            "- a bheith oiriúnach le haghaidh eagarthóireachta agus úsáide i scoil\n"
            "- na ceannteidil sheasta a úsáid go díreach agus san ord ceart\n\n"
            f"Iarratas úsáideora bunaidh: {question}"
        )

    return (
        "Create a full Transition Year annual plan.\n\n"
        "Use this context where relevant:\n"
        f"School name: {school_name}\n"
        f"Cohort size: {cohort_size}\n"
        f"School type: {school_type}\n"
        f"School ethos: {school_ethos}\n"
        f"Main priorities: {priorities}\n"
        f"Existing modules: {existing_modules}\n"
        f"Work experience timing: {work_experience}\n"
        f"Additional context: {additional_context}\n"
        f"Language: {language_label}\n\n"
        "The plan must:\n"
        "- reflect the school context where provided\n"
        "- use the school name and cohort context naturally where relevant\n"
        "- prioritise the stated focus areas\n"
        "- incorporate existing modules where relevant\n"
        "- structure work experience in a practical way\n"
        "- weave additional context or ethos into the document naturally rather than repeating it as a standalone sentence\n"
        "- feel realistic in the context of current Irish TY practice\n"
        "- remain realistic, editable, and useful for a TY coordinator\n"
        "- use the fixed section headings exactly and in the correct order\n\n"
        f"Original user request: {question}"
    )


def extract_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", "")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = getattr(response, "output", None)
    if not output:
        return ""

    collected: list[str] = []
    for item in output:
        content = getattr(item, "content", None) or item.get("content", [])  # type: ignore[union-attr]
        for block in content:
            text = getattr(block, "text", None)
            if isinstance(text, str) and text.strip():
                collected.append(text.strip())
            elif isinstance(block, dict):
                maybe_text = block.get("text")
                if isinstance(maybe_text, str) and maybe_text.strip():
                    collected.append(maybe_text.strip())
    return "\n".join(collected).strip()


def validate_template_output(text: str, language: str) -> bool:
    if not text.strip():
        return False
    lowered_text = text.lower()
    alias_map = heading_aliases(language)
    current_index = -1
    matched_sections = 0

    for heading in template_headings(language):
        variants = [variant.lower() for variant in alias_map.get(heading, [heading])]
        next_index = find_heading_position(lowered_text, variants, current_index + 1)
        if next_index == -1:
            continue
        if next_index <= current_index:
            continue
        matched_sections += 1
        current_index = next_index

    required_matches = max(1, int(0.8 * len(template_headings(language))))
    return matched_sections >= required_matches


def generate_template_plan_openai(question: str, language: str) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
    if not api_key:
        print(
            f"[ty-plan-openai] attempted=false model={model} fallback=true reason=missing_api_key",
            flush=True,
        )
        return "", "local_generation_fallback"

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover
        print(
            f"[ty-plan-openai] attempted=false model={model} fallback=true reason=sdk_import_failed detail={exc.__class__.__name__}",
            flush=True,
        )
        return "", "local_generation_fallback"

    print(f"[ty-plan-openai] attempted=true model={model} fallback=false", flush=True)
    try:
        client = OpenAI()
        response = client.responses.create(
            model=model,
            instructions=build_openai_template_instructions(language),
            input=build_openai_template_prompt(question, language),
        )
    except Exception as exc:  # pragma: no cover
        print(
            f"[ty-plan-openai] attempted=true model={model} fallback=true reason=request_failed detail={exc.__class__.__name__}",
            flush=True,
        )
        return "", "local_generation_fallback"

    output_text = extract_response_text(response)
    if not validate_template_output(output_text, language):
        print(
            f"[ty-plan-openai] attempted=true model={model} fallback=true reason=invalid_output chars={len(output_text)}",
            flush=True,
        )
        return "", "local_generation_fallback"

    print(
        f"[ty-plan-openai] attempted=true model={model} fallback=false result=openai_generation chars={len(output_text)}",
        flush=True,
    )
    return output_text, "openai_generation"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def clean_display_text(text: str) -> str:
    stripped = re.sub(r"(?m)^\s*#+\s*", "", text)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped


def snippet(text: str, max_chars: int = 180) -> str:
    compact = clean_display_text(text)
    return compact[: max_chars - 3] + "..." if len(compact) > max_chars else compact


def query_vector(question: str, idf: dict[str, float]) -> tuple[dict[str, float], float]:
    counts = Counter(tokenize(question))
    total = sum(counts.values()) or 1
    weights = {}
    norm = 0.0
    for term, count in counts.items():
        if term not in idf:
            continue
        weight = (count / total) * idf[term]
        weights[term] = weight
        norm += weight * weight
    return weights, math.sqrt(norm)


def score_document(doc: dict[str, object], q_weights: dict[str, float], q_norm: float) -> float:
    d_weights: dict[str, float] = doc["weights"]  # type: ignore[assignment]
    dot = 0.0
    for term, q_weight in q_weights.items():
        dot += q_weight * d_weights.get(term, 0.0)
    d_norm = float(doc.get("norm", 0.0))
    if dot == 0.0 or q_norm == 0.0 or d_norm == 0.0:
        return 0.0
    return dot / (q_norm * d_norm)


def answer_mode(question: str) -> str:
    tokens = set(tokenize(question))
    if tokens & {"purpose", "policy", "inclusive", "inclusion", "support", "supports", "voice", "achieve", "achievement"}:
        return "official_guidance_priority"
    if tokens & {"module", "modules", "ideas", "theme", "themes", "design", "wellbeing", "resilience", "growth", "mindset"}:
        return "ciunas_framework_supported"
    if "structure" in tokens and "school" in tokens:
        return "blended_planning"
    if tokens & {"planning", "plan"}:
        return "official_guidance_priority"
    official_hits = len(tokens & OFFICIAL_KEYWORDS)
    framework_hits = len(tokens & FRAMEWORK_KEYWORDS)
    if official_hits >= framework_hits + 1:
        return "official_guidance_priority"
    if framework_hits >= official_hits + 1:
        return "ciunas_framework_supported"
    return "blended_planning"


def rerank(question: str, documents: list[dict[str, object]]) -> list[tuple[float, dict[str, object]]]:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    q_weights, q_norm = query_vector(question, index["idf"])
    mode = answer_mode(question)

    ranked = []
    for doc in documents:
        score = score_document(doc, q_weights, q_norm)
        if score <= 0:
            continue
        if mode == "official_guidance_priority":
            score *= 1.15 if doc["source_layer"] == "official_guidance" else 0.92
        elif mode == "ciunas_framework_supported":
            score *= 1.2 if doc["source_layer"] == "ciunas_framework" else 0.96
        else:
            score *= 1.08 if doc["source_layer"] == "official_guidance" else 1.02
        if doc.get("doc_status") == "validation_warning":
            score *= 0.9
        ranked.append((score, doc))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked


def split_sentences(text: str) -> list[str]:
    normalised = clean_display_text(text)
    parts = re.split(r"(?<=[.!?])\s+", normalised)
    return [part.strip() for part in parts if part.strip()]


def question_category(question: str) -> str:
    lowered = question.lower()
    if any(term in lowered for term in ("ideas", "examples", "activities")):
        return "ideas"
    if any(term in lowered for term in ("engaged", "motivation", "interest")):
        return "engagement"
    if any(term in lowered for term in ("outline", "weeks", "week ", "week-", "across the weeks", "six week", "6 week")):
        return "outline"
    if "wellbeing" in lowered:
        return "wellbeing"
    if "student voice" in lowered or ("student" in lowered and "voice" in lowered):
        return "student_voice"
    if "inclusive" in lowered or "inclusion" in lowered:
        return "inclusive"
    if "what is ty" in lowered or "supposed to achieve" in lowered or "purpose" in lowered or "aim" in lowered:
        return "purpose"
    if any(term in lowered for term in ("structure", "organise", "across the year")):
        return "structure"
    if "resilience" in lowered or "growth mindset" in lowered:
        return "resilience"
    return "general"


def available_layers(ranked: list[tuple[float, dict[str, object]]]) -> list[str]:
    layers = []
    for _, doc in ranked:
        layer = str(doc["source_layer"])
        if layer not in layers:
            layers.append(layer)
    return layers


def make_point(layer: str, body: str) -> str:
    return f"[{layer}] {body}"


def dedupe_points(points: list[str], max_points: int = 5) -> list[str]:
    cleaned = []
    seen = set()
    for point in points:
        body = re.sub(r"^\[[^\]]+\]\s+", "", point).strip().lower()
        body = re.sub(r"[^a-z0-9\s]+", "", body)
        if body in seen:
            continue
        seen.add(body)
        cleaned.append(point)
        if len(cleaned) >= max_points:
            break
    return cleaned


def sentence_is_artefact(sentence: str) -> bool:
    lowered = sentence.lower().strip()
    if not lowered:
        return True
    if lowered.startswith(("this section", "section ", "table ", "appendix ", "chapter ", "note ")):
        return True
    if lowered.startswith(("transition year programmes", "introductory note", "these guidelines", "the main purpose of the guidelines")):
        return True
    if re.match(r"^\d+\s", lowered):
        return True
    if any(
        marker in lowered
        for marker in (
            "table 1",
            "table 2",
            "table 3",
            "section opens",
            "the statement offers",
            "introductory note",
            "circulars m31/93",
            "circulars m47/93",
        )
    ):
        return True
    if len(tokenize(lowered)) < 7:
        return True
    return False


def normalise_sentence(sentence: str) -> str:
    text = clean_display_text(sentence)
    text = text.replace("...", " ")
    text = re.sub(r"\bthis section\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthe statement\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\btable \d+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsection \d+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .,:;-")
    return text


def compress_sentence(sentence: str, max_words: int = 18) -> str:
    words = sentence.split()
    if len(words) <= max_words:
        return sentence.rstrip(".")
    trimmed = " ".join(words[:max_words]).rstrip(",;:-")
    return trimmed.rstrip(".")


def sentence_topic(sentence: str) -> str:
    lowered = sentence.lower()
    topic_map = {
        "choice": {"choice", "choices", "student voice", "student", "students"},
        "planning": {"plan", "planning", "review", "evaluate", "renewal", "coordinator"},
        "inclusion": {"inclusive", "diversity", "support", "supports", "participation", "accessible"},
        "wellbeing": {"wellbeing", "health", "relationships", "reflection", "regulation"},
        "experience": {"experience", "experiential", "project", "projects", "community", "work"},
        "growth": {"growth", "maturity", "responsibility", "resilience", "mindset"},
    }
    for topic, terms in topic_map.items():
        if any(term in lowered for term in terms):
            return topic
    return "general"


def topic_matches_category(topic: str, category: str) -> bool:
    preferred = {
        "structure": {"planning", "choice", "experience"},
        "purpose": {"growth", "experience", "wellbeing"},
        "ideas": {"experience", "wellbeing", "growth", "choice"},
        "outline": {"planning", "experience", "wellbeing", "growth"},
        "engagement": {"choice", "wellbeing", "experience", "growth"},
        "wellbeing": {"wellbeing", "growth", "inclusion"},
        "student_voice": {"choice", "planning"},
        "inclusive": {"inclusion", "planning"},
        "resilience": {"growth", "wellbeing"},
        "general": {"general", "planning", "experience", "growth"},
    }
    return topic in preferred.get(category, {"general"}) or (category == "general" and topic == "general")


def rewrite_as_guidance(sentence: str, layer: str, question: str, mode: str) -> str:
    text = normalise_sentence(sentence)
    lowered = text.lower()

    replacements = [
        (r"\bthe transition year should\b", ""),
        (r"\bthe ty programme should\b", ""),
        (r"\ba programme aligned to the ty programme statement\b", "the programme"),
        (r"\bschools should ensure\b", ""),
        (r"\bit is intended that\b", ""),
        (r"\bit is important that\b", ""),
        (r"\bcan be encouraged and promoted by\b", "can be strengthened by"),
        (r"\bis designed to\b", "should"),
        (r"\bis intended to\b", "should"),
        (r"\bprovides opportunities to\b", "should"),
        (r"\boffers opportunities to\b", "should"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .,:;-")
    lowered = text.lower()

    if "student voice" in question.lower() or "voice" in lowered:
        guidance = "Build student voice into planning, review, and day-to-day programme choices."
    elif any(term in lowered for term in ("inclusive", "diversity", "participation", "support", "accessible")):
        guidance = "Plan for flexible participation and suitable supports so all students can take part meaningfully."
    elif any(term in lowered for term in ("review", "evaluate", "renewal", "coordinator", "planning")):
        guidance = "Review the programme regularly and use clear coordination so it can be adjusted during the year."
    elif any(term in lowered for term in ("choice", "choices", "agency", "designing their own")):
        guidance = "Give students real choices over themes, projects, and how some learning is shaped."
    elif any(term in lowered for term in ("wellbeing", "health", "reflection", "relationships", "regulation")):
        guidance = "Build in regular reflection, relationships, and wellbeing routines rather than treating them as add-ons."
    elif any(term in lowered for term in ("project", "community", "experience", "work", "experiential")):
        guidance = "Use practical experiences, projects, and community-based learning to make TY active and applied."
    elif any(term in lowered for term in ("growth", "maturity", "responsibility", "mindset", "resilience")):
        guidance = "Use TY to build maturity, responsibility, and confidence through challenge and reflection."
    elif "official_guidance" == layer and mode == "official_guidance_priority":
        guidance = "Translate the guidance into a clear planning decision that fits your school context."
    elif layer == "ciunas_framework":
        guidance = "Turn the framework ideas into a clear module or programme strand that students can practise."
    else:
        guidance = text

    guidance = compress_sentence(guidance)
    if not guidance.endswith("."):
        guidance += "."
    return guidance[0].upper() + guidance[1:]


def source_layer_for_points(chunks: list[tuple[float, dict[str, object]]], preferred: str | None = None) -> str:
    layers = available_layers(chunks)
    if preferred and preferred in layers:
        return preferred
    return layers[0] if layers else "official_guidance"


def framework_examples_from_chunks(chunks: list[tuple[float, dict[str, object]]], max_examples: int = 3) -> list[str]:
    examples = []
    seen = set()
    for _, doc in chunks:
        if str(doc["source_layer"]) != "ciunas_framework":
            continue
        title = clean_display_text(str(doc.get("title", "")))
        title = re.sub(r"^(Chapter|Phase|Ciunas Framework Overview):?\s*", "", title, flags=re.IGNORECASE).strip()
        if not title:
            continue
        lowered = title.lower()
        if lowered in {"framework overview", "overview"}:
            continue
        if lowered in seen:
            continue
        seen.add(lowered)
        examples.append(title)
        if len(examples) >= max_examples:
            break
    return examples


def enforce_question_type_points(
    question: str, chunks: list[tuple[float, dict[str, object]]], mode: str, points: list[str]
) -> list[str]:
    category = question_category(question)
    point_map = {re.sub(r"^\[[^\]]+\]\s+", "", p): p for p in points}

    def add(layer: str, body: str) -> None:
        point_map.setdefault(body, make_point(layer, body))

    official_layer = source_layer_for_points(chunks, "official_guidance")
    framework_layer = source_layer_for_points(chunks, "ciunas_framework")

    if category == "structure":
        add(official_layer, "Keep the programme coherent so modules connect to a clear TY rationale.")
        add(official_layer, "Balance the year across personal development, active learning, and broader experiences.")
        add(official_layer, "Build progression across the year so students move from orientation to deeper responsibility.")
        add(official_layer, "Give students meaningful choice in themes, projects, and how work is presented.")
    elif category == "purpose":
        add(official_layer, "Use TY to help students mature in confidence, responsibility, and decision-making.")
        add(official_layer, "Broaden learning beyond exam preparation through projects, experience, and reflection.")
        add(official_layer, "Make personal development a visible part of the year, not an indirect by-product.")
    elif category == "outline":
        outline_layer = framework_layer if mode == "ciunas_framework_supported" else official_layer
        return [
            make_point(outline_layer, "Week 1-2: introduce the theme, set expectations, and gather student interests."),
            make_point(outline_layer, "Week 3-4: use practical activities, discussion, and reflection to build the core learning."),
            make_point(outline_layer, "Week 5-6: finish with a project, presentation, or review task that shows progress."),
        ]
    elif category == "ideas":
        examples = framework_examples_from_chunks(chunks)
        if examples:
            add(framework_layer, f"Use concrete themes such as {', '.join(examples[:3])} as starting points for TY activities.")
        add(framework_layer, "Include practical activities, short challenges, and reflection tasks rather than relying on discussion alone.")
        add(framework_layer, "Turn each idea into a short module with a clear question, activity, and review point.")
    elif category == "engagement":
        add(official_layer, "Increase engagement by giving students real choice over topics, roles, and outputs.")
        add(official_layer, "Use variation across discussion, project work, community activity, and reflection so TY does not feel repetitive.")
        add(official_layer, "Build regular review points so students can see progress and reconnect with the purpose of the programme.")

    return list(point_map.values())


def starts_with_vague_phrase(text: str) -> bool:
    lowered = text.lower().strip()
    vague_starts = (
        "a useful ty response",
        "the clearest starting point",
        "a practical ty answer",
        "this means",
        "it is important",
        "it is intended",
    )
    return lowered.startswith(vague_starts)


def action_quality_filter(points: list[str], max_points: int = 5) -> list[str]:
    approved = []
    starters = {
        "build",
        "keep",
        "balance",
        "give",
        "use",
        "plan",
        "review",
        "set",
        "organise",
        "link",
        "make",
        "treat",
        "coordinate",
        "increase",
        "include",
        "introduce",
        "finish",
        "week",
    }
    for point in points:
        layer, body = re.match(r"^\[(.*?)\]\s+(.*)$", point).groups() if re.match(r"^\[(.*?)\]\s+(.*)$", point) else (None, point)
        cleaned = body.strip()
        if len(cleaned.split()) < 6:
            continue
        if starts_with_vague_phrase(cleaned):
            continue
        first_word = cleaned.split()[0].lower().rstrip(":")
        if first_word not in starters and not cleaned.lower().startswith("week "):
            continue
        rebuilt = make_point(layer, cleaned) if layer else cleaned
        approved.append(rebuilt)
        if len(approved) >= max_points:
            break
    return approved


def fallback_points(question: str, ranked: list[tuple[float, dict[str, object]]], mode: str) -> list[str]:
    category = question_category(question)
    layers = available_layers(ranked)
    primary_layer = layers[0] if layers else "official_guidance"
    secondary_layer = layers[1] if len(layers) > 1 else primary_layer

    if category == "structure":
        points = [
            make_point("official_guidance", "Set out a clear TY rationale so the year is distinct from Leaving Certificate preparation."),
            make_point("official_guidance", "Organise the programme as a balanced mix of personal development, subject sampling, and experiential learning."),
            make_point("official_guidance", "Build student choice into modules, projects, and activities rather than treating TY as a fixed timetable only."),
            make_point("official_guidance", "Assign clear coordination and review points so the programme can be adjusted during the year."),
        ]
        if "ciunas_framework" in layers:
            points.append(make_point("ciunas_framework", "Use the framework to shape coherent strands or themes so modules feel connected rather than one-off events."))
        return dedupe_points(points)

    if category == "purpose":
        points = [
            make_point("official_guidance", "Use TY to broaden learning beyond exam preparation and give students space to mature."),
            make_point("official_guidance", "Plan for personal, social, and academic growth rather than treating the year as extra Leaving Certificate time."),
            make_point("official_guidance", "Include experiences that help students test interests, responsibility, and future pathways."),
            make_point("official_guidance", "Review success in terms of development, engagement, and readiness for the next stage of school."),
        ]
        return dedupe_points(points)

    if category == "ideas":
        points = [
            make_point(secondary_layer, "Use short practical activities, reflection prompts, and small projects to turn ideas into TY learning."),
            make_point(secondary_layer, "Choose examples that connect with student life so activities feel relevant and usable."),
            make_point(primary_layer, "Link each activity to a wider TY aim so the ideas feel part of a coherent programme."),
        ]
        return dedupe_points(points)

    if category == "outline":
        points = [
            make_point(primary_layer, "Week 1-2: introduce the theme, set expectations, and gather student interests."),
            make_point(primary_layer, "Week 3-4: develop the main learning through activities, discussion, and reflection."),
            make_point(primary_layer, "Week 5-6: complete a project, presentation, or review task to consolidate learning."),
        ]
        return dedupe_points(points)

    if category == "engagement":
        points = [
            make_point(primary_layer, "Increase engagement by giving students choice over themes, roles, and outputs."),
            make_point(primary_layer, "Use a varied mix of discussion, active tasks, and reflection so TY does not feel repetitive."),
            make_point(primary_layer, "Build regular review points so students can see progress and stay connected to the purpose of the year."),
        ]
        return dedupe_points(points)

    if category == "wellbeing":
        points = [
            make_point("official_guidance", "Treat wellbeing as a planned TY strand with clear aims, not as an occasional add-on session."),
            make_point("ciunas_framework" if "ciunas_framework" in layers else primary_layer, "Build the module around practical habits such as reflection, relationships, regulation, and everyday routines."),
            make_point("official_guidance", "Link the module to whole-school wellbeing and student-support structures so students know where help sits."),
            make_point("ciunas_framework" if "ciunas_framework" in layers else secondary_layer, "Use activities, discussion, and short applied tasks so students can practise ideas rather than only talk about them."),
            make_point("official_guidance", "Gather student feedback during the module and use it to refine the next cycle."),
        ]
        return dedupe_points(points)

    if category == "student_voice":
        points = [
            make_point("official_guidance", "Involve students in shaping TY priorities before the programme begins and at review points during the year."),
            make_point("official_guidance", "Give students real choices over themes, projects, and how some learning is presented or shared."),
            make_point("official_guidance", "Use reflection and feedback routines so student views influence adjustments rather than being collected once and ignored."),
            make_point("official_guidance", "Treat student voice as part of programme design, not just as a once-off survey."),
        ]
        if "ciunas_framework" in layers:
            points.append(make_point("ciunas_framework", "Use framework themes to help students name what matters to them and turn that into module ideas or community action."))
        return dedupe_points(points)

    if category == "inclusive":
        points = [
            make_point("official_guidance", "Plan TY so all students can participate meaningfully through flexible pathways, accessible activities, and suitable supports."),
            make_point("official_guidance", "Review entry points, workload, and communication so students with different needs are not excluded by design."),
            make_point("official_guidance", "Coordinate TY planning with student-support and SEN processes rather than treating inclusion as a separate issue."),
            make_point("official_guidance", "Use broader reporting and reflection methods so student progress is recognised in more than one way."),
        ]
        return dedupe_points(points)

    if category == "resilience":
        points = [
            make_point("ciunas_framework" if "ciunas_framework" in layers else primary_layer, "Teach resilience as something students build through repeated practice, reflection, and support."),
            make_point("ciunas_framework" if "ciunas_framework" in layers else primary_layer, "Use structured challenges that let students notice effort, setbacks, and progress over time."),
            make_point("official_guidance" if "official_guidance" in layers else secondary_layer, "Keep the work aligned with TY aims by focusing on growth, maturity, and learning habits rather than performance pressure."),
            make_point("ciunas_framework" if "ciunas_framework" in layers else primary_layer, "Link mindset language to daily routines such as review, goal-setting, and recovery after difficulty."),
        ]
        return dedupe_points(points)

    if mode == "official_guidance_priority":
        points = [
            make_point("official_guidance", "Start from the official TY expectations and translate them into a clear whole-school planning decision."),
            make_point("official_guidance", "Turn broad guidance into practical choices about structure, student experience, and review."),
            make_point("official_guidance", "Use the strongest available guidance first and add detail only where it helps local planning."),
            make_point("official_guidance", "Check that the plan remains distinct from exam-focused provision."),
        ]
        return dedupe_points(points)

    points = [
        make_point(primary_layer, "Use the retrieved guidance to shape a clear TY response that fits your school context."),
        make_point(primary_layer, "Prioritise a small number of practical planning moves rather than trying to cover everything at once."),
        make_point(secondary_layer, "Combine policy context with programme-design ideas where that helps make the next step more concrete."),
        make_point(primary_layer, "Review the plan with staff and students so the programme can be refined as evidence builds."),
    ]
    return dedupe_points(points)


def transform_chunks_to_guidance(
    chunks: list[tuple[float, dict[str, object]]], question: str, mode: str, max_points: int = 5
) -> list[str]:
    category = question_category(question)
    candidates = []
    for score, doc in chunks[:5]:
        layer = str(doc["source_layer"])
        for sentence in split_sentences(str(doc["text"])):
            if sentence_is_artefact(sentence):
                continue
            normalised = normalise_sentence(sentence)
            if not normalised:
                continue
            topic = sentence_topic(normalised)
            if not topic_matches_category(topic, category):
                continue
            guidance = rewrite_as_guidance(normalised, layer, question, mode)
            priority = score
            if topic == category:
                priority += 1.0
            if layer == "official_guidance" and mode == "official_guidance_priority":
                priority += 0.4
            if layer == "ciunas_framework" and mode == "ciunas_framework_supported":
                priority += 0.4
            candidates.append((priority, topic, make_point(layer, guidance)))

    candidates.sort(key=lambda item: item[0], reverse=True)
    points = []
    seen_topics = set()
    for _, topic, point in candidates:
        if topic in seen_topics and topic != "general":
            continue
        seen_topics.add(topic)
        points.append(point)
        if len(points) >= max_points:
            break
    points = dedupe_points(points, max_points=max_points)
    points = enforce_question_type_points(question, chunks, mode, points)
    points = dedupe_points(points, max_points=max_points + 3)
    points = action_quality_filter(points, max_points=max_points)

    if len(points) < 3:
        fallback = fallback_points(question, chunks, mode)
        points = dedupe_points(points + fallback, max_points=max_points + 3)
        points = action_quality_filter(points, max_points=max_points)
    return points[:max_points]


def first_sentence(question: str, ranked: list[tuple[float, dict[str, object]]], mode: str) -> str:
    lowered = question.lower()
    if "what is transition year supposed to achieve" in lowered or "what is transition year supposed to achieve?" in lowered or "what is ty" in lowered:
        return "Transition Year should broaden learning, support personal development, and create space for exploration beyond the exam track."
    if any(term in lowered for term in ("structure", "organise", "across the year")):
        return "A strong Transition Year programme should be organised as a coherent whole-school programme with clear aims, balanced strands, and room for student choice."
    if any(term in lowered for term in ("outline", "weeks", "week ", "week-", "across the weeks", "six week", "6 week")):
        return "A useful TY outline should move from orientation into active learning and finish with reflection or a shared outcome."
    if any(term in lowered for term in ("ideas", "examples", "activities")):
        return "The strongest TY ideas are concrete, practical, and clearly connected to the wider purpose of the programme."
    if any(term in lowered for term in ("engaged", "motivation", "interest")):
        return "Students stay engaged in TY when the programme offers choice, variety, and regular chances to reflect on progress."
    if "wellbeing" in lowered:
        return "A TY wellbeing module works best when it is planned as a structured strand with reflection, practical activity, and clear links to whole-school supports."
    if "student voice" in lowered:
        return "Student voice in TY should shape planning, review, and the day-to-day design of learning experiences."
    if "inclusive" in lowered:
        return "Inclusive education in a TY context means planning the programme so all students can participate meaningfully with suitable supports and flexible pathways."
    if "resilience" in lowered or "growth mindset" in lowered:
        return "TY can build resilience and growth mindset by giving students structured challenges, regular reflection, and explicit language for progress over time."
    if ranked:
        return "The strongest answer here is the one that turns the retrieved guidance into a clear planning move for your school."
    return "No grounded answer could be assembled from the current source set."


def build_sources(ranked: list[tuple[float, dict[str, object]]], max_sources: int = 4) -> list[dict[str, str]]:
    sources = []
    seen = set()
    for _, doc in ranked:
        key = (doc["title"], doc["source_layer"])
        if key in seen:
            continue
        seen.add(key)
        entry = {
            "title": str(doc["title"]),
            "source_layer": str(doc["source_layer"]),
            "chunk_id": str(doc["chunk_id"]),
        }
        if doc.get("doc_status") == "validation_warning":
            entry["source_note"] = "weak_source"
        sources.append(entry)
        if len(sources) >= max_sources:
            break
    return sources


def select_top_ranked(mode: str, ranked: list[tuple[float, dict[str, object]]], max_items: int = 5) -> list[tuple[float, dict[str, object]]]:
    selected = list(ranked[:max_items])
    layers = {str(doc["source_layer"]) for _, doc in selected}

    if mode == "ciunas_framework_supported" and "ciunas_framework" not in layers:
        for item in ranked[max_items:]:
            if item[1]["source_layer"] == "ciunas_framework":
                selected[-1] = item if selected else item
                break
    if mode == "official_guidance_priority" and "official_guidance" not in layers:
        for item in ranked[max_items:]:
            if item[1]["source_layer"] == "official_guidance":
                selected[-1] = item if selected else item
                break
    return selected


def evidence_note(ranked: list[tuple[float, dict[str, object]]], mode: str) -> str:
    layers = []
    weak_titles = []
    for _, doc in ranked[:5]:
        layer = str(doc["source_layer"])
        if layer not in layers:
            layers.append(layer)
        if doc.get("doc_status") == "validation_warning":
            weak_titles.append(str(doc["title"]))

    layer_note = (
        "Evidence uses both official guidance and Ciunas framework sources."
        if len(layers) > 1
        else f"Evidence uses {layers[0]} only." if layers else "No evidence retrieved."
    )
    weak_note = ""
    if weak_titles:
        weak_note = f" Weak-source warning: {weak_titles[0]} is flagged as a weaker source."
    return f"{layer_note}{weak_note}".strip()


def answer_question(question: str) -> dict[str, object]:
    if is_template_generation_request(question):
        language = detect_template_language(question)
        openai_answer, generation_source = generate_template_plan_openai(question, language)
        if openai_answer:
            return {
                "answer": openai_answer,
                "key_points": [],
                "sources": [],
                "evidence_note": (
                    "Annual plan generated with OpenAI using the fixed TY template structure."
                    if language == "en"
                    else "Gineadh an plean bliantúil le OpenAI ag úsáid struchtúr seasta teimpléid TY."
                ),
                "answer_mode": "template_generation_ga" if language == "ga" else "template_generation_en",
                "language": language,
                "generation_source": generation_source,
                "model_used": os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL,
            }

        local_answer = build_template_plan(question, language)
        return {
            "answer": local_answer,
            "key_points": [],
            "sources": [],
            "evidence_note": (
                "Template generation mode uses the fixed annual-plan structure. Local generation was used as the fallback."
                if language == "en"
                else "Úsáideann mód giniúna teimpléid struchtúr seasta an phlean bhliantúil. Úsáideadh giniúint áitiúil mar chúltaca."
            ),
            "answer_mode": "template_generation_ga" if language == "ga" else "template_generation_en",
            "language": language,
            "generation_source": "local_generation_fallback",
            "model_used": "",
        }

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    mode = answer_mode(question)
    ranked = rerank(question, index["documents"])
    top_chunks = select_top_ranked(mode, ranked, max_items=5)
    key_points = transform_chunks_to_guidance(top_chunks, question, mode, max_points=5)

    assert all(
        isinstance(k, str) and not k.lower().startswith("this section")
        for k in key_points
    ), "Key points are not transformed"

    return {
        "answer": first_sentence(question, top_chunks, mode),
        "key_points": key_points[:5],
        "sources": build_sources(top_chunks, max_sources=4),
        "evidence_note": evidence_note(top_chunks, mode),
        "answer_mode": mode,
        "language": "en",
        "generation_source": "local_qa",
        "model_used": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a grounded local TY planning answer.")
    parser.add_argument("question", nargs="+", help="Plain English TY planning question")
    args = parser.parse_args()

    question = " ".join(args.question)
    response = answer_question(question)
    if str(response.get("answer_mode", "")).startswith("template_generation"):
        print(str(response["answer"]))
        return
    print(json.dumps(response, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
