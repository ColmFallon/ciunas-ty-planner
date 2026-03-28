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
    <h1>Plan your Transition Year in minutes</h1>
    <p>Generate a structured TY annual plan in English or Irish &mdash; ready to edit, share, and use in your school.</p>
    <div class="ciunas-actions">
        <a class="ciunas-button primary" href="#ty-planner-tool">Generate your TY plan</a>
    </div>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-value">
    <div class="ciunas-ty-planner-copy">
        <h2>A simple way to start your TY planning</h2>
        <p>Planning Transition Year can be time-consuming and difficult to structure. This tool gives you a clear, professional starting point in minutes.</p>
    </div>
    <ul class="ciunas-bullet-list ciunas-ty-planner-bullets">
        <li>Create a full TY annual plan</li>
        <li>Adapt it to your school context</li>
        <li>Download and edit immediately</li>
        <li>Works in English and Irish</li>
    </ul>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-tool-wrap" id="ty-planner-tool">
    <div class="ciunas-ty-planner-copy ciunas-ty-planner-section-head">
        <h2>Generate your TY annual plan</h2>
        <p>You can enter your own context or simply generate a plan and improve it afterwards.</p>
    </div>

    <div class="ciunas-ty-planner-embed-shell">
        <iframe
            class="ciunas-ty-planner-frame"
            src="<?php echo esc_url($planner_iframe_url); ?>"
            title="Transition Year Planning Tool"
            loading="lazy"
            allow="clipboard-write"
        ></iframe>
    </div>

    <?php if ($planner_fallback_url !== '') : ?>
        <p class="ciunas-ty-planner-fallback">
            If the planner does not load properly here, <a href="<?php echo esc_url($planner_fallback_url); ?>" target="_blank" rel="noopener">open it in a new tab</a>.
        </p>
    <?php endif; ?>
</section>

<section class="ciunas-section ciunas-divider ciunas-ty-planner-cta">
    <h2>Start your TY planning today</h2>
    <div class="ciunas-actions">
        <a class="ciunas-button primary" href="#ty-planner-tool">Generate your TY plan</a>
    </div>
</section>
