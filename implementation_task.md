# Implementation Task: Areas Book Discovery and Creation

## Objective
Implement area and room discovery functionality to automatically create the "Areas" book structure in BookStack based on Home Assistant's area registry and device assignments.

## Background
Based on `shelf_structure.md`, the "Areas" book should contain:
- **Ground Floor** (chapters with pages: Living Room, Kitchen, Garage)
- **First Floor** (chapters with pages: Bedroom, Bathroom)
- **Basement**
- **Attic**
- **Outside**

## Implementation Plan

### Phase 1: Home Assistant Area Discovery

#### Task 1.1: Area Registry Integration
**File**: `custom_components/bookstack_integration/__init__.py`
- [ ] Import Home Assistant area registry
- [ ] Add function to query all areas from Home Assistant
- [ ] Handle area discovery exceptions gracefully

```python
async def _discover_home_assistant_areas(hass: HomeAssistant) -> Dict[str, Any]:
    """Discover all areas from Home Assistant."""
    from homeassistant.helpers import area_registry as ar
    area_registry = ar.async_get(hass)
    return {
        area.id: {
            "name": area.name,
            "normalized_name": area.normalized_name,
            "picture": area.picture,
            "aliases": area.aliases
        }
        for area in area_registry.areas.values()
    }
```

#### Task 1.2: Device and Entity Discovery per Area
**File**: `custom_components/bookstack_integration/__init__.py`
- [ ] Add function to get devices for each area
- [ ] Add function to get entities for each area
- [ ] Store device/entity counts and basic information

```python
async def _get_area_devices_and_entities(hass: HomeAssistant, area_id: str) -> Dict[str, Any]:
    """Get all devices and entities for a specific area."""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.core import HomeAssistantError
    
    device_registry = dr.async_get(hass)
    
    devices = [
        {
            "id": device.id,
            "name": device.name,
            "name_by_user": device.name_by_user,
            "manufacturer": device.manufacturer,
            "model": device.model,
            "identifiers": list(device.identifiers),
            "area_id": device.area_id
        }
        for device in device_registry.devices.values()
        if device.area_id == area_id
    ]
    
    # Get entities for this area
    entities = []
    for entity in hass.states.async_all():
        if entity.attributes.get("area_id") == area_id:
            entities.append({
                "entity_id": entity.entity_id,
                "friendly_name": entity.attributes.get("friendly_name", ""),
                "device_class": entity.attributes.get("device_class"),
                "unit_of_measurement": entity.attributes.get("unit_of_measurement")
            })
    
    return {
        "devices": devices,
        "entities": entities,
        "device_count": len(devices),
        "entity_count": len(entities)
    }
```

### Phase 2: BookStack "Areas" Book Structure Creation

#### Task 2.1: BookStack API Enhancement
**File**: `custom_components/bookstack_integration/bookstack_api.py`
- [ ] Add method to find or create the "Areas" book
- [ ] Add method to create chapter structure for floors/areas
- [ ] Add method to generate area pages with content

```python
def find_or_create_areas_book(self) -> Book:
    """Find or create the Areas book."""
    areas_book = self.find_book("Areas")
    if areas_book:
        return areas_book
    
    description = "Home Assistant device and entity documentation organized by physical areas"
    return self.create_book("Areas", description)

def create_area_chapter(self, book_id: int, area_name: str, area_info: Dict) -> Chapter:
    """Create a chapter for an area/floor."""
    description = f"Documentation for {area_name} area ({area_info.get('device_count', 0)} devices, {area_info.get('entity_count', 0)} entities)"
    return self.find_or_create_chapter(book_id, area_name, description)

def create_area_page(self, chapter_id: int, area_name: str, area_info: Dict) -> Page:
    """Create a detailed page for an area."""
    content = self._generate_area_page_content(area_name, area_info)
    return self.create_or_update_page(chapter_id, f"{area_name} Overview", content)

def _generate_area_page_content(self, area_name: str, area_info: Dict) -> str:
    """Generate markdown content for an area page."""
    content = f"""# {area_name} - Home Assistant Area Overview

## Overview
This page documents the Home Assistant devices and entities located in the **{area_name}** area.

## Statistics
- **Devices**: {area_info.get('device_count', 0)}
- **Entities**: {area_info.get('entity_count', 0)}

## Devices

| Device | Manufacturer | Model | Status |
|--------|-------------|-------|--------|
"""
    
    for device in area_info.get('devices', []):
        content += f"| {device.get('name', 'Unknown')} | {device.get('manufacturer', 'Unknown')} | {device.get('model', 'Unknown')} | Active |\n"
    
    content += """
## Entities

| Entity ID | Friendly Name | Device Class | Unit |
|-----------|--------------|--------------|------|
"""
    
    for entity in area_info.get('entities', []):
        unit = entity.get('unit_of_measurement', '-')
        device_class = entity.get('device_class', '-')
        friendly_name = entity.get('friendly_name', entity.get('entity_id', 'Unknown'))
        content += f"| {entity.get('entity_id', 'Unknown')} | {friendly_name} | {device_class} | {unit} |\n"
    
    content += f"""
## Last Updated
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This documentation is automatically generated by the Home Assistant BookStack Integration*
"""
    
    return content
```

### Phase 3: Area Mapping and Organization

#### Task 3.1: Area to Floor Mapping
**File**: `custom_components/bookstack_integration/__init__.py`
- [ ] Create area-to-floor mapping logic
- [ ] Handle unknown/fallback areas
- [ ] Support custom mapping configuration

```python
def _map_areas_to_floors(areas: Dict[str, Any]) -> Dict[str, List[str]]:
    """Map discovered areas to floor chapters."""
    floor_mapping = {
        "ground_floor": ["living room", "kitchen", "garage", "entrance", "dining room"],
        "first_floor": ["bedroom", "bathroom", "office", "guest room"],
        "basement": ["basement", "cellar"],
        "attic": ["attic", "loft"],
        "outside": ["garden", "patio", "balcony", "driveway", "outside"]
    }
    
    areas_by_floor = {
        "Ground Floor": [],
        "First Floor": [],
        "Basement": [],
        "Attic": [],
        "Outside": []
    }
    
    unmapped_areas = []
    
    for area_id, area_info in areas.items():
        area_name_lower = area_info["name"].lower()
        mapped = False
        
        for floor_key, floor_areas in floor_mapping.items():
            if any(keyword in area_name_lower for keyword in floor_areas):
                floor_name = floor_key.replace("_", " ").title()
                if floor_name in areas_by_floor:
                    areas_by_floor[floor_name].append(area_id)
                mapped = True
                break
        
        if not mapped:
            unmapped_areas.append(area_id)
    
    # Add unmapped areas to "Other" or create new chapters
    if unmapped_areas:
        areas_by_floor["Other Areas"] = unmapped_areas
    
    return areas_by_floor
```

#### Task 3.2: Enhanced Export Service
**File**: `custom_components/bookstack_integration/__init__.py`
- [ ] Implement actual export logic for areas
- [ ] Support area filtering in export service
- [ ] Add progress tracking and error handling

```python
async def handle_export(call: ServiceCall) -> None:
    """Handle the export service call with full implementation."""
    area_filter = call.data.get("area_filter")
    
    try:
        # Discover areas
        areas = await _discover_home_assistant_areas(hass)
        _LOGGER.info(f"Discovered {len(areas)} areas in Home Assistant")
        
        # Create or get Areas book
        areas_book = await hass.async_add_executor_job(
            client.find_or_create_areas_book
        )
        
        # Map areas to floors
        areas_by_floor = _map_areas_to_floors(areas)
        
        # Create structure and pages
        for floor_name, floor_area_ids in areas_by_floor.items():
            if area_filter and area_filter.lower() not in floor_name.lower():
                continue
                
            # Create floor chapter
            floor_chapter = await hass.async_add_executor_job(
                client.create_area_chapter, areas_book.id, floor_name, {}
            )
            
            # Create pages for each area in floor
            for area_id in floor_area_ids:
                area_info = await _get_area_devices_and_entities(hass, area_id)
                await hass.async_add_executor_job(
                    client.create_area_page, 
                    floor_chapter.id, 
                    areas[area_id]["name"], 
                    area_info
                )
        
        message = f"Successfully exported {len(areas)} areas to BookStack 'Areas' book"
        await async_create(
            hass, message, title="BookStack Export Complete",
            notification_id="bookstack_export_complete"
        )
        
    except Exception as e:
        _LOGGER.error(f"Export failed: {e}")
        message = f"Export failed: {str(e)}"
        await async_create(
            hass, message, title="BookStack Export Failed",
            notification_id="bookstack_export_failed"
        )
```

### Phase 4: Configuration and Customization

#### Task 4.1: Area Mapping Configuration
**File**: `custom_components/bookstack_integration/const.py`
- [ ] Add configuration options for custom area mapping
- [ ] Add settings for book/chapter creation preferences

```python
# Configuration for area mapping
DEFAULT_AREA_MAPPING = {
    "ground_floor_keywords": ["living", "kitchen", "garage", "entrance", "dining"],
    "first_floor_keywords": ["bedroom", "bathroom", "office", "guest"],
    "basement_keywords": ["basement", "cellar"],
    "attic_keywords": ["attic", "loft"],
    "outside_keywords": ["garden", "patio", "balcony", "driveway", "outside"]
}

# Create chapters for individual rooms
CREATE_ROOM_PAGES = True
```

#### Task 4.2: Error Handling and Logging
**File**: `custom_components/bookstack_integration/__init__.py`
- [ ] Add comprehensive error handling
- [ ] Improve logging for debugging
- [ ] Add validation for discovered data

## Testing Strategy

### Unit Tests
- [ ] Test area discovery function
- [ ] Test area-to-floor mapping logic
- [ ] Test BookStack API integration
- [ ] Test content generation

### Integration Tests
- [ ] Test with mock Home Assistant environment
- [ ] Test with real BookStack instance
- [ ] Test area filtering functionality
- [ ] Test error scenarios

### Manual Testing
- [ ] Test with actual Home Assistant setup
- [ ] Verify BookStack structure creation
- [ ] Check content formatting
- [ ] Test incremental updates

## Success Criteria

1. **Area Discovery**: Successfully discovers all areas from Home Assistant
2. **BookStack Structure**: Creates proper "Areas" book with floor-based chapters
3. **Content Generation**: Generates informative pages with device/entity details
4. **Area Filtering**: Respects area filter parameters in export service
5. **Error Handling**: Gracefully handles missing areas, devices, or API failures
6. **Performance**: Completes export within reasonable time for typical setups

## Dependencies

- Home Assistant area registry
- Home Assistant device registry
- BookStack API client (already implemented)
- Python datetime for timestamps

## Files to Modify

1. `custom_components/bookstack_integration/__init__.py` - Main export logic
2. `custom_components/bookstack_integration/bookstack_api.py` - BookStack content generation
3. `custom_components/bookstack_integration/const.py` - Configuration constants
4. `custom_components/bookstack_integration/services.yaml` - Service documentation
5. `tests/test_*` - Test files (new)

## Timeline Estimate

- **Phase 1** (Area Discovery): 2-3 hours
- **Phase 2** (BookStack Structure): 3-4 hours  
- **Phase 3** (Mapping & Export): 4-5 hours
- **Phase 4** (Configuration): 1-2 hours
- **Testing**: 2-3 hours

**Total Estimated Time**: 12-17 hours

## Next Steps After Completion

1. Implement similar functionality for "Rooms" book
2. Add "Integrations" and "Addons" book creation
3. Implement incremental updates
4. Add content templates for different entity types
5. Implement cross-referencing and linking