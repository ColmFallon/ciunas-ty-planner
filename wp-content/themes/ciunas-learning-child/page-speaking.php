<?php
/**
 * Speaking page template.
 * Template Name: Speaking Page
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
            <h1 class="ciunas-page-title">Speaking</h1>
            <p>Ci&uacute;nas Learning offers a limited number of school talks focused on student formation, educational purpose, and wise engagement with emerging technologies.</p>
            <p>Talks are practical, calm, and designed with school leadership and teaching teams around local needs.</p>

            <h2>Core Speaking Themes</h2>
            <ul>
                <li>Mindset and growth mindset</li>
                <li>Resilience and habit formation</li>
                <li>Science of caring for the body (sleep, movement, nutrition)</li>
                <li>Caring for the mind (attention, emotions, self-regulation)</li>
                <li>Connection with others and character formation</li>
                <li>Meditation and practical mindfulness (teacher-safe framing)</li>
            </ul>

            <h2>Selected Engagements</h2>
            <p><strong>Schools (2019-2023):</strong> Sion Hill College, Ashbourne Community School, St Mary&rsquo;s (Edenderry), Mount Sackville, St Declan&rsquo;s (Cabra), Synge Street CBS (Dublin), Mercy (Kilbeggan), and other schools nationally.</p>
            <p><strong>Conferences and events:</strong> Literacy Association of Ireland Conference (Nov 2024), Ticketsolve Annual Education Event (Mar 2023), Dublin MindBody Experience (2019), and Sl&iacute; na Band&eacute; Yoga Retreat (2019).</p>

            <h2>Availability</h2>
            <p><strong>Limited school talks are available during the remainder of the 2025-26 school year (to end of May).</strong> From September onwards, engagements are selective and focused on substantial school adoptions or special events.</p>
            <p><a class="ciunas-button primary" href="<?php echo esc_url(home_url('/contact/')); ?>">Enquire About School Talks</a></p>
        </section>
    </div>
</main>
<?php
ciunas_site_footer();
ciunas_page_end();
