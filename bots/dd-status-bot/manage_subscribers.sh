#!/bin/bash
# Digitized Delivery Status Bot - Subscriber Management
# Usage: ./manage_subscribers.sh add email@cisco.com
#        ./manage_subscribers.sh remove email@cisco.com
#        ./manage_subscribers.sh list

cd "$(dirname "$0")"

ACTION=$1
EMAIL=$2

case $ACTION in
  add)
    if [ -z "$EMAIL" ]; then
      echo "Usage: ./manage_subscribers.sh add email@cisco.com"
      exit 1
    fi
    
    # Check if already exists
    if grep -q "$EMAIL" subscribers.json; then
      echo "⚠️  $EMAIL is already subscribed"
      exit 0
    fi
    
    # Add to JSON (insert before last ])
    sed -i '' "s/\]$/,\n    \"$EMAIL\"\n]/" subscribers.json
    
    # Clean up formatting
    python3 -c "import json; f=open('subscribers.json'); d=json.load(f); f.close(); open('subscribers.json','w').write(json.dumps(d, indent=2))"
    
    git add subscribers.json
    git commit -m "Add subscriber: $EMAIL"
    git push
    
    echo "✅ Added $EMAIL"
    echo "📋 Current subscribers:"
    cat subscribers.json
    ;;
    
  remove)
    if [ -z "$EMAIL" ]; then
      echo "Usage: ./manage_subscribers.sh remove email@cisco.com"
      exit 1
    fi
    
    # Remove from JSON
    python3 -c "
import json
with open('subscribers.json') as f:
    d = json.load(f)
if '$EMAIL' in d['emails']:
    d['emails'].remove('$EMAIL')
    with open('subscribers.json', 'w') as f:
        json.dump(d, indent=2, fp=f)
    print('Removed')
else:
    print('Not found')
"
    
    git add subscribers.json
    git commit -m "Remove subscriber: $EMAIL"
    git push
    
    echo "✅ Removed $EMAIL"
    ;;
    
  list)
    echo "📋 Current subscribers:"
    cat subscribers.json
    ;;
    
  *)
    echo "Digitized Delivery Status Bot - Subscriber Management"
    echo ""
    echo "Usage:"
    echo "  ./manage_subscribers.sh add email@cisco.com"
    echo "  ./manage_subscribers.sh remove email@cisco.com"
    echo "  ./manage_subscribers.sh list"
    ;;
esac
