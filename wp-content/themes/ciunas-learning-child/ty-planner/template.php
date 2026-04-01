<?php
/**
 * TY planner landing page module.
 *
 * Expected variables:
 * - $planner_iframe_url
 * - $planner_fallback_url
 */

if (!defined('ABSPATH')) {
    exit;
}

$planner_iframe_url = isset($planner_iframe_url) ? (string) $planner_iframe_url : '';
$planner_fallback_url = isset($planner_fallback_url) ? (string) $planner_fallback_url : $planner_iframe_url;
?>
<section class="ciunas-hero ciunas-section ciunas-ty-planner-hero">
    <h1>Transition Year Planning Tool</h1>
    <p>Generate a complete Transition Year plan in minutes &mdash; in English or Irish.</p>
    <p class="ciunas-lead">Create a structured TY annual plan tailored to your school context, ready to download and adapt.</p>
    <div class="ciunas-actions">
        <a class="ciunas-button primary" href="#ty-planner-tool">Try the Tool</a>
    </div>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-value">
    <div class="ciunas-ty-planner-copy">
        <h2>What this is</h2>
        <p>This tool is designed to support TY coordinators and school leaders in planning a clear, structured, and realistic Transition Year programme.</p>
        <p>It provides a strong first draft that can be adapted to suit your school&rsquo;s context, priorities, and available resources.</p>
        <p>Whether you are starting from scratch or refining an existing programme, it helps reduce the time spent on planning while keeping the focus on meaningful student development.</p>
    </div>
    <ul class="ciunas-bullet-list ciunas-ty-planner-bullets">
        <li>Create a full TY annual plan</li>
        <li>Adapt it to your school (DEIS, Gaelscoil, rural, etc.)</li>
        <li>Download in Word or PDF</li>
        <li>Designed for Irish secondary schools</li>
    </ul>
</section>

<section class="ciunas-section ciunas-divider">
    <div class="ciunas-ty-planner-copy">
        <h2>Who it&rsquo;s for</h2>
    </div>
    <ul class="ciunas-bullet-list ciunas-ty-planner-bullets">
        <li>TY Coordinators</li>
        <li>School leadership teams</li>
        <li>Teachers involved in TY planning</li>
        <li>Schools reviewing or updating their TY programme</li>
    </ul>
</section>

<section class="ciunas-section ciunas-divider">
    <div class="ciunas-ty-planner-copy">
        <h2>Built for Irish schools</h2>
        <p>The tool reflects the structure, language, and expectations of Transition Year in Irish secondary schools.</p>
        <p>It supports:</p>
    </div>
    <ul class="ciunas-bullet-list ciunas-ty-planner-bullets">
        <li>English and Irish language outputs</li>
        <li>Common school contexts (DEIS, Gaelscoil, rural, etc.)</li>
        <li>Practical classroom delivery and planning realities</li>
    </ul>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-tool-wrap" id="ty-planner-tool">
    <div class="ciunas-ty-planner-copy ciunas-ty-planner-section-head">
        <h2>Try the Tool</h2>
        <p>Generate a complete TY annual plan in minutes, then download and adapt it for your school.</p>
    </div>

    <div class="ciunas-ty-planner-embed-shell">
        <iframe
            class="ciunas-ty-planner-frame"
            src="<?php echo esc_url($planner_iframe_url); ?>"
            title="Transition Year Planning Tool"
            loading="lazy"
            allow="clipboard-write; fullscreen"
            width="100%"
            height="900"
            style="border: none;"
        ></iframe>
    </div>

    <?php if ($planner_fallback_url !== '') : ?>
        <p class="ciunas-ty-planner-fallback">
            If the tool does not load, you can open it directly here:
            <a href="<?php echo esc_url($planner_fallback_url); ?>" target="_blank" rel="noopener">Open the tool</a>.
        </p>
    <?php endif; ?>
</section>

<section class="ciunas-section ciunas-divider">
    <div class="ciunas-ty-planner-copy">
        <h2>New: Experience Mapping (coming next)</h2>
        <p>You will also be able to generate TY Experience records aligned to Oide requirements &mdash; helping to document workshops, trips, and activities across the four student dimensions.</p>
    </div>
</section>

<section class="ciunas-section ciunas-divider">
    <div class="ciunas-ty-planner-copy">
        <h2>About Ciunas Learning</h2>
        <p>Ciunas Learning develops reflective, science-informed school resources that support long-term student development.</p>
        <p>This tool has been developed as part of that work with schools and teachers.</p>
        <p class="ciunas-ty-planner-note">If you try the tool, I&rsquo;d really value your feedback &mdash; even a short reaction helps improve it for schools.</p>
    </div>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-cta">
    <h2>Ready to try it?</h2>
    <div class="ciunas-actions">
        <a class="ciunas-button primary" href="#ty-planner-tool">Try the Tool</a>
    </div>
</section>
