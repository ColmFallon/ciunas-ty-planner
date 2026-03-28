<?php
/**
 * Resource page helpers, sample request handling, and seeded writing content.
 */

if (!defined('ABSPATH')) {
    exit;
}

function ciunas_theme_asset_url(string $relative_path): string
{
    $relative_path = ltrim($relative_path, '/');
    $file = trailingslashit(get_stylesheet_directory()) . $relative_path;
    $url = trailingslashit(get_stylesheet_directory_uri()) . $relative_path;

    if (file_exists($file)) {
        return add_query_arg('v', (string) filemtime($file), $url);
    }

    return $url;
}

function ciunas_resource_definitions(): array
{
    return array(
        'public' => array(
            array(
                'label'    => 'Programme Overview',
                'filename' => 'Programme Overview.pdf',
            ),
            array(
                'label'    => 'Transition Year Scheme of Work',
                'filename' => 'TY Scheme of Work.pdf',
            ),
        ),
        'gated' => array(
            array(
                'label'    => 'The Climb and the Return Sample',
                'filename' => 'The Climb & the Return Sample.pdf',
            ),
            array(
                'label'    => 'An Dreapadh agus an Filleadh Sampla',
                'filename' => 'An Dreapadh agus an Filleadh Sampla.pdf',
            ),
            array(
                'label'    => 'Teacher Handbook Sample',
                'filename' => 'TY Wellbeing Programme Teacher Handbook Sample.pdf',
            ),
        ),
    );
}

function ciunas_resource_details(string $filename): array
{
    $relative_path = 'assets/resources/' . $filename;
    $absolute_path = trailingslashit(get_stylesheet_directory()) . $relative_path;

    return array(
        'filename' => $filename,
        'path'     => $absolute_path,
        'url'      => ciunas_theme_asset_url($relative_path),
        'exists'   => file_exists($absolute_path),
    );
}

function ciunas_resources_by_type(string $type): array
{
    $definitions = ciunas_resource_definitions();
    $resources = array();

    foreach ($definitions[$type] ?? array() as $resource) {
        $details = ciunas_resource_details((string) $resource['filename']);
        $resources[] = array_merge($resource, $details);
    }

    return $resources;
}

function ciunas_resources_page_url(): string
{
    $page = get_page_by_path('resources', OBJECT, 'page');
    if ($page instanceof WP_Post) {
        $url = get_permalink($page);
        if ($url) {
            return $url;
        }
    }

    return home_url('/resources/');
}

function ciunas_resources_success_message(): string
{
    return 'Thank you. Your sample links have been sent by email.';
}

function ciunas_sample_pack_label(): string
{
    return 'Sample Chapters pack';
}

function ciunas_send_sample_request_emails(string $name, string $email, string $school, string $requested_pack): bool
{
    $timestamp = wp_date('j F Y, H:i', current_time('timestamp'));

    $admin_headers = array(
        'Content-Type: text/plain; charset=UTF-8',
        'From: Ciúnas Learning <' . CIUNAS_CONTACT_EMAIL . '>',
        'Reply-To: ' . $name . ' <' . $email . '>',
    );

    $admin_body = implode(
        "\n",
        array(
            'Name: ' . $name,
            'Email: ' . $email,
            'School / Organisation: ' . ($school !== '' ? $school : 'Not provided'),
            'Timestamp: ' . $timestamp,
            'Requested sample pack: ' . $requested_pack,
        )
    );

    $admin_sent = wp_mail(
        CIUNAS_CONTACT_EMAIL,
        '[Ciúnas Learning] Sample request',
        $admin_body,
        $admin_headers
    );

    $available_links = array();
    foreach (ciunas_resources_by_type('gated') as $resource) {
        if (!empty($resource['exists'])) {
            $available_links[] = '- ' . $resource['label'] . ': ' . $resource['url'];
        }
    }

    $auto_response_lines = array(
        'Hi ' . $name . ',',
        '',
        'Thank you for your interest in Ciúnas Learning.',
        '',
        'You can access the requested sample materials below:',
        '',
    );

    if (!empty($available_links)) {
        $auto_response_lines = array_merge($auto_response_lines, $available_links);
    } else {
        $auto_response_lines[] = 'Sample links are not available at present.';
    }

    $auto_response_lines = array_merge(
        $auto_response_lines,
        array(
            '',
            'You can also view the following public programme documents on the website:',
            '- Programme Overview',
            '- Transition Year Scheme of Work',
            '',
            'If you would like to discuss a pilot, school rollout, or any aspect of the materials, please feel free to reply directly to this email.',
            '',
            'Best wishes,',
            'Colm Fallon',
            'Ciúnas Learning',
        )
    );

    $auto_headers = array(
        'Content-Type: text/plain; charset=UTF-8',
        'From: Ciúnas Learning <' . CIUNAS_CONTACT_EMAIL . '>',
        'Reply-To: ' . CIUNAS_CONTACT_EMAIL,
    );

    $user_sent = wp_mail(
        $email,
        'Your Ciúnas Learning sample chapters',
        implode("\n", $auto_response_lines),
        $auto_headers
    );

    return $admin_sent && $user_sent;
}

function ciunas_handle_resource_request_form(): void
{
    $redirect_url = ciunas_resources_page_url();
    $nonce = isset($_POST['ciunas_resources_nonce']) ? sanitize_text_field((string) $_POST['ciunas_resources_nonce']) : '';

    if (!wp_verify_nonce($nonce, 'ciunas_resources_request')) {
        wp_safe_redirect(add_query_arg('sent', '0', $redirect_url));
        exit;
    }

    $honeypot = isset($_POST['website']) ? trim((string) $_POST['website']) : '';
    if ($honeypot !== '') {
        wp_safe_redirect(add_query_arg('sent', '1', $redirect_url));
        exit;
    }

    $name = isset($_POST['name']) ? sanitize_text_field((string) $_POST['name']) : '';
    $email = isset($_POST['email']) ? sanitize_email((string) $_POST['email']) : '';
    $school = isset($_POST['school']) ? sanitize_text_field((string) $_POST['school']) : '';
    $requested_pack = isset($_POST['requested_pack']) ? sanitize_text_field((string) $_POST['requested_pack']) : ciunas_sample_pack_label();

    if ($name === '' || !is_email($email)) {
        wp_safe_redirect(add_query_arg('sent', '0', $redirect_url));
        exit;
    }

    $sent = ciunas_send_sample_request_emails($name, $email, $school, $requested_pack);
    wp_safe_redirect(add_query_arg('sent', $sent ? '1' : '0', $redirect_url));
    exit;
}
add_action('admin_post_ciunas_resource_request', 'ciunas_handle_resource_request_form');
add_action('admin_post_nopriv_ciunas_resource_request', 'ciunas_handle_resource_request_form');

function ciunas_find_attachment_by_source(string $relative_path): int
{
    $matches = get_posts(
        array(
            'post_type'              => 'attachment',
            'post_status'            => 'inherit',
            'posts_per_page'         => 1,
            'fields'                 => 'ids',
            'meta_key'               => '_ciunas_source_relative_path',
            'meta_value'             => $relative_path,
            'no_found_rows'          => true,
            'ignore_sticky_posts'    => true,
            'update_post_meta_cache' => false,
            'update_post_term_cache' => false,
        )
    );

    return !empty($matches[0]) ? (int) $matches[0] : 0;
}

function ciunas_ensure_attachment_from_theme_asset(string $relative_path, string $alt_text, int $parent_id = 0): int
{
    $relative_path = ltrim($relative_path, '/');
    $absolute_path = trailingslashit(get_stylesheet_directory()) . $relative_path;

    if (!file_exists($absolute_path)) {
        return 0;
    }

    $attachment_id = ciunas_find_attachment_by_source($relative_path);

    if ($attachment_id < 1) {
        $filetype = wp_check_filetype(basename($absolute_path), null);
        $attachment_id = wp_insert_attachment(
            array(
                'guid'           => ciunas_theme_asset_url($relative_path),
                'post_mime_type' => (string) ($filetype['type'] ?? ''),
                'post_title'     => sanitize_text_field(pathinfo($absolute_path, PATHINFO_FILENAME)),
                'post_content'   => '',
                'post_status'    => 'inherit',
                'post_parent'    => $parent_id,
            ),
            $absolute_path,
            $parent_id
        );

        if (is_wp_error($attachment_id) || !$attachment_id) {
            return 0;
        }
    }

    update_post_meta($attachment_id, '_ciunas_source_relative_path', $relative_path);
    update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);

    $attachment_post = array(
        'ID'          => $attachment_id,
        'post_parent' => $parent_id,
    );
    wp_update_post($attachment_post);

    if (!function_exists('wp_generate_attachment_metadata')) {
        require_once ABSPATH . 'wp-admin/includes/image.php';
    }

    $metadata = wp_generate_attachment_metadata($attachment_id, $absolute_path);
    if (!is_wp_error($metadata) && !empty($metadata)) {
        wp_update_attachment_metadata($attachment_id, $metadata);
    }

    return $attachment_id;
}

function ciunas_resources_page_content_seed(): string
{
    return 'Ciúnas Learning provides practical materials to help teachers evaluate programmes, preview sample content, and plan classroom implementation.';
}

function ciunas_ensure_resources_page_content(): void
{
    $page = get_page_by_path('resources', OBJECT, 'page');
    if (!($page instanceof WP_Post)) {
        return;
    }

    $page_id = (int) $page->ID;
    $updated_page = array(
        'ID'           => $page_id,
        'post_title'   => 'Resources for Teachers',
        'post_name'    => 'resources',
        'post_status'  => 'publish',
        'post_type'    => 'page',
        'post_content' => ciunas_resources_page_content_seed(),
    );

    wp_update_post($updated_page);
    update_post_meta($page_id, '_wp_page_template', 'page-resources.php');
}

function ciunas_ensure_writing_category(): int
{
    $term = get_term_by('slug', 'writing', 'category');
    if ($term instanceof WP_Term) {
        return (int) $term->term_id;
    }

    $term_id = wp_create_category('Writing');
    return is_wp_error($term_id) ? 0 : (int) $term_id;
}

function ciunas_baptism_article_content(): string
{
    $publication = get_page_by_path('the-climb-and-the-return', OBJECT, 'publication');
    $publication_url = $publication instanceof WP_Post ? get_permalink($publication) : home_url('/publications/the-climb-and-the-return/');

    $final_line = sprintf(
        '<p class="ciunas-article-note">This reflection sits alongside the wider formation framework developed in <a href="%s">The Climb and the Return</a>.</p>',
        esc_url($publication_url)
    );

    $body = <<<'HTML'
<p>There has been debate recently about whether infant baptism infringes on a child’s human rights because the child cannot consent.</p>
<p>I am not a lawyer or a politician, and I am not trying to resolve that question in policy terms. I can only speak from experience.</p>
<p>I drifted far from the faith of my childhood. For years I explored other spiritual traditions and philosophies. I read writers such as Eckhart Tolle and Jiddu Krishnamurti. I practised yoga and meditation. I questioned, wrestled, and experimented.</p>
<p>As a physicist, I do not take things on authority. I need to understand things for myself.</p>
<p>About two years ago, I began returning to the Catholic faith in which I was raised — not blindly, not uncritically, but slowly and consciously, with many questions still alive.</p>
<p>Looking back, I do not experience my baptism as something that trapped me. I experience it as something that gave me a home — a home I was free to leave, and free to return to.</p>
<p>When I was growing up in Ireland, Christianity was not only something you encountered in church. It was part of the cultural landscape.</p>
<p>We learned about the High Crosses in history class.</p>
<p>We encountered Christian stories in religion class.</p>
<p>Christian imagery and language appeared in literature, art, and Irish cultural history.</p>
<p>It was simply part of the background of life — like the stone walls in the fields or the old ruins on a hill.</p>
<p>Every child is born into a framework they did not choose: a language, a culture, a moral story, a way of seeing the world.</p>
<p>Secularism is also a framework. It is not neutrality.</p>
<p>This question also sits quietly behind some of the debates about the ethos of schools in Ireland. I do not pretend to know what the policy answer should be. History shows that forcing belief rarely ends well.</p>
<p>But removing a Christian cultural framework does not suddenly produce neutrality. It simply removes one story, and leaves another to take its place — sometimes consciously designed, sometimes not.</p>
<p>The real question is not whether children inherit a story. They always will.</p>
<p>The question is whether that story ultimately enlarges their freedom or diminishes it.</p>
<p>In my own life, the Christian story enlarged mine. There is a line from St Augustine:</p>
<p>“Our hearts are restless until they rest in You.”</p>
<p>I recognise something of myself in that.</p>
<p>After years of seeking, what I found was not a new philosophy but rest.</p>
<p>When I say I have come home to God, that word is nuanced for me. I do not mean certainty about every doctrine or agreement with every political stance of the Church.</p>
<p>I mean something simpler and more personal.</p>
<p>It feels like the end of striving.</p>
<p>It feels like the place where I come to lick my wounds and heal.</p>
<p>It feels like returning to the boy who did not mask himself, who did not need to impress anyone, who loved life without trying to.</p>
<p>The one who was not holding on to anything, and so had nothing to let go of.</p>
<p>For me, faith has become the practice of surrender and humility to reality as it is. When I am open in that way, reality sometimes feels less random and more relational.</p>
<p>I notice small hints of guidance, small movements of grace.</p>
<p>When I am closed, I look for love in the form I expect it to take, and I miss it.</p>
<p>It is Lent as I write this. My children are two and four. I do not talk to them about God yet — at that age the word would probably sit beside Santa Claus and the Easter Bunny.</p>
<p>But we practise.</p>
<p>We place coins in the Trocaire box.</p>
<p>We set sweets aside until Easter.</p>
<p>They are not learning doctrine.</p>
<p>They are learning connection.</p>
<p>They are learning that the year has rhythm, that restraint can lead to celebration, that their small hands can reach beyond themselves.</p>
<p>They are beginning to sense that their lives are part of something larger.</p>
<p>That is formation — not coercion.</p>
<p>My baptism did not force belief upon me. It did not remove my freedom to wander, question, or explore.</p>
<p>It quietly preserved the address of home.</p>
<p>I share this not to persuade anyone and not to dismiss concerns about freedom or rights.</p>
<p>I share it because when the striving quiets and the mask drops, what remains is love — or perhaps that which loves.</p>
<p>And perhaps that quiet love, that peace, is what we are all, in our own way, seeking.</p>
HTML;

    return $body . "\n" . $final_line;
}

function ciunas_ensure_baptism_article(): void
{
    $category_id = ciunas_ensure_writing_category();
    $existing = get_page_by_path('baptism-freedom-and-the-address-of-home', OBJECT, 'post');

    $postarr = array(
        'post_type'      => 'post',
        'post_status'    => 'publish',
        'post_title'     => 'Baptism, Freedom, and the Address of Home',
        'post_name'      => 'baptism-freedom-and-the-address-of-home',
        'post_excerpt'   => 'Looking back, I do not experience my baptism as something that trapped me. I experience it as something that gave me a home I was free to leave, and free to return to.',
        'post_content'   => ciunas_baptism_article_content(),
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
        return;
    }

    if ($category_id > 0) {
        wp_set_post_categories((int) $post_id, array($category_id), false);
    }

    $featured_image_id = ciunas_ensure_attachment_from_theme_asset(
        'assets/blog/high-crosses.png',
        'High crosses in Ireland',
        (int) $post_id
    );

    if ($featured_image_id > 0) {
        set_post_thumbnail((int) $post_id, $featured_image_id);
    }

    ciunas_ensure_attachment_from_theme_asset(
        'assets/blog/210824_Inishmurray_204-1800x1011.jpg',
        'Inishmurray, Ireland (aerial view)'
    );
}

function ciunas_seed_resources_and_writing_content(): void
{
    ciunas_ensure_resources_page_content();
    ciunas_ensure_baptism_article();
}
