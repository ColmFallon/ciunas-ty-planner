<?php
/**
 * Template Name: Resources Page
 * Description: Teacher resources and sample chapter request form.
 */

if (!defined('ABSPATH')) {
    exit;
}

$public_resources = ciunas_resources_by_type('public');
$gated_resources = ciunas_resources_by_type('gated');
$form_status = isset($_GET['sent']) ? sanitize_text_field((string) $_GET['sent']) : '';

ciunas_page_start('ciunas-page ciunas-resources-page');
ciunas_site_header();
?>
<main class="ciunas-main">
    <div class="ciunas-container">
        <section class="ciunas-section">
            <h1 class="ciunas-page-title">Resources for Teachers</h1>
            <p>Ciúnas Learning provides practical materials to help teachers evaluate programmes, preview sample content, and plan classroom implementation.</p>
            <p>These resources are designed to support informed adoption, pilot planning, and structured delivery in Transition Year.</p>
        </section>

        <section class="ciunas-section ciunas-divider">
            <div class="ciunas-resource-section-head">
                <div>
                    <h2>Programme Materials for The Climb and the Return</h2>
                    <p>Download the programme overview and Transition Year scheme of work for The Climb and the Return and An Dreapadh agus an Fill.</p>
                </div>
            </div>

            <div class="ciunas-resource-grid">
                <?php foreach ($public_resources as $resource) : ?>
                    <?php if (empty($resource['exists'])) { continue; } ?>
                    <article class="ciunas-card ciunas-resource-card">
                        <h3><?php echo esc_html($resource['label']); ?></h3>
                        <p>PDF download</p>
                        <p><a class="ciunas-button primary" href="<?php echo esc_url($resource['url']); ?>" download>Download PDF</a></p>
                    </article>
                <?php endforeach; ?>
            </div>
            <p>Programme materials for AI and the Future of Education and Intleacht Shaorga agus Todhcha&iacute; an Oideachais are in development and will be added separately.</p>
        </section>

        <section class="ciunas-section ciunas-divider">
            <div class="ciunas-resource-section-head">
                <div>
                    <h2>Sample Chapters</h2>
                    <p>Sample chapters and handbook extracts are available on request. Please enter your details below and the download links will be sent automatically by email.</p>
                </div>
            </div>

            <div class="ciunas-resource-request-wrap">
                <div class="ciunas-card ciunas-resource-card">
                    <h3>Included in the sample pack</h3>
                    <ul class="ciunas-bullet-list">
                        <?php foreach ($gated_resources as $resource) : ?>
                            <?php if (empty($resource['exists'])) { continue; } ?>
                            <li><?php echo esc_html($resource['label']); ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>

                <div class="ciunas-card ciunas-resource-form-card">
                    <?php if ($form_status === '1') : ?>
                        <p class="ciunas-form-message ciunas-form-success"><?php echo esc_html(ciunas_resources_success_message()); ?></p>
                    <?php elseif ($form_status === '0') : ?>
                        <p class="ciunas-form-message ciunas-form-error">There was a problem sending your request. Please check your details and try again.</p>
                    <?php endif; ?>

                    <form class="ciunas-publication-form" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" method="post">
                        <input type="hidden" name="action" value="ciunas_resource_request">
                        <?php wp_nonce_field('ciunas_resources_request', 'ciunas_resources_nonce'); ?>
                        <input type="hidden" name="requested_pack" value="<?php echo esc_attr(ciunas_sample_pack_label()); ?>">

                        <div class="ciunas-form-grid">
                            <div class="ciunas-form-field">
                                <label for="ciunas-resource-name">Name</label>
                                <input id="ciunas-resource-name" name="name" type="text" required>
                            </div>
                            <div class="ciunas-form-field">
                                <label for="ciunas-resource-email">Email</label>
                                <input id="ciunas-resource-email" name="email" type="email" required>
                            </div>
                            <div class="ciunas-form-field ciunas-form-field-full">
                                <label for="ciunas-resource-school">School / Organisation</label>
                                <input id="ciunas-resource-school" name="school" type="text">
                            </div>
                        </div>

                        <div class="ciunas-honeypot" aria-hidden="true">
                            <label for="ciunas-resource-website">Website</label>
                            <input id="ciunas-resource-website" name="website" type="text" tabindex="-1" autocomplete="off">
                        </div>

                        <div class="ciunas-form-actions">
                            <button class="ciunas-button primary" type="submit">Request Sample Chapters</button>
                        </div>
                    </form>
                </div>
            </div>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
