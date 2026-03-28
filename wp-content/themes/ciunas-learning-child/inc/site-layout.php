<?php
/**
 * Shared layout helpers for Ciunas page templates.
 */

if (!defined('ABSPATH')) {
    exit;
}

function ciunas_page_start(string $extra_class = ''): void
{
    ?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class($extra_class); ?>>
<?php wp_body_open(); ?>
<?php
}

function ciunas_primary_nav_markup(): void
{
    if (has_nav_menu('primary')) {
        wp_nav_menu(
            array(
                'theme_location' => 'primary',
                'container'      => false,
                'menu_class'     => 'ciunas-nav-list',
                'fallback_cb'    => false,
            )
        );
        return;
    }

    echo '<ul class="ciunas-nav-list">';
    echo '<li><a href="' . esc_url(home_url('/')) . '">Home</a></li>';
    echo '<li><a href="' . esc_url(home_url('/publications/')) . '">Publications</a></li>';
    echo '<li><a href="' . esc_url(home_url('/resources/')) . '">Resources</a></li>';
    echo '<li><a href="' . esc_url(home_url('/speaking/')) . '">Speaking</a></li>';
    echo '<li><a href="' . esc_url(home_url('/writing/')) . '">Writing</a></li>';
    echo '<li><a href="' . esc_url(home_url('/about/')) . '">About</a></li>';
    echo '<li><a href="' . esc_url(home_url('/contact/')) . '">Contact</a></li>';
    echo '</ul>';
}

function ciunas_site_header(): void
{
    ?>
    <header class="ciunas-site-header">
        <div class="ciunas-container ciunas-header-inner">
            <a class="ciunas-wordmark" href="<?php echo esc_url(home_url('/')); ?>">Ci&uacute;nas Learning</a>
            <nav class="ciunas-nav" aria-label="Primary navigation">
                <?php ciunas_primary_nav_markup(); ?>
            </nav>
        </div>
    </header>
    <?php
}

function ciunas_footer_nav_markup(): void
{
    if (has_nav_menu('footer')) {
        wp_nav_menu(
            array(
                'theme_location' => 'footer',
                'container'      => false,
                'menu_class'     => 'ciunas-footer-nav',
                'fallback_cb'    => false,
            )
        );
        return;
    }

    echo '<ul class="ciunas-footer-nav">';
    echo '<li><a href="' . esc_url(home_url('/')) . '">Home</a></li>';
    echo '<li><a href="' . esc_url(home_url('/publications/')) . '">Publications</a></li>';
    echo '<li><a href="' . esc_url(home_url('/resources/')) . '">Resources</a></li>';
    echo '<li><a href="' . esc_url(home_url('/speaking/')) . '">Speaking</a></li>';
    echo '<li><a href="' . esc_url(home_url('/writing/')) . '">Writing</a></li>';
    echo '<li><a href="' . esc_url(home_url('/about/')) . '">About</a></li>';
    echo '<li><a href="' . esc_url(home_url('/contact/')) . '">Contact</a></li>';
    echo '</ul>';
}

function ciunas_site_footer(): void
{
    ?>
    <footer class="ciunas-site-footer">
        <div class="ciunas-container ciunas-footer-inner">
            <div>
                <p class="ciunas-footer-title">Ci&uacute;nas Learning</p>
                <p>Ireland</p>
                <p><a href="mailto:colm@ciunaslearning.com">colm@ciunaslearning.com</a></p>
            </div>
            <nav aria-label="Footer navigation">
                <?php ciunas_footer_nav_markup(); ?>
            </nav>
        </div>
    </footer>
    <?php
}

function ciunas_page_end(): void
{
    wp_footer();
    echo '</body></html>';
}
