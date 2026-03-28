<?php
/**
 * Single post template.
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-single');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <section class="ciunas-section">
                <article <?php post_class(); ?>>
                    <header class="entry-header">
                        <span class="ciunas-year"><?php echo esc_html(get_the_date('Y')); ?></span>
                        <h1 class="entry-title"><?php the_title(); ?></h1>
                    </header>
                    <?php if (has_post_thumbnail()) : ?>
                        <figure class="ciunas-post-featured-image">
                            <?php the_post_thumbnail('full', array('loading' => 'eager')); ?>
                        </figure>
                    <?php endif; ?>
                    <div class="entry-content">
                        <?php the_content(); ?>
                    </div>
                </article>
            </section>
        <?php endwhile; endif; ?>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
