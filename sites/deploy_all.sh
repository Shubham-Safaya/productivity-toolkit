#!/usr/bin/env bash
# Deploy the three marketing sites as GitHub Pages project sites.
# Requires: gh (authenticated as the repo owner), git, curl.
# Usage: ./deploy_all.sh            # deploys all three
#        ./deploy_all.sh kongposh   # deploys one
set -euo pipefail

OWNER="$(gh api user --jq .login)"
echo "Deploying as: $OWNER"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITES=("${@:-kongposh threadpass sundays-with-safaya}")
[ $# -eq 0 ] && SITES=(kongposh threadpass sundays-with-safaya)

deploy_site() {
  local name="$1"
  local src="$SCRIPT_DIR/$name"
  local url="https://${OWNER,,}.github.io/$name/"
  echo ""
  echo "=== $name ==="

  # 1. Create the repo (skip if it already exists)
  if ! gh repo view "$OWNER/$name" >/dev/null 2>&1; then
    gh repo create "$name" --public --description "$(head -3 "$src/README.md" | tail -1)"
  else
    echo "Repo $OWNER/$name already exists, reusing."
  fi

  # 2. Push site files to main
  local tmp
  tmp="$(mktemp -d)"
  cp -r "$src/." "$tmp/"
  (
    cd "$tmp"
    git init -q -b main
    git add -A
    git commit -q -m "Launch $name pre-launch site"
    git remote add origin "https://github.com/$OWNER/$name.git"
    for i in 1 2 3 4 5; do
      git push -u origin main --force && break
      [ "$i" -eq 5 ] && { echo "push failed after retries"; exit 1; }
      sleep $((2 ** i))
    done
  )

  # 3. Enable Pages from main branch root; fall back to gh-pages branch
  if ! gh api -X POST "repos/$OWNER/$name/pages" \
       -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1; then
    if ! gh api "repos/$OWNER/$name/pages" >/dev/null 2>&1; then
      echo "Pages API on main failed; falling back to gh-pages branch."
      (
        cd "$tmp"
        git checkout -q -b gh-pages
        git push -u origin gh-pages --force
      )
      gh api -X POST "repos/$OWNER/$name/pages" \
        -f "source[branch]=gh-pages" -f "source[path]=/" >/dev/null 2>&1 || true
    else
      echo "Pages already enabled."
    fi
  fi
  rm -rf "$tmp"

  # 4. Poll the live URL until it returns 200 (up to ~5 minutes)
  echo -n "Polling $url "
  for i in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "$url")"
    if [ "$code" = "200" ]; then
      echo ""
      echo "LIVE: $url"
      return 0
    fi
    echo -n "."
    sleep 10
  done
  echo ""
  echo "WARN: $url not returning 200 yet (last status $code). Check repo Settings → Pages."
}

for site in ${SITES[@]}; do
  deploy_site "$site"
done

echo ""
echo "All done. Live URLs:"
for site in ${SITES[@]}; do
  echo "  https://${OWNER,,}.github.io/$site/"
done
