<?php
/**
 * Default page template.
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <section class="ciunas-section">
                <article <?php post_class(); ?>>
                    <h1 class="ciunas-page-title"><?php the_title(); ?></h1>
                    <div class="ciunas-content-prose">
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
