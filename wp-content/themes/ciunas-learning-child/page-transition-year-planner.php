<?php
/**
 * Template Name: Transition Year Planner
 * Description: Landing page for the embedded Transition Year planning tool.
 */

if (!defined('ABSPATH')) {
    exit;
}

$planner_iframe_url = ciunas_ty_planner_url();
$planner_fallback_url = preg_replace('/([?&])embed_mode=1(&?)/', '$1', $planner_iframe_url);
$planner_fallback_url = rtrim((string) $planner_fallback_url, '?&');
if ($planner_fallback_url === '') {
    $planner_fallback_url = $planner_iframe_url;
}

ciunas_page_start('ciunas-page ciunas-ty-planner-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <?php require get_stylesheet_directory() . '/ty-planner/template.php'; ?>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
