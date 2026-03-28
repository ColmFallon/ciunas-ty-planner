<?php
/**
 * Writing archive page template.
 * Template Name: Writing Page
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-page ciunas-writing-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <section class="ciunas-section">
            <h1 class="ciunas-page-title">Writing</h1>
            <p>Essays on education, formation, resilience, and artificial intelligence in school life.</p>
            <p>The writing style is measured, practical, and teacher-facing: clear enough for implementation, reflective enough to support good judgment.</p>

            <h2>Editorial Focus</h2>
            <ul>
                <li>Formation over performance in education</li>
                <li>Character, responsibility, and maturity in Transition Year</li>
                <li>Evidence-informed formation in Irish school contexts</li>
                <li>AI, abundance, and what cannot be outsourced</li>
            </ul>

            <div class="ciunas-post-list">
                <?php
                $posts_query = new WP_Query(
                    array(
                        'post_type'           => 'post',
                        'posts_per_page'      => 12,
                        'paged'               => max(1, get_query_var('paged')),
                        'ignore_sticky_posts' => true,
                    )
                );

                if ($posts_query->have_posts()) :
                    while ($posts_query->have_posts()) :
                        $posts_query->the_post();
                        ?>
                        <article class="ciunas-post-card">
                            <?php if (has_post_thumbnail()) : ?>
                                <a class="ciunas-post-card-image" href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('large', array('loading' => 'lazy')); ?>
                                </a>
                            <?php endif; ?>
                            <span class="ciunas-year"><?php echo esc_html(get_the_date('Y')); ?></span>
                            <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                            <p><?php echo esc_html(wp_trim_words(get_the_excerpt(), 28)); ?></p>
                            <p><a href="<?php the_permalink(); ?>">Read essay</a></p>
                        </article>
                        <?php
                    endwhile;
                    wp_reset_postdata();
                else :
                    ?>
                    <p class="ciunas-empty">No essays are published yet.</p>
                    <?php
                endif;
                ?>
            </div>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
