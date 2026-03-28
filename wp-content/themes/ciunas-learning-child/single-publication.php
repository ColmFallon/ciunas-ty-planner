<?php
/**
 * Single publication template.
 */

if (!defined('ABSPATH')) {
    exit;
}

ciunas_page_start('ciunas-single-publication');
ciunas_site_header();
?>
<main class="ciunas-main">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
        <?php
        $publication_id = get_the_ID();
        $publication_slug = (string) get_post_field('post_name', $publication_id);
        $meta = ciunas_publication_meta($publication_id);
        $cover_url = ciunas_publication_cover_url($publication_id);
        $status = trim((string) $meta['status']);
        $language = strtoupper(trim((string) $meta['language']));
        $is_unleash = ($publication_slug === 'unleash-your-potential');
        $is_pilot_available = (strcasecmp($status, 'Pilot Available') === 0);
        $is_irish = ($language === 'GA') || (strpos($publication_slug, '-gaeilge') !== false);

        // Single-page CTA system, aligned with card states.
        if ($is_unleash) {
            $primary_cta_label = 'Order Now — €15.99';
        } elseif ($is_pilot_available) {
            $primary_cta_label = 'Request Pilot Copy';
        } else {
            $primary_cta_label = $is_irish ? 'Cláraigh Spéis' : 'Register Interest';
        }

        $primary_cta_url = $is_unleash ? '#publication-enquiry' : '#publication-interest';
        $sent = isset($_GET['sent']) ? sanitize_text_field((string) $_GET['sent']) : '';
        ?>
        <section class="ciunas-publication-hero-wrap">
            <div class="ciunas-container">
                <div class="ciunas-publication-hero">
                    <div class="ciunas-publication-hero-cover">
                        <?php if ($cover_url !== '') : ?>
                            <img src="<?php echo esc_url($cover_url); ?>" alt="<?php echo esc_attr(get_the_title() . ' cover'); ?>" loading="eager">
                        <?php endif; ?>
                    </div>
                    <div class="ciunas-publication-hero-content">
                        <div class="ciunas-badge-row">
                            <?php if ($meta['language'] !== '') : ?>
                                <span class="ciunas-badge"><?php echo esc_html($meta['language']); ?></span>
                            <?php endif; ?>
                            <?php if ($meta['status'] !== '') : ?>
                                <span class="ciunas-badge ciunas-badge-status"><?php echo esc_html($meta['status']); ?></span>
                            <?php endif; ?>
                        </div>
                        <h1 class="ciunas-page-title"><?php the_title(); ?></h1>
                        <?php if ($meta['hero_subtitle'] !== '') : ?>
                            <p class="ciunas-lead"><?php echo esc_html($meta['hero_subtitle']); ?></p>
                        <?php endif; ?>
                        <p class="ciunas-feature-line">Includes Teacher&rsquo;s Booklet</p>
                        <p>
                            <a class="ciunas-button primary" href="<?php echo esc_url($primary_cta_url); ?>"><?php echo esc_html($primary_cta_label); ?></a>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <div class="ciunas-container">
            <section class="ciunas-section ciunas-divider">
                <div class="ciunas-content-prose">
                    <?php the_content(); ?>
                </div>
            </section>

            <?php if ($is_unleash) : ?>
                <section class="ciunas-section ciunas-divider" id="publication-enquiry">
                    <h2>Order / Request</h2>
                    <p>Use this form to order copies or request school rollout information.</p>

                    <?php if ($sent === '1') : ?>
                        <p class="ciunas-form-message ciunas-form-success">Thanks. Your message has been sent successfully.</p>
                    <?php elseif ($sent === '0') : ?>
                        <p class="ciunas-form-message ciunas-form-error">Your message could not be sent. Please review your details and try again.</p>
                    <?php endif; ?>

                    <form class="ciunas-publication-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <input type="hidden" name="action" value="ciunas_publication_enquiry">
                        <input type="hidden" name="publication_id" value="<?php echo esc_attr((string) $publication_id); ?>">
                        <?php wp_nonce_field('ciunas_publication_enquiry_' . $publication_id, 'ciunas_publication_nonce'); ?>

                        <div class="ciunas-form-grid">
                            <div class="ciunas-form-field">
                                <label for="ciunas-name">Name</label>
                                <input id="ciunas-name" type="text" name="name" required>
                            </div>

                            <div class="ciunas-form-field">
                                <label for="ciunas-email">Email</label>
                                <input id="ciunas-email" type="email" name="email" required>
                            </div>

                            <div class="ciunas-form-field">
                                <label for="ciunas-school">School (optional)</label>
                                <input id="ciunas-school" type="text" name="school">
                            </div>

                            <div class="ciunas-form-field ciunas-form-field-full">
                                <label for="ciunas-message">Message (optional)</label>
                                <textarea id="ciunas-message" name="message" rows="6"></textarea>
                            </div>
                        </div>

                        <div class="ciunas-honeypot" aria-hidden="true">
                            <label for="ciunas-company">Company</label>
                            <input id="ciunas-company" type="text" name="company_name" tabindex="-1" autocomplete="off">
                        </div>

                        <div class="ciunas-form-actions">
                            <button class="ciunas-button primary" type="submit">Send</button>
                        </div>
                    </form>
                </section>
            <?php else : ?>
                <section class="ciunas-section ciunas-divider" id="publication-interest">
                    <h2>Register interest</h2>
                    <p>Register your school&rsquo;s interest for updates on pilot copies, rollout timing, and availability.</p>
                    <p>
                        <a class="ciunas-button primary" href="#publication-interest-form"><?php echo esc_html($primary_cta_label); ?></a>
                        <a class="ciunas-button" href="<?php echo esc_url('mailto:' . CIUNAS_CONTACT_EMAIL . '?subject=' . rawurlencode('Publication interest: ' . get_the_title($publication_id))); ?>">Email directly</a>
                    </p>

                    <?php if ($sent === '1') : ?>
                        <p class="ciunas-form-message ciunas-form-success">Thanks. Your message has been sent successfully.</p>
                    <?php elseif ($sent === '0') : ?>
                        <p class="ciunas-form-message ciunas-form-error">Your message could not be sent. Please review your details and try again.</p>
                    <?php endif; ?>
                </section>

                <section class="ciunas-section" id="publication-interest-form">
                    <h2>Interest form</h2>
                    <form class="ciunas-publication-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <input type="hidden" name="action" value="ciunas_publication_enquiry">
                        <input type="hidden" name="publication_id" value="<?php echo esc_attr((string) $publication_id); ?>">
                        <?php wp_nonce_field('ciunas_publication_enquiry_' . $publication_id, 'ciunas_publication_nonce'); ?>

                        <div class="ciunas-form-grid">
                            <div class="ciunas-form-field">
                                <label for="ciunas-name">Name</label>
                                <input id="ciunas-name" type="text" name="name" required>
                            </div>

                            <div class="ciunas-form-field">
                                <label for="ciunas-email">Email</label>
                                <input id="ciunas-email" type="email" name="email" required>
                            </div>

                            <div class="ciunas-form-field">
                                <label for="ciunas-school">School (optional)</label>
                                <input id="ciunas-school" type="text" name="school">
                            </div>

                            <div class="ciunas-form-field ciunas-form-field-full">
                                <label for="ciunas-message">Message</label>
                                <textarea id="ciunas-message" name="message" rows="6" placeholder="Tell us your class year group, expected numbers, or preferred rollout timeline."></textarea>
                            </div>
                        </div>

                        <div class="ciunas-honeypot" aria-hidden="true">
                            <label for="ciunas-company">Company</label>
                            <input id="ciunas-company" type="text" name="company_name" tabindex="-1" autocomplete="off">
                        </div>

                        <div class="ciunas-form-actions">
                            <button class="ciunas-button primary" type="submit"><?php echo esc_html($primary_cta_label); ?></button>
                        </div>
                    </form>
                </section>
            <?php endif; ?>

            <?php if ($meta['sample_chapter'] !== '') : ?>
                <section class="ciunas-section ciunas-divider">
                    <h2>Sample chapter</h2>
                    <p>
                        <a class="ciunas-button" href="<?php echo esc_url($meta['sample_chapter']); ?>">Download sample chapter</a>
                    </p>
                </section>
            <?php endif; ?>
        </div>
    <?php endwhile; endif; ?>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
