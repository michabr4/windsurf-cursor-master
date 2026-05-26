#!/usr/bin/env bash
# Export last 7 days from Mail.app (all accounts: Inbox + Sent), build digest, open it.
# Usage: ./run_email_digest.sh           # removes mail_raw.txt after success
#        ./run_email_digest.sh --keep-raw
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
RAW="$DIR/mail_raw.txt"
MD="$DIR/Email_Digest_Last_7_Days.md"
KEEP_RAW=0
if [[ "${1:-}" == "--keep-raw" ]]; then KEEP_RAW=1; fi

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

osascript <<'APPLESCRIPT' >"$RAW" 2>&1
with timeout of 900 seconds
	tell application "Mail"
		if not (it is running) then launch
		set cutoffDate to (current date) - (7 * days)
		set rowDelim to ASCII character 31 & "ROW" & ASCII character 31
		set colDelim to ASCII character 31 & "COL" & ASCII character 31
		set output to ""
		repeat with acc in accounts
			try
				set mbx to mailbox "Inbox" of acc
				set n to count of messages of mbx
				repeat with i from 1 to n
					if i > 5000 then exit repeat
					set msg to message i of mbx
					if (date received of msg) < cutoffDate then exit repeat
					set subj to ""
					try
						set subj to subject of msg as string
					end try
					set sndr to ""
					try
						set sndr to sender of msg as string
					end try
					set recd to date received of msg as string
					set output to output & rowDelim & subj & colDelim & sndr & colDelim & recd
				end repeat
			end try
			set sentMbx to missing value
			try
				set sentMbx to mailbox "Sent Items" of acc
			end try
			if sentMbx is missing value then
				try
					set sentMbx to mailbox "Sent Messages" of acc
				end try
			end if
			if sentMbx is not missing value then
				try
					set n to count of messages of sentMbx
					repeat with i from 1 to n
						if i > 3000 then exit repeat
						set msg to message i of sentMbx
						if (date sent of msg) < cutoffDate then exit repeat
						set subj to ""
						try
							set subj to subject of msg as string
						end try
						set sndr to ""
						try
							set sndr to sender of msg as string
						end try
						set recd to date sent of msg as string
						set output to output & rowDelim & "(Sent) " & subj & colDelim & sndr & colDelim & recd
					end repeat
				end try
			end if
		end repeat
		return output
	end tell
end timeout
APPLESCRIPT

if ! python3 "$DIR/email_digest.py" "$RAW"; then
	echo "Digest step failed." >&2
	exit 1
fi

if [[ "$KEEP_RAW" -eq 0 ]]; then
	rm -f "$RAW"
fi

open "$MD"
