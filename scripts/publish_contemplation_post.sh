#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

POST_TITLE="Contemplation in an Age of Curation"
POST_SLUG="contemplation-in-an-age-of-curation"
POST_STATUS="publish"
CATEGORY_NAME="Writing"
EXCERPT="Meditation can become self-optimisation unless it is rooted in culture, discipline, and a wider framework of meaning."
IMAGE_TITLE_ALT="Inishmurray, Ireland (aerial view)"

CONTENT_FILE="$SCRIPT_DIR/essay_contemplation.html"
IMAGE_FILE="$REPO_ROOT/wp-content/themes/ciunas-learning-child/assets/blog/210824_Inishmurray_204-1800x1011.jpg"

if ! command -v wp >/dev/null 2>&1; then
  echo "Error: wp-cli is not installed or not in PATH." >&2
  echo "Install WP-CLI locally, or run this script over SSH on SiteGround where wp is available." >&2
  exit 1
fi

if [[ ! -f "$CONTENT_FILE" ]]; then
  echo "Error: content file not found: $CONTENT_FILE" >&2
  exit 1
fi

if [[ ! -f "$IMAGE_FILE" ]]; then
  echo "Error: image file not found: $IMAGE_FILE" >&2
  exit 1
fi

wp_cmd=(wp)
if [[ -n "${WP_PATH:-}" ]]; then
  wp_cmd+=(--path="$WP_PATH")
fi
if [[ -n "${WP_URL:-}" ]]; then
  wp_cmd+=(--url="$WP_URL")
fi

"${wp_cmd[@]}" core is-installed >/dev/null

category_id="$("${wp_cmd[@]}" term list category --name="$CATEGORY_NAME" --field=term_id --format=ids | awk '{print $1}')"
if [[ -z "$category_id" ]]; then
  category_id="$("${wp_cmd[@]}" term create category "$CATEGORY_NAME" --porcelain)"
fi

post_id="$("${wp_cmd[@]}" post create "$CONTENT_FILE" \
  --post_type=post \
  --post_status="$POST_STATUS" \
  --post_title="$POST_TITLE" \
  --post_name="$POST_SLUG" \
  --post_category="$category_id" \
  --porcelain)"

"${wp_cmd[@]}" post update "$post_id" --post_excerpt="$EXCERPT" >/dev/null

attachment_id="$("${wp_cmd[@]}" media import "$IMAGE_FILE" \
  --post_id="$post_id" \
  --featured_image \
  --title="$IMAGE_TITLE_ALT" \
  --porcelain)"

"${wp_cmd[@]}" post meta update "$attachment_id" _wp_attachment_image_alt "$IMAGE_TITLE_ALT" >/dev/null

post_url="$("${wp_cmd[@]}" post url "$post_id")"
echo "$post_url"
