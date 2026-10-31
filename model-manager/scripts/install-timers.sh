#!/bin/bash
# Run by the user: daily snapshot at 23:50 and weekly review on Monday 08:00.
# Remove with: systemctl --user disable --now model-manager-snapshot.timer model-manager-review.timer
# and delete ~/.config/systemd/user/model-manager-*.
set -euo pipefail
SINCE="${1:-2026-11-01}"
PROJECT="${2:-dom-z-widokiem}"
SCRIPTS="$HOME/.claude/plugins/marketplaces/phejno-plugins/model-manager/scripts"
UNITS="$HOME/.config/systemd/user"
mkdir -p "$UNITS" "$HOME/.claude/model-manager/snapshots"
cat > "$UNITS/model-manager-snapshot.service" <<UNIT
[Unit]
Description=model-manager daily statistics snapshot

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'python3 $SCRIPTS/report.py --since $SINCE --project $PROJECT --json > %h/.claude/model-manager/snapshots/\$(date +%%F).json'
UNIT
cat > "$UNITS/model-manager-review.service" <<UNIT
[Unit]
Description=model-manager weekly review

[Service]
Type=oneshot
Environment=PATH=$(dirname "$(command -v claude)"):/usr/local/bin:/usr/bin:/bin
ExecStart=/bin/bash $SCRIPTS/review.sh
UNIT
timer() {
  cat > "$UNITS/model-manager-$1.timer" <<UNIT
[Unit]
Description=model-manager $1 schedule

[Timer]
OnCalendar=$2
Persistent=true

[Install]
WantedBy=timers.target
UNIT
}
timer snapshot '*-*-* 23:50'
timer review 'Mon 08:00'
systemctl --user daemon-reload
systemctl --user enable --now model-manager-snapshot.timer model-manager-review.timer
systemctl --user list-timers 'model-manager*' --no-pager
