# BookStack Export Usage Guide

## How to Start the Export

The BookStack integration provides a service called `bookstack_integration.export` that can be triggered in several ways:

## Method 1: Home Assistant Developer Tools (Manual Export)

### Step 1: Open Developer Tools
1. In Home Assistant, click the **Developer Tools** icon (wrench/hammer icon)
2. Go to the **Services** tab

### Step 2: Configure the Service
1. In the **Service** field, type or select: `bookstack_integration.export`
2. The service will show available parameters:
   - **area_filter** (optional): Filter specific areas by name

### Step 3: Execute the Export
1. Click **Call Service**
2. The export will start and you'll see notifications about the progress
3. Check Home Assistant's **Notifications** panel for results

### Example Service Call (Export All Areas)
```json
{}
```

### Example Service Call (Export Only Ground Floor Areas)
```json
{
  "area_filter": "Ground Floor"
}
```

## Method 2: Home Assistant Automations

### Create an Automation to Export Daily
```yaml
alias: "Daily BookStack Export"
description: "Export Home Assistant areas to BookStack daily"
trigger:
  - platform: time
    at: "02:00:00"  # 2 AM daily
action:
  - service: bookstack_integration.export
    data:
      area_filter: ""  # Leave empty to export all areas
mode: single
```

### Create an Automation to Export on Area Changes
```yaml
alias: "BookStack Export on Area Changes"
description: "Export to BookStack when areas are modified"
trigger:
  - platform: state
    entity_id: 
      - zone.home
    to: "home"  # Or any other condition
action:
  - delay: "00:05:00"  # Wait 5 minutes for changes to settle
  - service: bookstack_integration.export
    data: {}
mode: single
```

## Method 3: Home Assistant Scripts

### Create a Script for Manual Export
```yaml
bookstack_export:
  alias: "Export to BookStack"
  sequence:
    - service: bookstack_integration.export
      data:
        area_filter: "Ground Floor"  # Optional: specify area
  mode: parallel
```

### Use the Script in the UI
1. Go to **Settings** -> **Automations & Scenes**
2. Click **Scripts**
3. Find your "bookstack_export" script
4. Click **Run** to execute

## Method 4: REST API (Advanced)

You can also trigger the service via Home Assistant's REST API:

```bash
curl -X POST \
  http://your-home-assistant:8123/api/services/bookstack_integration/export \
  -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "area_filter": ""
  }'
```

## Export Process Flow

When you trigger the export, here's what happens:

1. **Area Discovery**
   - Integration queries Home Assistant's area registry
   - Discovers all configured areas
   - Logs: "Starting Home Assistant area discovery"

2. **Device & Entity Collection**
   - For each area, collects all devices assigned to it
   - Collects all entities with area_id matching the area
   - Logs: "Found X devices and Y entities for area [name]"

3. **Area Mapping**
   - Areas are automatically mapped to floor categories:
     - Ground Floor (living, kitchen, garage, etc.)
     - First Floor (bedroom, bathroom, office, etc.)
     - Basement (basement, cellar)
     - Attic (attic, loft)
     - Outside (garden, patio, etc.)
     - Other Areas (unmapped areas)
   - Logs: "Area mapping complete: X areas mapped to Y floors"

4. **BookStack Connection**
   - Connects to your configured BookStack instance
   - Creates or finds the "Areas" book
   - Logs: "Using Areas book: [name] (ID: [id])"

5. **Structure Creation**
   - Creates floor-based chapters in BookStack
   - Creates detailed pages for each area
   - Includes device tables, entity lists, and statistics
   - Logs progress for each created chapter and page

6. **Completion**
   - Shows success notification with statistics
   - Example: "Successfully exported 8 areas to BookStack (5 chapters, 8 pages)"

## Available Area Filters

Use these values in the `area_filter` parameter to export specific areas:

- **"Ground Floor"** - Export only ground floor areas
- **"First Floor"** - Export only first floor areas
- **"Basement"** - Export only basement areas
- **"Attic"** - Export only attic areas
- **"Outside"** - Export only outside areas
- **"Other Areas"** - Export only unmapped areas
- **"" (empty)** - Export all areas (default)

## Troubleshooting

### Check Logs
1. Go to **Settings** -> **System** -> **Logs**
2. Look for entries with "bookstack_integration"
3. Enable **Debug** level logging for detailed information

### Common Issues
- **"No BookStack configuration found"**: Configure the integration first
- **"No areas found in Home Assistant"**: Create areas in Home Assistant first
- **BookStack connection errors**: Check your BookStack URL and tokens

### Notification Messages
The integration shows notifications for:
- Export started
- Export complete (with statistics)
- Export failed (with error details)

## Next Steps

After the initial export:
1. Check your BookStack instance for the "Areas" book
2. Review the generated content and formatting
3. Consider setting up automated exports
4. Customize area mappings if needed in the integration code

## Integration Requirements

Before using the export:
1. **Configure BookStack Integration**: Set up connection to your BookStack instance
2. **Create Areas**: Set up areas in Home Assistant (Settings -> Areas & Zones)
3. **Assign Devices**: Ensure devices are assigned to the correct areas
4. **Test Connection**: Verify the BookStack connection works in integration settings