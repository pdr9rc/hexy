# Procedural Audio Generation & Biome Integration Research

## Executive Summary

This research document explores how to integrate procedural audio generation with biomes for the Hexy - Dying Lands hexcrawl generator. While a specific "sndbox generator by Atelier Clandestin" tool was not found, this research identifies multiple viable approaches for creating dynamic, biome-aware audio experiences.

## Research Findings

### 1. Atelier Clandestin Investigation

**Company Profile:**
- **Location:** Le Mesnil Simon, France (28260)
- **Industry:** Movies, Videos, and Sound
- **Status:** Active production company

**Key Finding:** No specific "sndbox generator" tool was found publicly available from Atelier Clandestin. The company appears to be a traditional audiovisual production house rather than a software tools developer.

### 2. Alternative Procedural Audio Solutions

#### A. Web Audio API-Based Solutions

**Advantages:**
- Browser-native, no external dependencies
- Real-time generation
- Perfect integration with existing Flask web interface
- Zero asset downloads (lightweight)
- Dynamic parameter control

**Implementation Approach:**
```javascript
// Basic procedural audio texture generation
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function createBiomeAudio(biomeType) {
    const noiseSource = audioCtx.createBufferSource();
    const filter = audioCtx.createBiquadFilter();
    const lfo = audioCtx.createOscillator();
    
    // Configure based on biome
    switch(biomeType) {
        case 'forest':
            filter.frequency.value = 800;
            lfo.frequency.value = 0.1;
            break;
        case 'swamp':
            filter.frequency.value = 200;
            lfo.frequency.value = 0.05;
            break;
        // ... other biomes
    }
}
```

#### B. Unity-Based Procedural Audio

**Notable Tools Found:**
- **AmigaKlang/AtariKlang:** Advanced procedural audio for retro platforms
- **Unity Procedural Audio scripts:** Real-time sound generation
- **HDRP-compatible solutions:** For high-quality rendering pipelines

**Not Suitable For Current Project:** These require Unity game engine, while the current project uses Flask/web technologies.

#### C. BeepBox/Sandbox Family

**Tools Identified:**
- **Sandbox 3.1:** Browser-based chiptune melody creation
- **BeepBox variants:** Procedural music generation
- **SoundBox:** Online music editor with synthesis capabilities

**Relevance:** Could be adapted for ambient texture generation but primarily designed for music creation.

## Recommended Integration Strategy

### Phase 1: Web Audio API Foundation

**Core Components:**
1. **Biome Audio Engine** (JavaScript)
2. **Flask API Integration** (Python)
3. **Real-time Parameter Control** (WebSocket or AJAX)

**Architecture:**
```
Current Flask App
├── ASCII Map Viewer (existing)
├── Terrain System (existing)
└── [NEW] Audio System
    ├── Biome Audio Mapping
    ├── Procedural Audio Generation
    └── Real-time Parameter Updates
```

### Phase 2: Biome-Specific Audio Profiles

**Terrain-to-Audio Mapping:**

| Biome | Audio Characteristics | Technical Parameters |
|-------|----------------------|---------------------|
| **Mountain** | Wind, echoes, sparse sounds | High-pass filter, reverb, low density |
| **Forest** | Rustling, bird calls, dense ambient | Band-pass filter, multiple layers |
| **Coast** | Waves, gulls, wind | White noise + rhythm, stereo width |
| **Plains** | Gentle wind, distant sounds | Low-pass filter, subtle modulation |
| **Swamp** | Bubbling, insects, murky sounds | Low-frequency emphasis, irregular rhythms |
| **Desert** | Sparse wind, heat shimmer effects | Filtered noise, minimal elements |

### Phase 3: Dynamic Audio Parameters

**Hex-Based Audio Variables:**
- **Population Density:** Affects ambient sound complexity
- **Settlement Type:** Different audio signatures for cities vs. wilderness
- **Weather/Time:** Dynamic parameter modulation
- **Player Actions:** Interactive audio responses

## Technical Implementation Plan

### 1. Backend Integration (Python/Flask)

**New API Endpoints:**
```python
@app.route('/api/audio/biome/<hex_code>')
def get_biome_audio_params(hex_code):
    """Return audio parameters for a specific hex."""
    terrain = get_terrain_for_hex(hex_code)
    settlement = get_settlement_data(hex_code)
    
    return jsonify({
        'biome': terrain,
        'population': settlement.get('population', 0),
        'audio_params': generate_audio_params(terrain, settlement)
    })

def generate_audio_params(terrain, settlement):
    """Generate procedural audio parameters based on terrain and settlement."""
    base_params = BIOME_AUDIO_CONFIGS[terrain]
    
    # Modify based on settlement
    if settlement.get('population', 0) > 100:
        base_params['density'] *= 1.5
        base_params['urban_elements'] = True
    
    return base_params
```

### 2. Frontend Audio Engine (JavaScript)

**Core Audio Classes:**
```javascript
class BiomeAudioEngine {
    constructor() {
        this.audioContext = new AudioContext();
        this.activeAudioSources = new Map();
        this.currentBiome = null;
    }
    
    loadBiome(hexCode) {
        // Fetch audio parameters from Flask API
        // Generate procedural audio based on biome type
        // Transition smoothly from previous biome
    }
    
    generateProceduralAudio(biomeParams) {
        // Create audio graph based on biome parameters
        // Return audio source for playback
    }
}

class BiomeAudioTransition {
    static crossfade(fromAudio, toAudio, duration = 2000) {
        // Smooth transition between biome audio
    }
}
```

### 3. Enhanced User Interface

**New UI Components:**
- **Audio Toggle:** Enable/disable procedural audio
- **Volume Control:** Master and biome-specific volume
- **Audio Visualization:** Simple spectrum or waveform display
- **Biome Audio Status:** Current playing audio information

## Alternative Approaches

### 1. Hybrid Sample + Procedural Approach

**Concept:** Combine pre-recorded environmental samples with procedural modulation.

**Benefits:**
- More realistic base sounds
- Procedural variation prevents repetition
- Lower computational requirements

**Implementation:**
```javascript
// Load base samples for each biome
const biomeSamples = {
    forest: 'forest_base.wav',
    swamp: 'swamp_base.wav',
    // ...
};

// Apply procedural modulation
function modulateSample(sample, biomeParams) {
    const modulator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    // Apply LFO modulation based on biome characteristics
    modulator.connect(gainNode.gain);
    sample.connect(gainNode);
    
    return gainNode;
}
```

### 2. ByteBeat-Style Generation

**Concept:** Mathematical formula-based audio generation (inspired by ByteBeat techniques found in research).

**Example:**
```javascript
function generateBiomeFormula(biomeType, time) {
    switch(biomeType) {
        case 'forest':
            return ((time * 0.125) & (time >> 1)) * 0.5;
        case 'desert':
            return (time & time >> 8) * ((time >> 4) & (time >> 8));
        default:
            return time * 0.1;
    }
}
```

### 3. WebGL Audio Visualization

**Concept:** Combine procedural audio with visual terrain representation.

**Research Finding:** Several examples of WebGL terrain generation with audio integration were found, providing potential inspiration for visual-audio correlation.

## Integration with Current Codebase

### Minimal Changes Required

**New Files to Add:**
```
web/static/js/
├── biome-audio-engine.js
├── procedural-audio-generator.js
└── audio-ui-controls.js

src/
├── audio_system.py
└── biome_audio_configs.py
```

**Existing Files to Modify:**
```
src/ascii_map_viewer.py:
  - Add audio API endpoints
  - Include audio parameters in hex data

web/templates/main_map.html:
  - Add audio control UI
  - Include audio JavaScript files

src/terrain_system.py:
  - Add audio parameter generation methods
```

### Configuration Integration

**Biome Audio Configuration:**
```python
# biome_audio_configs.py
BIOME_AUDIO_CONFIGS = {
    'forest': {
        'base_frequency': 200,
        'filter_type': 'bandpass',
        'modulation_rate': 0.1,
        'density': 0.7,
        'reverb': 0.3,
        'elements': ['rustling', 'birds', 'insects']
    },
    'swamp': {
        'base_frequency': 80,
        'filter_type': 'lowpass',
        'modulation_rate': 0.05,
        'density': 0.9,
        'reverb': 0.6,
        'elements': ['bubbling', 'insects', 'water']
    },
    # ... other biomes
}
```

## Performance Considerations

### Computational Load
- **Web Audio API:** Low to moderate CPU usage
- **Real-time Generation:** Manageable for ambient textures
- **Memory Usage:** Minimal (no large audio files)

### Browser Compatibility
- **Web Audio API Support:** Good (95%+ modern browsers)
- **Fallback Strategy:** Silent operation for unsupported browsers
- **Mobile Considerations:** Reduced complexity for mobile devices

### Scalability
- **Multiple Hexes:** Audio pooling and recycling
- **Background Processing:** Web Workers for complex calculations
- **Parameter Caching:** Reduce redundant calculations

## Implementation Timeline

### Phase 1 (1-2 weeks): Foundation
- [ ] Research and prototype basic Web Audio API integration
- [ ] Create biome-to-audio parameter mappings
- [ ] Implement simple procedural noise generation
- [ ] Add basic UI controls

### Phase 2 (1-2 weeks): Integration
- [ ] Integrate with existing Flask API
- [ ] Add biome-specific audio profiles
- [ ] Implement smooth biome transitions
- [ ] Test with existing hex generation system

### Phase 3 (1 week): Enhancement
- [ ] Add advanced audio features (reverb, filtering)
- [ ] Optimize performance
- [ ] Add user preferences and controls
- [ ] Documentation and testing

## Conclusion

While the specific "sndbox generator by Atelier Clandestin" was not found, numerous viable alternatives exist for creating procedural, biome-aware audio experiences. The recommended approach using Web Audio API provides the best balance of:

- **Technical Compatibility:** Works with existing Flask/web architecture
- **Flexibility:** Highly customizable procedural generation
- **Performance:** Lightweight and efficient
- **User Experience:** Seamless integration with current interface

The proposed solution would significantly enhance the immersive quality of the Dying Lands hexcrawl generator while maintaining the project's current technical stack and design philosophy.

## References and Resources

1. **Web Audio API Documentation:** [MDN Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
2. **Procedural Audio Techniques:** Various GitHub repositories and research papers
3. **Biome Audio Design:** Environmental sound design principles
4. **Performance Optimization:** Web Audio best practices
5. **AmigaKlang/AtariKlang:** Reference for advanced procedural audio (different platform)

## Next Steps

1. **Prototype Development:** Create a minimal working prototype
2. **User Testing:** Test audio integration with existing users
3. **Performance Analysis:** Measure impact on application performance
4. **Documentation:** Create implementation and user guides