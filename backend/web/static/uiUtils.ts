// web/static/uiUtils.ts

// Bleeding Effect Variables
let bleedingAnimation: any = null;
let bleedingCompleted: boolean = true;
let bleedingResized: boolean = false;
let bleedingClearTimeout: ReturnType<typeof setTimeout> | undefined;

function ensureOverlay(): { root: HTMLElement, video: HTMLVideoElement | null } | null {
  let root = document.getElementById('loading-indicator') as HTMLElement | null;
  if (!root) return null;
  const video = document.getElementById('loading-video') as HTMLVideoElement | null;
  return { root, video };
}

// Bleeding Effect Functions
function removeBleedingLines(): void {
  if (!bleedingCompleted) return;
  
  const svgContainer = document.getElementById('svgContainer') as SVGElement | null;
  const svgGroup = svgContainer?.querySelector('g') as SVGElement | null;
  
  if (!svgContainer || !svgGroup) return;
  
  while (svgGroup.childElementCount > 0) {
    const firstChild = svgGroup.firstChild;
    if (firstChild) {
      svgGroup.removeChild(firstChild);
    }
  }
  addBleedingLines();
}

function addBleedingLines(): void {
  console.log('🩸 Adding bleeding lines...');
  const svgContainer = document.getElementById('svgContainer') as SVGElement | null;
  const svgGroup = svgContainer?.querySelector('g') as SVGElement | null;
  
  console.log('🩸 SVG Container:', !!svgContainer);
  console.log('🩸 SVG Group:', !!svgGroup);
  
  if (!svgContainer || !svgGroup) {
    console.log('🩸 Cannot add bleeding lines - missing elements');
    return;
  }
  
  const strokeWidth = 15;
  const fragment = document.createDocumentFragment();
  
  // Compute integer pixel dimensions with a small safety margin to avoid
  // fractional rounding leaving a gap at the edges.
  const rect = svgContainer.getBoundingClientRect();
  const boxHeight = Math.ceil(rect.height) + 32; // extra 32px
  const boxWidth = Math.ceil(rect.width);
  console.log('🩸 Container dimensions:', boxWidth, 'x', boxHeight);
  svgContainer.setAttribute('viewBox', `0 0 ${boxWidth} ${boxHeight}`);
  
  for (let i = Math.ceil(boxWidth / strokeWidth); i > 0; i--) {
    const posX = (i - 1) * strokeWidth;
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line') as SVGLineElement;
    
    line.setAttribute('x1', posX.toString());
    line.setAttribute('x2', posX.toString());
    line.setAttribute('y1', '0');
    // Use the exact container height in device pixels to avoid any
    // rounding/percentage issues that can leave a gap at the bottom.
    line.setAttribute('y2', boxHeight.toString());
    line.setAttribute('style', `stroke-width: ${strokeWidth + 2}; stroke-dasharray: ${boxHeight}; stroke-dashoffset: ${boxHeight};`);
    
    fragment.appendChild(line);
    
    // Animate the line
    const delay = Math.random() * 1000;
    const duration = 2000 + Math.random() * 2000;
    
    setTimeout(() => {
      line.style.transition = `stroke-dashoffset ${duration}ms ease-in-out`;
      line.style.strokeDashoffset = '0';
    }, delay);
  }
  
  svgGroup.appendChild(fragment);
  console.log('🩸 Added', Math.ceil(boxWidth / strokeWidth), 'bleeding lines');
  
  // Hide after animation completes
  setTimeout(() => {
    const svgContainer2 = document.getElementById('svgContainer') as SVGElement | null;
    if (svgContainer2) {
      svgContainer2.classList.add('hidden');
      setTimeout(() => {
        bleedingCompleted = true;
        if (bleedingResized) {
          bleedingResized = false;
          removeBleedingLines();
        }
      }, 2000);
    }
  }, 4000);
}

function createBleedingSVG(): SVGElement {
  console.log('🩸 Creating bleeding SVG...');
  
  // Remove existing SVG if it exists
  const existingSvg = document.getElementById('svgContainer');
  if (existingSvg) {
    existingSvg.remove();
  }
  
  // Create new SVG
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  svg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
  svg.setAttribute('preserveAspectRatio', 'xMinYMin slice');
  svg.setAttribute('class', 'bleeding-effect hidden');
  svg.setAttribute('id', 'svgContainer');
  svg.style.position = 'fixed';
  svg.style.top = '-24px';
  svg.style.right = '0';
  svg.style.bottom = '-24px';
  svg.style.left = '0';
  svg.style.zIndex = '2';
  svg.style.width = '100%';
  svg.style.height = 'calc(100% + 48px)';
  svg.style.pointerEvents = 'none';
  svg.style.opacity = '1';
  svg.style.transition = 'opacity 2s';
  
  // Create filter
  const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
  filter.setAttribute('id', 'liquify');
  
  const blur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
  blur.setAttribute('in', 'SourceGraphic');
  blur.setAttribute('stdDeviation', '20');
  blur.setAttribute('result', 'blur');
  
  const colorMatrix = document.createElementNS('http://www.w3.org/2000/svg', 'feColorMatrix');
  colorMatrix.setAttribute('in', 'blur');
  colorMatrix.setAttribute('type', 'matrix');
  colorMatrix.setAttribute('values', '.15 0 0 0 0,  0 0 0 0 0,  0 0 0 0 0,  0 0 0 100 -20');
  
  filter.appendChild(blur);
  filter.appendChild(colorMatrix);
  
  // Create group
  const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  group.setAttribute('filter', 'url(#liquify)');
  
  svg.appendChild(filter);
  svg.appendChild(group);
  
  // Add to loading overlay so it sits under the skull video
  const loading = document.getElementById('loading-indicator');
  if (loading) {
    loading.appendChild(svg);
  } else {
    document.body.appendChild(svg);
  }
  
  console.log('🩸 Bleeding SVG created and added to DOM');
  return svg;
}

function startBleedingEffect(): void {
  console.log('🩸 Starting bleeding effect...');
  let svgContainer = document.getElementById('svgContainer') as SVGElement | null;
  
  if (!svgContainer) {
    console.log('🩸 SVG Container not found, creating it...');
    svgContainer = createBleedingSVG();
  }
  
  console.log('🩸 SVG Container found:', !!svgContainer);
  console.log('🩸 Bleeding completed:', bleedingCompleted);
  
  if (!svgContainer || !bleedingCompleted) {
    console.log('🩸 Cannot start bleeding effect - container or state issue');
    return;
  }
  
  bleedingCompleted = false;
  svgContainer.classList.remove('hidden');
  console.log('🩸 SVG Container classes:', svgContainer.className);
  addBleedingLines();
}

export function showLoading(_msg: string = 'Loading...') {
  const ensured = ensureOverlay();
  if (!ensured) return;
  const { root, video } = ensured;
  
  root.removeAttribute('hidden');
  
  if (video) {
    // Delay video display by 500ms
    setTimeout(() => {
      try {
        video.currentTime = 0;
        video.play().catch(error => {
          console.warn('Video playback failed:', error);
        });
      } catch (error) {
        console.warn('Video playback error:', error);
      }
    }, 500);
  }
}

export function hideLoading() {
  const el = document.getElementById('loading-indicator');
  if (el) el.setAttribute('hidden', 'true');
}

// Reset bleeding lines back to the starting position and clear them
export function resetBleedingToTop(): void {
  const svg = document.getElementById('svgContainer') as SVGElement | null;
  if (!svg) return;
  const group = svg.querySelector('g') as SVGGElement | null;
  if (!group) return;
  const boxHeight = Math.ceil(svg.getBoundingClientRect().height) + 32;
  Array.from(group.children).forEach((node) => {
    const line = node as SVGLineElement;
    line.style.transition = 'none';
    line.style.strokeDashoffset = boxHeight.toString();
  });
  while (group.firstChild) {
    group.removeChild(group.firstChild);
  }
  bleedingCompleted = true;
}

export function showNotification(msg: string, type: 'info' | 'error' = 'info') {
  const el = document.getElementById('notification-container');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  el.style.color = type === 'error' ? 'var(--mork-magenta)' : 'var(--mork-yellow)';
  setTimeout(() => { el.style.display = 'none'; }, 3500);
}

export const showError = (msg: string) => showNotification(msg, 'error');

// Custom, non-blocking confirmation shown within the loading overlay
export function showResetConfirm(onConfirm: () => void, onCancel?: () => void): void {
  const loading = document.getElementById('loading-indicator');
  if (!loading) { onConfirm(); return; }

  // Create overlay container if not present
  let overlay = document.getElementById('confirm-reset-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'confirm-reset-overlay';
    overlay.className = 'confirm-reset-overlay';
    loading.appendChild(overlay);
  }

  // Create modal box
  const modal = document.createElement('div');
  modal.className = 'confirm-reset-modal';
  modal.innerHTML = `
    <h4>KILL EM' ALL?</h4>
    <p>This will regenerate the entire map and content. This cannot be undone.</p>
    <div class="confirm-reset-actions">
      <button id="confirm-reset-yes" class="btn-mork-borg">Confirm</button>
      <button id="confirm-reset-no" class="btn-mork-borg">Cancel</button>
    </div>
  `;
  overlay.appendChild(modal);

  const cleanup = () => {
    modal.remove();
    // Remove overlay if empty
    if (overlay && overlay.childElementCount === 0) overlay.remove();
  };

  const yes = modal.querySelector('#confirm-reset-yes') as HTMLButtonElement | null;
  const no = modal.querySelector('#confirm-reset-no') as HTMLButtonElement | null;

  if (yes) yes.addEventListener('click', () => { cleanup(); onConfirm(); });
  if (no) no.addEventListener('click', () => { cleanup(); if (onCancel) onCancel(); });
}

export function showLoreModal(lore: any) {
  const container = document.getElementById('details-panel');
  if (!container) return;
  
  let html = `
    <div class="city-hex-details-box">
      <div class="ascii-box">
        <div class="ascii-inner-box">
          <div class="ascii-section ascii-lore-title">
            <span>LORE OVERVIEW</span>
          </div>`;
  
  if (lore.major_cities) {
    html += `
          <div class="ascii-section ascii-lore-cities">
            <span>MAJOR CITIES</span>
            <div class="ascii-content">${(lore.major_cities as string[]).join('\n')}</div>
          </div>`;
  }
  
  if (lore.factions) {
    html += `
          <div class="ascii-section ascii-lore-factions">
            <span>FACTIONS</span>
            <div class="ascii-content">${(lore.factions as string[]).join('\n')}</div>
          </div>`;
  }
  
  if (lore.notable_npcs) {
    html += `
          <div class="ascii-section ascii-lore-npcs">
            <span>NOTABLE NPCS</span>
            <div class="ascii-content">${(lore.notable_npcs as string[]).join('\n')}</div>
          </div>`;
  }
  
  if (lore.regional_lore) {
    html += `
          <div class="ascii-section ascii-lore-regions">
            <span>REGIONAL LORE</span>
            <div class="ascii-content">${(lore.regional_lore as string[]).join('\n')}</div>
          </div>`;
  }
  
  html += `
        </div>
      </div>
    </div>`;
  
  container.innerHTML = html;
} 

// Initialize bleeding effect on window load
window.addEventListener('load', () => {
  const svgContainer = document.getElementById('svgContainer') as SVGElement | null;
  if (svgContainer) {
    svgContainer.style.height = `calc(100vh + 48px)`;
    addBleedingLines();
  }
  
  // Expose global helper to start bleeding (for reset handler)
  (window as any).startBleeding = () => startBleedingEffect();
  
  console.log('🩸 UI Utils ready: start with (window as any).startBleeding() on reset');
});

// Handle window resize for bleeding effect
window.addEventListener('resize', () => {
  if (bleedingCompleted) {
    clearTimeout(bleedingClearTimeout);
    bleedingClearTimeout = setTimeout(removeBleedingLines, 500);
  } else {
    bleedingResized = true;
  }
});