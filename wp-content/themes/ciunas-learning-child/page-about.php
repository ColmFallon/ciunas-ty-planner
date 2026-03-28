<?php
/**
 * About page template.
 * Template Name: About Page
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <section class="ciunas-section">
            <h1 class="ciunas-page-title">About</h1>
            <div class="ciunas-about-grid">
                <div class="ciunas-author-image-wrap">
                    <img class="author-photo" src="<?php echo esc_url(get_stylesheet_directory_uri() . '/assets/img/profile-placeholder.jpg'); ?>" alt="Portrait of Colm Fallon" loading="lazy">
                </div>
                <div>
                    <p><strong>Colm Fallon</strong> is a physicist, educator, and founder of Ci&uacute;nas Learning. He holds a PhD in physics and has spent the past decade exploring the intersection of science, education, and human development.</p>
                    <p>He has spoken at national education conferences, corporate education events, and schools across Ireland on mindset, resilience, formation, and the implications of artificial intelligence for education.</p>
                    <p>His work brings together scientific clarity and philosophical reflection, with a focus on helping young people develop judgment, direction, and steadiness in a rapidly changing world.</p>
                    <p>He is the author of <em>The Climb and the Return</em> and <em>AI and the Future of Education</em>, and previously developed the <em>Project One Sky</em> programme for schools.</p>
                    <p>Ci&uacute;nas Learning is an Irish education publisher creating literary, science-informed resources for schools.</p>
                </div>
            </div>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
