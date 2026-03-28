# Publish "Contemplation in an Age of Curation"

This folder includes:
- `scripts/essay_contemplation.html` (post body in HTML `<p>...</p>` blocks)
- `scripts/publish_contemplation_post.sh` (WP-CLI publish script)

## Run locally (with WP-CLI)

From site root:

```bash
chmod +x scripts/publish_contemplation_post.sh
WP_PATH="$(pwd)" WP_URL="https://your-site.example" ./scripts/publish_contemplation_post.sh
```

If your WP-CLI environment already resolves path/url, you can run:

```bash
./scripts/publish_contemplation_post.sh
```

The script will print the final published post URL.

## Run on SiteGround via SSH

1. SSH into SiteGround.
2. `cd` to your WordPress site root.
3. Run:

```bash
chmod +x scripts/publish_contemplation_post.sh
WP_PATH="$(pwd)" WP_URL="https://your-live-domain.example" ./scripts/publish_contemplation_post.sh
```

The script verifies `wp core is-installed`, ensures the `Writing` category exists, creates/publishes the post, imports the image, sets featured image, and echoes the permalink.

## Note on media import

`wp media import` supports both `--post_id` (attach media to a post) and `--featured_image` (set as featured image during import).
