<?php
/**
 * Template Name: Publication Page
 * Description: Reusable publication detail page template.
 */

if (!defined('ABSPATH')) {
    exit;
}

function ciunas_publication_cover_by_slug(string $slug): array
{
    $base = get_stylesheet_directory_uri() . '/assets/img/covers/';
    $map = array(
        'the-climb-and-the-return' => array(
            'webp' => $base . 'climb_cover_front.webp',
            'jpg'  => $base . 'climb_cover_front.jpg',
            'alt'  => 'The Climb and the Return cover',
        ),
        'ai-and-the-future-of-education' => array(
            'webp' => $base . 'ai_future_cover_front.webp',
            'jpg'  => $base . 'ai_future_cover_front.jpg',
            'alt'  => 'AI and the Future of Education cover',
        ),
        'unleash-your-potential' => array(
            'webp' => $base . 'unleash_cover_front.webp',
            'jpg'  => $base . 'unleash_cover_front.jpg',
            'alt'  => 'Unleash Your Potential cover',
        ),
    );

    if (isset($map[$slug])) {
        return $map[$slug];
    }

    return array(
        'webp' => $base . 'climb_cover_front.webp',
        'jpg'  => $base . 'climb_cover_front.jpg',
        'alt'  => 'Publication cover',
    );
}

ciunas_page_start('ciunas-page ciunas-publication-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <?php
            $page_slug = get_post_field('post_name', get_the_ID());
            $cover = ciunas_publication_cover_by_slug($page_slug);

            $meta_cover_webp = get_post_meta(get_the_ID(), 'ciunas_cover_webp', true);
            $meta_cover_jpg = get_post_meta(get_the_ID(), 'ciunas_cover_jpg', true);
            $blurb = get_post_meta(get_the_ID(), 'ciunas_blurb', true);
            $students_do_raw = get_post_meta(get_the_ID(), 'ciunas_students_do', true);
            $teacher_guide_url = get_post_meta(get_the_ID(), 'ciunas_teacher_guide_url', true);

            if (!empty($meta_cover_webp)) {
                $cover['webp'] = esc_url_raw($meta_cover_webp);
            }
            if (!empty($meta_cover_jpg)) {
                $cover['jpg'] = esc_url_raw($meta_cover_jpg);
            }

            if (empty($blurb)) {
                $blurb = get_the_excerpt();
            }
            if (empty($blurb)) {
                $blurb = 'Reflective, classroom-ready material designed for thoughtful use in Irish secondary schools.';
            }

            $students_do = array();
            if (!empty($students_do_raw)) {
                $students_do = array_filter(array_map('trim', preg_split('/\r\n|\r|\n/', $students_do_raw)));
            }
            if (empty($students_do)) {
                $students_do = array(
                    'Reflect on core themes through structured workbook prompts.',
                    'Engage in practical, discussion-based classroom activities.',
                    'Build habits of attention, judgment, and deliberate action.',
                );
            }
            ?>

            <section class="ciunas-section ciunas-publication-hero">
                <div class="ciunas-publication-grid">
                    <picture>
                        <source srcset="<?php echo esc_url($cover['webp']); ?>" type="image/webp">
                        <img src="<?php echo esc_url($cover['jpg']); ?>" alt="<?php echo esc_attr($cover['alt']); ?>" loading="lazy">
                    </picture>
                    <div>
                        <h1 class="ciunas-page-title"><?php the_title(); ?></h1>
                        <p class="ciunas-lead"><?php echo esc_html($blurb); ?></p>
                    </div>
                </div>
            </section>

            <section class="ciunas-section ciunas-divider">
                <h2>Overview</h2>
                <div class="ciunas-content-prose">
                    <?php the_content(); ?>
                </div>
            </section>

            <section class="ciunas-section">
                <h2>What students do</h2>
                <ul class="ciunas-bullet-list">
                    <?php foreach ($students_do as $item) : ?>
                        <li><?php echo esc_html($item); ?></li>
                    <?php endforeach; ?>
                </ul>
            </section>

            <section class="ciunas-section">
                <h2>For schools</h2>
                <ul class="ciunas-bullet-list">
                    <li>English editions: ongoing availability for conference and school adoption</li>
                    <li>Irish editions (The Climb and the Return; AI and the Future of Education): planned availability September 2026</li>
                    <li>Transition Year procurement cycle: schools often select in spring and purchase before end of May for September use</li>
                    <li>Limited school talks available until May 2026</li>
                </ul>
            </section>

            <section class="ciunas-section">
                <h2>Teacher Guide</h2>
                <p>Teacher guide and classroom support downloads will be listed here.</p>
                <p>
                    <a class="ciunas-button" href="<?php echo esc_url(!empty($teacher_guide_url) ? $teacher_guide_url : '#'); ?>">
                        Teacher Guide (Coming Soon)
                    </a>
                </p>
            </section>

            <section class="ciunas-section">
                <a class="ciunas-button primary" href="<?php echo esc_url(home_url('/contact/')); ?>">Enquire about preview copies</a>
            </section>
        <?php endwhile; endif; ?>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
