<?php
/**
 * Publications page template.
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-page');
ciunas_site_header();

$publications = new WP_Query(
    array(
        'post_type'      => 'publication',
        'posts_per_page' => 5,
        'orderby'        => array('menu_order' => 'ASC', 'date' => 'ASC'),
    )
);
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <section class="ciunas-section">
            <h1 class="ciunas-page-title">Publications</h1>
            <p>Ciúnas Learning publishes research-informed classroom resources for Irish secondary schools.</p>
            <p>Each title includes a dedicated Teacher&rsquo;s Booklet with structured lesson guidance, discussion prompts, and implementation notes.</p>
            <p>Our titles are practical in implementation, grounded in school experience, and designed to support maturity, judgment, and purposeful action in Transition Year.</p>

            <h2>Current Titles</h2>
            <p>Unleash Your Potential<br>A classroom-ready Transition Year workbook based on the original Project One Sky course. It is supported by ten video resources and guides students through structured reflection, disciplined habits, and steady decision-making.<br>Available now — €15.99.</p>
            <p>The Climb and the Return (English Edition)<br>A structured formation programme for Transition Year students, guiding them through resilience, moral clarity, and deliberate practice.<br>Pilot copies available now.</p>

            <h2>Forthcoming and Pilot Editions</h2>
            <p>An Dreapadh agus an Fill (Irish Edition)<br>Irish-language edition of The Climb and the Return.<br>Pilot available from April 2026.</p>
            <p>AI and the Future of Education (English Edition)<br>A practical school workbook helping students evaluate AI tools with discernment, strengthen agency, and protect deep learning in everyday study.<br>Pilot available from April 2026.</p>
            <p>Intleacht Shaorga agus Todhchaí an Oideachais (Irish Edition)<br>Irish-language edition of AI and the Future of Education.<br>Pilot available from April 2026.</p>

            <h2>Pilot and Release Timeline</h2>
            <p>• Available now: Unleash Your Potential</p>
            <p>• Pilot available now: The Climb and the Return (English)</p>
            <p>• Pilot from April 2026: Irish edition of The Climb and the Return; AI and the Future of Education (English and Irish)</p>
            <p>• A sample chapter is available upon request for April 2026 titles.</p>
        </section>

        <section class="ciunas-section ciunas-divider" aria-label="Publication index">
            <?php if ($publications->have_posts()) : ?>
                <div class="ciunas-publications ciunas-publications-five">
                    <?php while ($publications->have_posts()) : $publications->the_post(); ?>
                        <?php
                        $publication_id = get_the_ID();
                        $meta = ciunas_publication_meta($publication_id);
                        $cover_url = ciunas_publication_cover_url($publication_id);
                        $cta_url = $meta['cta_url'] !== '' ? $meta['cta_url'] : get_permalink($publication_id);

                        if (strpos($cta_url, 'http') !== 0) {
                            $cta_url = home_url($cta_url);
                        }
                        ?>
                        <article class="ciunas-card ciunas-publication-card">
                            <?php if ($cover_url !== '') : ?>
                                <img src="<?php echo esc_url($cover_url); ?>" alt="<?php echo esc_attr(get_the_title() . ' cover'); ?>" loading="lazy">
                            <?php endif; ?>
                            <div class="ciunas-badge-row">
                                <?php if ($meta['language'] !== '') : ?>
                                    <span class="ciunas-badge"><?php echo esc_html($meta['language']); ?></span>
                                <?php endif; ?>
                                <?php if ($meta['status'] !== '') : ?>
                                    <span class="ciunas-badge ciunas-badge-status"><?php echo esc_html($meta['status']); ?></span>
                                <?php endif; ?>
                            </div>
                            <h2 class="ciunas-publication-title"><?php the_title(); ?></h2>
                            <p class="ciunas-publication-summary"><?php echo esc_html(wp_trim_words(get_the_excerpt(), 25)); ?></p>
                            <div class="ciunas-actions ciunas-card-cta">
                                <a class="ciunas-button primary" href="<?php echo esc_url($cta_url); ?>"><?php echo esc_html($meta['cta_label'] !== '' ? $meta['cta_label'] : 'Learn More'); ?></a>
                                <a class="ciunas-button" href="<?php the_permalink(); ?>">View Details</a>
                            </div>
                        </article>
                    <?php endwhile; wp_reset_postdata(); ?>
                </div>
            <?php else : ?>
                <p class="ciunas-empty">No publications found.</p>
            <?php endif; ?>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
