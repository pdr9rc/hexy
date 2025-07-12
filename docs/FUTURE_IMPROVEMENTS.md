# The Dying Lands - Future Improvements Documentation

## Overview
This document outlines planned improvements and redesigns for The Dying Lands ASCII Map Viewer, focusing on enhanced user experience, better visual design, and improved functionality.

## 1. Map Fixes and Improvements

### 1.1 Terrain Sheet Integration
**Issue**: Terrain sheet not found: `../data/TheDyingLands-Terrain Sheet.png.png`
**Solution**: 
- Fix file path resolution for terrain sheet images
- Implement proper image loading with fallback to coordinate-based detection
- Add error handling for missing image files
- Consider using relative paths or environment variables for image locations

### 1.2 Campaign Sheet Integration
**Issue**: Campaign sheet not found: `../data/TheDyingLands-Campaign Sheet.png`
**Solution**:
- Fix file path resolution for campaign sheet
- Implement campaign sheet parsing for additional lore data
- Add campaign-specific content generation


## 2. UI/UX Redesign

### 2.1 Button Styling Redesign
**Current State**: Basic Bootstrap styling
**New Design Goals**:
- Mörk Borg aesthetic with high contrast colors
- Custom button designs with dark themes
- Hover effects and animations
- Consistent styling across all interactive elements

**Color Palette**:
- Background: `#000000` (Pure black)
- Primary: `#00FFFF` (Cyan)
- Secondary: `#FFFF00` (Yellow)
- Accent: `#00FF00` (Green)
- Warning: `#FF00FF` (Magenta)
- Text: `#FFFFFF` (White)

**Button Styles**:
```css
.btn-mork-borg {
    background: #000000;
    border: 2px solid #00FFFF;
    color: #00FFFF;
    font-family: 'Adhesive NR Seven', serif;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}

.btn-mork-borg:hover {
    background: #00FFFF;
    color: #000000;
    box-shadow: 0 0 10px #00FFFF;
}
```

### 2.2 Layout Redesign - Side by Side Split

#### 2.2.1 Main Layout Structure
**Current State**: Single column layout
**New Design**: Split-screen layout with 50/50 division

```html
<div class="container-fluid">
    <div class="row">
        <!-- Left Side - Original Map -->
        <div class="col-md-6">
            <div class="map-container">
                <!-- ASCII Map Display -->
            </div>
        </div>
        
        <!-- Right Side - Modal Content -->
        <div class="col-md-6">
            <div class="modal-content-container">
                <!-- Dynamic Modal Content -->
            </div>
        </div>
    </div>
</div>
```

#### 2.2.2 Responsive Design
- Mobile: Stack vertically (map on top, modal below)
- Tablet: 60/40 split (map larger)
- Desktop: 50/50 split
- Large screens: 40/60 split (modal larger)

### 2.3 Modal System Redesign

#### 2.3.1 Current Modal Issues
- Modal appears over the map, hiding content
- Limited space for detailed information
- No persistent view of the map while viewing details

#### 2.3.2 New Modal Approach
**Split-Screen Modal Display**:
- Left side: Original ASCII map (static view)
- Right side: Detailed hex information
- No overlay - content displayed side by side
- Persistent map visibility

#### 2.3.3 Modal Content Structure
```html
<div class="modal-content">
    <div class="modal-header">
        <h3>Hex 0601 - Forest</h3>
        <button class="close-btn">×</button>
    </div>
    
    <div class="modal-body">
        <!-- Terrain Information -->
        <div class="terrain-section">
            <h4>Terrain: Forest</h4>
            <div class="ascii-terrain">
                ♠ ♠ ♠ ♠ ♠
                ♠ ♠ ♠ ♠ ♠
                ♠ ♠ ♠ ♠ ♠
            </div>
        </div>
        
        <!-- Encounter Information -->
        <div class="encounter-section">
            <h4>Encounter</h4>
            <p>※ Wild Beast Encounter</p>
        </div>
        
        <!-- Denizen Information -->
        <div class="denizen-section">
            <h4>Denizen</h4>
            <p>**Brother Bones** - Forest witch</p>
        </div>
        
        <!-- Notable Features -->
        <div class="features-section">
            <h4>Notable Features</h4>
            <p>Dense undergrowth</p>
        </div>
        
        <!-- Atmosphere -->
        <div class="atmosphere-section">
            <h4>Atmosphere</h4>
            <p>Dark and mysterious</p>
        </div>
    </div>
</div>
```

## 3. ASCII Map Enhancements

### 3.1 ASCII Art Improvements
**Current State**: Basic ASCII characters
**Enhancements**:
- Use extended ASCII characters for better visual representation
- Add color coding for different terrain types
- Implement animated elements (subtle)
- Add weather effects overlay

### 3.2 Interactive ASCII Elements
- Hover effects on hexes
- Click animations
- Visual feedback for selected hexes
- Path highlighting between hexes

### 3.3 ASCII Modal Integration
**Feature**: Show modal content in ASCII format
**Implementation**:
```javascript
function showAsciiModal(hexData) {
    const asciiModal = `
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Hex ${hexData.hex_code} - ${hexData.terrain}                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  Terrain: ${hexData.terrain}                                    ║
    ║  ${getAsciiTerrain(hexData.terrain)}                              ║
    ║                                                              ║
    ║  Encounter: ${hexData.encounter}                              ║
    ║                                                              ║
    ║  Denizen: ${hexData.denizen}                                  ║
    ║                                                              ║
    ║  Features: ${hexData.notable_feature}                        ║
    ║                                                              ║
    ║  Atmosphere: ${hexData.atmosphere}                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    `;
    
    document.getElementById('ascii-modal').innerHTML = asciiModal;
}
```

## 4. Technical Implementation

### 4.1 CSS Framework Updates
**Current**: Bootstrap 5
**Enhancements**:
- Custom CSS variables for Mörk Borg theme
- CSS Grid for advanced layouts
- Flexbox for responsive design
- Custom animations and transitions

### 4.2 JavaScript Improvements
**Modal System**:
```javascript
class ModalManager {
    constructor() {
        this.currentHex = null;
        this.modalContainer = document.getElementById('modal-container');
    }
    
    showHexModal(hexCode) {
        // Fetch hex data
        fetch(`/api/hex/${hexCode}`)
            .then(response => response.json())
            .then(data => {
                this.displayModal(data);
                this.updateMapView(hexCode);
            });
    }
    
    displayModal(hexData) {
        // Update right panel with modal content
        this.modalContainer.innerHTML = this.generateModalHTML(hexData);
    }
    
    updateMapView(hexCode) {
        // Highlight selected hex on left panel
        this.highlightHex(hexCode);
    }
}
```

### 4.3 Backend API Enhancements
**New Endpoints**:
- `/api/hex/{hex_code}` - Get detailed hex information
- `/api/map/terrain` - Get terrain distribution
- `/api/map/generate` - Generate new map content
- `/api/content/types` - Get available content types

## 5. Content Generation Improvements

### 5.1 Enhanced Content Types
**Current**: Basic terrain, settlements, dungeons, beasts, NPCs
**New Types**:
- Weather events
- Random encounters
- Faction territories
- Trade routes
- Hidden locations

### 5.2 Content Relationships
- Connected hexes with shared stories
- Regional themes and conflicts
- Faction influence areas
- Economic networks

## 6. Performance Optimizations

### 6.1 Loading Strategies
- Lazy loading for hex content
- Progressive map generation
- Background processing
- Content caching

### 6.2 Memory Management
- Cleanup of unused hex data
- Efficient data structures
- Optimized rendering

## 7. Accessibility Improvements

### 7.1 Screen Reader Support
- ARIA labels for interactive elements
- Semantic HTML structure
- Keyboard navigation
- High contrast mode

### 7.2 Mobile Optimization
- Touch-friendly interface
- Responsive design
- Optimized for small screens
- Gesture support

## 8. Testing and Quality Assurance

### 8.1 Automated Testing
- Unit tests for content generation
- Integration tests for API endpoints
- UI tests for modal interactions
- Performance benchmarks

### 8.2 Manual Testing Checklist
- [ ] Modal displays correctly in split view
- [ ] ASCII map remains visible during modal display
- [ ] Responsive design works on all screen sizes
- [ ] Button styling matches Mörk Borg aesthetic
- [ ] Content generation includes all types (dungeons, loot, NPCs)
- [ ] Performance is acceptable for large maps

## 9. Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- Fix map file path issues
- Implement basic split-screen layout
- Create new button styling system

### Phase 2: Modal System (Week 3-4)
- Redesign modal to display side by side
- Implement ASCII modal content
- Add persistent map view

### Phase 3: Content Enhancement (Week 5-6)
- Ensure all content types are working
- Add missing dungeons, loot, and NPCs
- Optimize content generation

### Phase 4: Polish and Testing (Week 7-8)
- Performance optimization
- Accessibility improvements
- Comprehensive testing
- Documentation updates

## 10. Success Metrics

### 10.1 User Experience
- Reduced time to view hex details
- Improved content discovery
- Better visual consistency
- Enhanced mobile experience

### 10.2 Technical Performance
- Faster map generation
- Reduced memory usage
- Improved loading times
- Better error handling

### 10.3 Content Quality
- All content types available
- Rich, interconnected content
- Consistent Mörk Borg aesthetic
- Engaging user interactions

---

**Note**: This document should be updated as implementation progresses and new requirements are discovered. Regular reviews and updates ensure the project stays aligned with user needs and technical best practices. 