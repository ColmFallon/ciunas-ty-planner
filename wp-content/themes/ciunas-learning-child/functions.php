<?php
/**
 * Theme setup and utility hooks for Ciunas Learning child theme.
 */

if (!defined('ABSPATH')) {
    exit;
}

require_once get_stylesheet_directory() . '/inc/site-layout.php';
require_once get_stylesheet_directory() . '/inc/resources-content.php';

if (!defined('CIUNAS_CONTACT_EMAIL')) {
    define('CIUNAS_CONTACT_EMAIL', 'colm@ciunaslearning.com');
}

if (!defined('CIUNAS_TY_PLANNER_URL')) {
    define('CIUNAS_TY_PLANNER_URL', 'http://localhost:8501/');
}

function ciunas_ty_planner_url(): string
{
    $default_url = getenv('CIUNAS_TY_PLANNER_URL');

    if (!is_string($default_url) || $default_url === '') {
        $default_url = CIUNAS_TY_PLANNER_URL;
    }

    $planner_url = (string) apply_filters('ciunas_ty_planner_url', $default_url);

    if ($planner_url === '') {
        return '';
    }

    return (string) add_query_arg('embed_mode', '1', $planner_url);
}

/**
 * Load locked publication content from publications.json.
 */
function ciunas_publications_data(): array
{
    static $data = null;

    if ($data !== null) {
        return $data;
    }

    $file = get_stylesheet_directory() . '/publications.json';

    if (!file_exists($file) || !is_readable($file)) {
        $data = array();
        return $data;
    }

    $raw = file_get_contents($file);
    $decoded = json_decode((string) $raw, true);

    $data = is_array($decoded) ? $decoded : array();

    return $data;
}

function ciunas_child_enqueue_styles(): void
{
    $main_css_path = get_stylesheet_directory() . '/assets/css/main.css';
    $main_css_version = file_exists($main_css_path) ? (string) filemtime($main_css_path) : wp_get_theme()->get('Version');

    wp_enqueue_style(
        'twentytwentyfour-style',
        get_template_directory_uri() . '/style.css',
        array(),
        wp_get_theme('twentytwentyfour')->get('Version')
    );

    wp_enqueue_style(
        'ciunas-child-main',
        get_stylesheet_directory_uri() . '/assets/css/main.css',
        array('twentytwentyfour-style'),
        $main_css_version
    );

    if (is_page_template('page-transition-year-planner.php')) {
        $planner_css_path = get_stylesheet_directory() . '/ty-planner/ty-planner.css';
        $planner_css_version = file_exists($planner_css_path) ? (string) filemtime($planner_css_path) : $main_css_version;
        wp_enqueue_style(
            'ciunas-ty-planner',
            get_stylesheet_directory_uri() . '/ty-planner/ty-planner.css',
            array('ciunas-child-main'),
            $planner_css_version
        );
    }
}
add_action('wp_enqueue_scripts', 'ciunas_child_enqueue_styles');

function ciunas_add_favicon_fallback(): void
{
    if (has_site_icon()) {
        return;
    }

    $favicon_uri = trailingslashit(get_stylesheet_directory_uri()) . 'assets/brand/favicon.png';
    echo '<link rel="icon" type="image/png" href="' . esc_url($favicon_uri) . '" sizes="32x32">' . "\n";
    echo '<link rel="apple-touch-icon" href="' . esc_url($favicon_uri) . '">' . "\n";
}
add_action('wp_head', 'ciunas_add_favicon_fallback');

function ciunas_child_theme_setup(): void
{
    add_theme_support('post-thumbnails');

    register_nav_menus(
        array(
            'primary' => __('Primary Menu', 'ciunas-learning-child'),
            'footer'  => __('Footer Menu', 'ciunas-learning-child'),
        )
    );
}
add_action('after_setup_theme', 'ciunas_child_theme_setup');

function ciunas_register_publication_cpt(): void
{
    register_post_type(
        'publication',
        array(
            'labels' => array(
                'name'               => __('Publications', 'ciunas-learning-child'),
                'singular_name'      => __('Publication', 'ciunas-learning-child'),
                'add_new_item'       => __('Add New Publication', 'ciunas-learning-child'),
                'edit_item'          => __('Edit Publication', 'ciunas-learning-child'),
                'new_item'           => __('New Publication', 'ciunas-learning-child'),
                'view_item'          => __('View Publication', 'ciunas-learning-child'),
                'search_items'       => __('Search Publications', 'ciunas-learning-child'),
                'not_found'          => __('No publications found', 'ciunas-learning-child'),
                'not_found_in_trash' => __('No publications found in trash', 'ciunas-learning-child'),
            ),
            'public'             => true,
            'show_in_rest'       => true,
            'supports'           => array('title', 'editor', 'excerpt', 'thumbnail', 'page-attributes'),
            'has_archive'        => false,
            'menu_icon'          => 'dashicons-book',
            'rewrite'            => array('slug' => 'publications', 'with_front' => false),
            'publicly_queryable' => true,
        )
    );
}
add_action('init', 'ciunas_register_publication_cpt');

function ciunas_publication_meta(int $post_id): array
{
    return array(
        'language'         => (string) get_post_meta($post_id, 'ciunas_language', true),
        'status'           => (string) get_post_meta($post_id, 'ciunas_status', true),
        'hero_subtitle'    => (string) get_post_meta($post_id, 'ciunas_hero_subtitle', true),
        'cta_label'        => (string) get_post_meta($post_id, 'ciunas_cta_label', true),
        'cta_url'          => (string) get_post_meta($post_id, 'ciunas_cta_url', true),
        'sample_chapter'   => (string) get_post_meta($post_id, 'ciunas_sample_chapter_url', true),
        'cover_image_path' => (string) get_post_meta($post_id, 'ciunas_cover_image', true),
    );
}

function ciunas_publication_cover_url(int $post_id): string
{
    $path = (string) get_post_meta($post_id, 'ciunas_cover_image', true);

    if ($path === '') {
        return '';
    }

    if (filter_var($path, FILTER_VALIDATE_URL)) {
        return esc_url_raw($path);
    }

    $relative_path = ltrim($path, '/');
    $url = trailingslashit(get_stylesheet_directory_uri()) . $relative_path;
    $file = trailingslashit(get_stylesheet_directory()) . $relative_path;

    if (file_exists($file)) {
        return add_query_arg('v', (string) filemtime($file), $url);
    }

    return $url;
}

function ciunas_sync_publications(): void
{
    $publications = ciunas_publications_data();

    if (empty($publications)) {
        return;
    }

    foreach ($publications as $index => $entry) {
        if (!is_array($entry) || empty($entry['slug']) || empty($entry['title'])) {
            continue;
        }

        $slug = sanitize_title((string) $entry['slug']);
        $existing = get_page_by_path($slug, OBJECT, 'publication');

        $postarr = array(
            'post_type'      => 'publication',
            'post_name'      => $slug,
            'post_title'     => sanitize_text_field((string) $entry['title']),
            'post_excerpt'   => wp_kses_post((string) ($entry['summary'] ?? '')),
            'post_content'   => wpautop(wp_kses_post((string) ($entry['long_description'] ?? ''))),
            'post_status'    => 'publish',
            'menu_order'     => (int) $index,
            'comment_status' => 'closed',
            'ping_status'    => 'closed',
        );

        if ($existing instanceof WP_Post) {
            $postarr['ID'] = (int) $existing->ID;
            $post_id = wp_update_post($postarr, true);
        } else {
            $post_id = wp_insert_post($postarr, true);
        }

        if (is_wp_error($post_id) || !$post_id) {
            continue;
        }

        update_post_meta((int) $post_id, 'ciunas_language', sanitize_text_field((string) ($entry['language'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_status', sanitize_text_field((string) ($entry['status'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_hero_subtitle', sanitize_text_field((string) ($entry['hero_subtitle'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_cta_label', sanitize_text_field((string) ($entry['cta_label'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_cta_url', sanitize_text_field((string) ($entry['cta_url'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_sample_chapter_url', esc_url_raw((string) ($entry['sample_chapter_url'] ?? '')));
        update_post_meta((int) $post_id, 'ciunas_cover_image', sanitize_text_field((string) ($entry['cover_image'] ?? '')));
    }
}

function ciunas_ensure_publications_page(): void
{
    $page = get_page_by_path('publications', OBJECT, 'page');

    $page_args = array(
        'post_title'   => 'Publications',
        'post_name'    => 'publications',
        'post_status'  => 'publish',
        'post_type'    => 'page',
        'post_content' => 'Explore our current publications for schools.',
    );

    if ($page instanceof WP_Post) {
        $page_args['ID'] = (int) $page->ID;
        $page_id = wp_update_post($page_args, true);
    } else {
        $page_id = wp_insert_post($page_args, true);
    }

    if (!is_wp_error($page_id) && $page_id) {
        update_post_meta((int) $page_id, '_wp_page_template', 'page-publications.php');
    }
}

function ciunas_ensure_core_pages(): void
{
    $pages = array(
        'speaking' => array(
            'title'    => 'Speaking',
            'template' => 'page-speaking.php',
            'content'  => 'Speaking enquiries and school talks.',
        ),
        'writing' => array(
            'title'    => 'Writing',
            'template' => 'page-writing.php',
            'content'  => 'Essays and publication updates.',
        ),
        'about' => array(
            'title'    => 'About',
            'template' => 'page-about.php',
            'content'  => 'About Ciúnas Learning.',
        ),
        'contact' => array(
            'title'    => 'Contact',
            'template' => 'page-contact.php',
            'content'  => 'Contact Ciúnas Learning.',
        ),
        'resources' => array(
            'title'    => 'Resources for Teachers',
            'template' => 'page-resources.php',
            'content'  => 'Teacher resources, programme documents, and sample chapter requests.',
        ),
        'transition-year-planner' => array(
            'title'    => 'Transition Year Planner',
            'template' => 'page-transition-year-planner.php',
            'content'  => 'Plan your Transition Year in minutes.',
        ),
    );

    foreach ($pages as $slug => $spec) {
        $page = get_page_by_path($slug, OBJECT, 'page');
        $page_id = 0;

        if ($page instanceof WP_Post) {
            $page_id = (int) $page->ID;
            // Keep existing content/title; enforce correct template.
        } else {
            $page_id = wp_insert_post(
                array(
                    'post_title'   => (string) $spec['title'],
                    'post_name'    => (string) $slug,
                    'post_status'  => 'publish',
                    'post_type'    => 'page',
                    'post_content' => (string) $spec['content'],
                ),
                true
            );
        }

        if (!is_wp_error($page_id) && $page_id) {
            update_post_meta((int) $page_id, '_wp_page_template', (string) $spec['template']);
        }
    }
}

function ciunas_activate_theme(): void
{
    ciunas_register_publication_cpt();
    ciunas_sync_publications();
    ciunas_ensure_publications_page();
    ciunas_ensure_core_pages();
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'ciunas_activate_theme');

function ciunas_sync_publications_on_init(): void
{
    $json_file = get_stylesheet_directory() . '/publications.json';
    $checksum = file_exists($json_file) ? md5_file($json_file) : '';
    $saved_checksum = (string) get_option('ciunas_publications_checksum', '');

    if (!get_option('ciunas_publications_seeded') || ($checksum !== '' && $checksum !== $saved_checksum)) {
        ciunas_sync_publications();
        ciunas_ensure_publications_page();
        ciunas_ensure_core_pages();
        update_option('ciunas_publications_seeded', 1);
        update_option('ciunas_publications_checksum', $checksum);
    }
}
add_action('init', 'ciunas_sync_publications_on_init', 30);

add_action('init', 'ciunas_ensure_core_pages', 35);

function ciunas_form_redirect_base_url(int $publication_id): string
{
    $url = get_permalink($publication_id);
    return $url ? $url : home_url('/publications/');
}

function ciunas_handle_publication_form(): void
{
    $publication_id = isset($_POST['publication_id']) ? absint($_POST['publication_id']) : 0;
    $redirect_url = ciunas_form_redirect_base_url($publication_id);

    if ($publication_id < 1 || get_post_type($publication_id) !== 'publication') {
        wp_safe_redirect(add_query_arg('sent', '0', $redirect_url));
        exit;
    }

    $nonce = isset($_POST['ciunas_publication_nonce']) ? sanitize_text_field((string) $_POST['ciunas_publication_nonce']) : '';

    if (!wp_verify_nonce($nonce, 'ciunas_publication_enquiry_' . $publication_id)) {
        wp_safe_redirect(add_query_arg('sent', '0', $redirect_url));
        exit;
    }

    $honeypot = isset($_POST['company_name']) ? trim((string) $_POST['company_name']) : '';
    if ($honeypot !== '') {
        wp_safe_redirect(add_query_arg('sent', '1', $redirect_url));
        exit;
    }

    $name = isset($_POST['name']) ? sanitize_text_field((string) $_POST['name']) : '';
    $email = isset($_POST['email']) ? sanitize_email((string) $_POST['email']) : '';
    $school = isset($_POST['school']) ? sanitize_text_field((string) $_POST['school']) : '';
    $message = isset($_POST['message']) ? sanitize_textarea_field((string) $_POST['message']) : '';

    if ($name === '' || !is_email($email)) {
        wp_safe_redirect(add_query_arg('sent', '0', $redirect_url));
        exit;
    }

    $publication_title = get_the_title($publication_id);
    $subject = sprintf('Publication enquiry: %s', $publication_title);

    $body_lines = array(
        'Publication: ' . $publication_title,
        'Name: ' . $name,
        'Email: ' . $email,
        'School: ' . ($school !== '' ? $school : 'Not provided'),
        '',
        'Message:',
        $message !== '' ? $message : 'No additional message.',
    );

    $headers = array('Reply-To: ' . $name . ' <' . $email . '>');

    $sent = wp_mail(CIUNAS_CONTACT_EMAIL, $subject, implode("\n", $body_lines), $headers);

    wp_safe_redirect(add_query_arg('sent', $sent ? '1' : '0', $redirect_url));
    exit;
}
add_action('admin_post_ciunas_publication_enquiry', 'ciunas_handle_publication_form');
add_action('admin_post_nopriv_ciunas_publication_enquiry', 'ciunas_handle_publication_form');

function ciunas_disable_comments_everywhere(): void
{
    foreach (get_post_types() as $post_type) {
        if (post_type_supports($post_type, 'comments')) {
            remove_post_type_support($post_type, 'comments');
            remove_post_type_support($post_type, 'trackbacks');
        }
    }
}
add_action('admin_init', 'ciunas_disable_comments_everywhere');

add_filter('comments_open', '__return_false', 20, 2);
add_filter('pings_open', '__return_false', 20, 2);
add_filter('comments_array', '__return_empty_array', 10, 2);

function ciunas_hide_admin_comments_menu(): void
{
    remove_menu_page('edit-comments.php');
}
add_action('admin_menu', 'ciunas_hide_admin_comments_menu');

function ciunas_remove_comments_from_admin_bar($wp_admin_bar): void
{
    $wp_admin_bar->remove_node('comments');
}
add_action('admin_bar_menu', 'ciunas_remove_comments_from_admin_bar', 999);
