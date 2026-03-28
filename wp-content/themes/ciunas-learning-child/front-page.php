<?php
/**
 * Front page template.
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-home');
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
        <section class="ciunas-hero ciunas-section" aria-labelledby="hero-title">
            <h1 id="hero-title">Ci&uacute;nas Learning</h1>
            <p>Ci&uacute;nas Learning develops reflective, science-informed school resources that help students build judgment, steadiness, and purposeful action.</p>
            <p class="ciunas-lead">Our publications are designed for practical classroom delivery and long-term formation in Irish secondary schools.</p>
            <div class="ciunas-actions">
                <a class="ciunas-button primary" href="<?php echo esc_url(home_url('/publications/')); ?>">Explore Publications</a>
                <a class="ciunas-button" href="<?php echo esc_url(home_url('/contact/')); ?>">Contact</a>
            </div>
        </section>

        <section class="ciunas-section ciunas-divider" aria-labelledby="publications-title">
            <h2 id="publications-title">Publications</h2>
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
                            <h3 class="ciunas-publication-title"><?php the_title(); ?></h3>
                            <p class="ciunas-publication-summary"><?php echo esc_html(wp_trim_words(get_the_excerpt(), 25)); ?></p>
                            <div class="ciunas-actions ciunas-card-cta">
                                <a class="ciunas-button primary" href="<?php echo esc_url($cta_url); ?>"><?php echo esc_html($meta['cta_label'] !== '' ? $meta['cta_label'] : 'Learn More'); ?></a>
                                <a class="ciunas-button" href="<?php the_permalink(); ?>">Details</a>
                            </div>
                        </article>
                    <?php endwhile; wp_reset_postdata(); ?>
                </div>
            <?php else : ?>
                <p class="ciunas-empty">Publication cards will appear here after sync.</p>
            <?php endif; ?>
        </section>

        <section class="ciunas-section" aria-labelledby="matters-title">
            <h2 id="matters-title" class="ciunas-muted-heading">Why This Work Matters</h2>
            <p class="ciunas-callout">As expectations rise and technologies accelerate, education faces a deeper question than performance alone. What forms steadiness, judgment, and direction in young people? Ci&uacute;nas Learning exists to support that formation calmly, practically, and in partnership with teachers.</p>
        </section>

        <section class="ciunas-section ciunas-schools" aria-labelledby="schools-title">
            <h2 id="schools-title">For Schools</h2>
            <ul>
                <li>English and Irish editions</li>
                <li>Pilot copies available now</li>
                <li>Classroom-ready rollouts through 2026</li>
                <li>School partnership support available</li>
            </ul>
            <a class="ciunas-button primary" href="<?php echo esc_url(home_url('/contact/')); ?>">Enquire About Pilot Copies</a>
        </section>

        <section class="ciunas-section" aria-labelledby="writing-title">
            <h2 id="writing-title">Writing</h2>
            <p>Essays on education, formation, artificial intelligence, and the conditions that help young people grow in steadiness and judgment.</p>
            <div class="ciunas-writing-grid">
                <?php
                $writing_posts = new WP_Query(
                    array(
                        'post_type'           => 'post',
                        'posts_per_page'      => 3,
                        'ignore_sticky_posts' => true,
                    )
                );

                if ($writing_posts->have_posts()) :
                    while ($writing_posts->have_posts()) :
                        $writing_posts->the_post();
                        ?>
                        <article class="ciunas-writing-item">
                            <?php if (has_post_thumbnail()) : ?>
                                <a class="ciunas-writing-item-image" href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('large', array('loading' => 'lazy')); ?>
                                </a>
                            <?php endif; ?>
                            <span class="ciunas-year"><?php echo esc_html(get_the_date('Y')); ?></span>
                            <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                            <p><?php echo esc_html(wp_trim_words(get_the_excerpt(), 22)); ?></p>
                        </article>
                        <?php
                    endwhile;
                    wp_reset_postdata();
                else :
                    ?>
                    <p class="ciunas-empty">Writing pieces will appear here shortly.</p>
                    <?php
                endif;
                ?>
            </div>
            <p><a class="ciunas-button" href="<?php echo esc_url(home_url('/writing/')); ?>">View All Writing</a></p>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
