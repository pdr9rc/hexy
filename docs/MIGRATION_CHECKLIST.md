# Hexy WebV2 Migration Checklist

## 📋 File Migration Status

### ✅ Completed Files
- [x] `api.ts` → `src/api/client.ts` (Enhanced with all endpoints)
- [x] `types.ts` → `src/models/types.ts` (Enhanced with all interfaces)
- [x] `cityOverlays.ts` → `src/services/CityOverlayService.ts` + `src/components/CityOverlay.ts`
- [x] `fonts.css` → `src/styles/fonts.css` (Copied)
- [x] `globals.css` → `src/styles/globals.css` (Enhanced with city styles)
- [x] `controls.ts` → `src/components/Controls.ts` (Complete)
- [x] `uiUtils.ts` → `src/utils/uiUtils.ts` (Complete)
- [x] `mapRenderer.ts` → `src/components/MapRenderer.ts` (Complete)
- [x] `main.css` → `src/styles/main.css` (Critical hex styling)
- [x] `city-overlay.css` → `src/styles/city-overlay.css` (Complete)
- [x] `hexViewer.ts` → `src/components/HexContent.ts` (Enhanced with complex formatting)

### 🔄 In Progress Files
- [ ] `hexViewer.ts` → `src/components/WorldGrid.ts` (Basic structure done, needs complex logic)
- [ ] `main.ts` → `src/main.ts` (Basic structure done, needs enhancement)

### ⏳ Pending Files
- [x] `cityOverlay.ts` → `src/components/CityOverlay.ts` (Complete - all features migrated)

### 📁 Asset Files
- [x] `BLACH___.TTF` → `src/assets/fonts/BLACH___.TTF` (Copied)
- [x] `Jacquard12-Regular.ttf` → `src/assets/fonts/Jacquard12-Regular.ttf` (Copied)
- [ ] `public/` directory contents

## 🎯 Priority Order

### Phase 1: Core Functionality (High Priority)
1. **`hexViewer.ts`** - Complex hex rendering logic
2. **`mapRenderer.ts`** - Grid positioning and layout
3. **`main.css`** - Critical styling for hex display

### Phase 2: Enhanced Features (Medium Priority)
4. **`controls.ts`** - Language switching, generation controls
5. **`uiUtils.ts`** - Loading states, notifications
6. **`cityOverlay.ts`** - Additional city features

### Phase 3: Polish (Low Priority)
7. **`city-overlay.css`** - Additional city styling
8. **`public/`** - Static assets

## 📊 Progress Tracking

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| `api.ts` | ✅ Complete | High | All endpoints migrated |
| `types.ts` | ✅ Complete | High | All interfaces defined |
| `hexViewer.ts` | ✅ Complete | High | Enhanced with complex formatting |
| `main.ts` | ✅ Complete | High | Full functionality with clean architecture |
| `cityOverlays.ts` | ✅ Complete | Medium | Full service + component |
| `controls.ts` | ✅ Complete | Medium | Language, generation controls |
| `uiUtils.ts` | ✅ Complete | Low | Loading, notifications |
| `mapRenderer.ts` | ✅ Complete | High | Grid positioning |
| `main.css` | ✅ Complete | High | Critical hex styling |
| `city-overlay.css` | ✅ Complete | Low | Additional city styles |
| `cityOverlay.ts` | ✅ Complete | Low | All features migrated |
| `fonts.css` | ✅ Complete | Low | Copied |
| `globals.css` | ✅ Complete | Medium | Enhanced |

## 🚀 Next Steps

1. **Examine `hexViewer.ts`** - Port complex hex rendering logic
2. **Examine `mapRenderer.ts`** - Port grid positioning logic
3. **Examine `main.css`** - Port critical hex styling
4. **Start backend** - Test with real data

## 📝 Notes

- **Complex Logic**: `hexViewer.ts` contains the most complex rendering logic
- **Styling**: `main.css` is large (48KB) and contains critical hex styling
- **Dependencies**: Some files depend on others, need to migrate in order
- **Testing**: Need backend running to test API integration 