<?php
/**
 * Archive template fallback.
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
            <h1 class="ciunas-page-title"><?php echo esc_html(get_the_archive_title()); ?></h1>
            <?php if (have_posts()) : ?>
                <div class="ciunas-post-list">
                    <?php while (have_posts()) : the_post(); ?>
                        <article class="ciunas-post-card">
                            <span class="ciunas-year"><?php echo esc_html(get_the_date('Y')); ?></span>
                            <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                            <p><?php echo esc_html(wp_trim_words(get_the_excerpt(), 28)); ?></p>
                            <p><a href="<?php the_permalink(); ?>">Read essay</a></p>
                        </article>
                    <?php endwhile; ?>
                </div>
            <?php else : ?>
                <p class="ciunas-empty">No posts found.</p>
            <?php endif; ?>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
