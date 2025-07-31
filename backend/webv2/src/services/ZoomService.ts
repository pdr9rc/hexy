import type { ViewMode } from '@/models/types';

interface ZoomState {
  scale: number;
  translateX: number;
  translateY: number;
  minScale: number;
  maxScale: number;
}

export class ZoomService {
  private state: ZoomState = {
    scale: 1,
    translateX: 0,
    translateY: 0,
    minScale: 0.1,
    maxScale: 5.0
  };
  
  private isEnabled = true;
  private isDragging = false;
  private isTouchDragging = false;
  private lastX = 0;
  private lastY = 0;
  private initialDistance = 0;
  private initialScale = 1;
  private animationFrameId: number | null = null;
  
  // DOM elements
  private container: HTMLElement | null = null;
  private gridElement: HTMLElement | null = null;
  
  // Touch state for pinch zoom
  private touchStartDistance = 0;
  private touchStartScale = 1;
  
  constructor() {
    this.initialize();
  }
  
  private initialize(): void {
    // Make zoom state globally accessible for debugging
    (window as any).zoomService = this;
  }
  
  // ===== INITIALIZATION =====
  
  public initializeZoom(container: HTMLElement, gridElement: HTMLElement): void {
    this.container = container;
    this.gridElement = gridElement;
    
    // Calculate initial scale to fit grid in container
    this.fitGridToContainer();
    
    // Setup event listeners
    this.setupWheelZoom();
    this.setupTouchZoom();
    this.setupPan();
  }
  
  private fitGridToContainer(): void {
    if (!this.container || !this.gridElement) return;
    
    const containerRect = this.container.getBoundingClientRect();
    const gridRect = this.gridElement.getBoundingClientRect();
    
    // Calculate scale to fit grid in container with some padding
    const padding = 20;
    const scaleX = (containerRect.width - padding) / gridRect.width;
    const scaleY = (containerRect.height - padding) / gridRect.height;
    
    // Use the smaller scale to ensure grid fits completely
    const fitScale = Math.min(scaleX, scaleY, 1); // Don't scale up beyond 1
    
    this.state.minScale = Math.min(fitScale, 0.1); // Ensure minimum zoom allows fitting
    this.state.scale = fitScale;
    this.state.translateX = 0;
    this.state.translateY = 0;
    
    this.applyTransform();
  }
  
  // ===== ZOOM FUNCTIONALITY =====
  
  public enableZoom(): void {
    this.isEnabled = true;
  }
  
  public disableZoom(): void {
    this.isEnabled = false;
  }
  
  public setZoom(scale: number): void {
    this.state.scale = Math.max(this.state.minScale, Math.min(this.state.maxScale, scale));
    this.applyTransform();
  }
  
  public getZoom(): number {
    return this.state.scale;
  }
  
  public zoomIn(): void {
    if (this.isEnabled) {
      this.setZoom(this.state.scale * 1.2);
    }
  }
  
  public zoomOut(): void {
    if (this.isEnabled) {
      this.setZoom(this.state.scale / 1.2);
    }
  }
  
  public resetZoom(): void {
    this.fitGridToContainer();
  }
  
  // ===== WHEEL ZOOM =====
  
  private setupWheelZoom(): void {
    if (!this.container) return;
    
    this.container.addEventListener('wheel', (e) => {
      if (!this.isEnabled || this.isDragging || this.isTouchDragging) return;
      
      e.preventDefault();
      
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newScale = this.state.scale * delta;
      
      if (newScale >= this.state.minScale && newScale <= this.state.maxScale) {
        // Calculate zoom center point
        const rect = this.container!.getBoundingClientRect();
        const centerX = e.clientX - rect.left;
        const centerY = e.clientY - rect.top;
        
        this.zoomToPoint(newScale, centerX, centerY);
      }
    }, { passive: false });
  }
  
  // ===== TOUCH ZOOM =====
  
  private setupTouchZoom(): void {
    if (!this.container) return;
    
    this.container.addEventListener('touchstart', (e) => {
      if (!this.isEnabled) return;
      
      if (e.touches.length === 2) {
        // Pinch zoom
        e.preventDefault();
        this.startPinchZoom(e);
      } else if (e.touches.length === 1) {
        // Single touch for panning
        const touch = e.touches[0];
        this.startPan(touch.clientX, touch.clientY);
      }
    }, { passive: false });
    
    this.container.addEventListener('touchmove', (e) => {
      if (!this.isEnabled) return;
      
      if (e.touches.length === 2) {
        // Pinch zoom
        e.preventDefault();
        this.handlePinchZoom(e);
      } else if (e.touches.length === 1 && this.isTouchDragging) {
        // Single touch panning
        e.preventDefault();
        const touch = e.touches[0];
        this.handlePan(touch.clientX, touch.clientY);
      }
    }, { passive: false });
    
    this.container.addEventListener('touchend', (e) => {
      if (e.touches.length === 0) {
        this.stopPinchZoom();
        this.stopPan();
      }
    });
    
    this.container.addEventListener('touchcancel', () => {
      this.stopPinchZoom();
      this.stopPan();
    });
  }
  
  private startPinchZoom(e: TouchEvent): void {
    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    
    this.touchStartDistance = this.getDistance(touch1, touch2);
    this.touchStartScale = this.state.scale;
  }
  
  private handlePinchZoom(e: TouchEvent): void {
    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    
    const currentDistance = this.getDistance(touch1, touch2);
    const scale = currentDistance / this.touchStartDistance;
    const newScale = this.touchStartScale * scale;
    
    if (newScale >= this.state.minScale && newScale <= this.state.maxScale) {
      // Calculate center point between touches
      const centerX = (touch1.clientX + touch2.clientX) / 2;
      const centerY = (touch1.clientY + touch2.clientY) / 2;
      
      this.zoomToPoint(newScale, centerX, centerY);
    }
  }
  
  private stopPinchZoom(): void {
    this.touchStartDistance = 0;
    this.touchStartScale = 1;
  }
  
  private getDistance(touch1: Touch, touch2: Touch): number {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }
  
  // ===== PAN FUNCTIONALITY =====
  
  private setupPan(): void {
    if (!this.container) return;
    
    this.container.addEventListener('mousedown', (e) => {
      if (!this.isEnabled) return;
      
      // Support middle mouse (button 1) and left mouse with ctrl/cmd (button 0)
      if (e.button === 1 || (e.button === 0 && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        this.startPan(e.clientX, e.clientY);
        this.container!.style.cursor = 'grabbing';
        this.container!.style.userSelect = 'none';
      }
    });
    
    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        e.preventDefault();
        this.handlePan(e.clientX, e.clientY);
      }
    }, { passive: false });
    
    window.addEventListener('mouseup', (e) => {
      if (this.isDragging && (e.button === 1 || e.button === 0)) {
        this.stopPan();
        if (this.container) {
          this.container.style.cursor = '';
          this.container.style.userSelect = '';
        }
      }
    });
    
    window.addEventListener('mouseleave', () => {
      if (this.isDragging) {
        this.stopPan();
        if (this.container) {
          this.container.style.cursor = '';
          this.container.style.userSelect = '';
        }
      }
    });
  }
  
  private startPan(x: number, y: number): void {
    this.isDragging = true;
    this.isTouchDragging = true;
    this.lastX = x;
    this.lastY = y;
  }
  
  private handlePan(x: number, y: number): void {
    if (!this.isDragging && !this.isTouchDragging) return;
    
    // Cancel any pending animation frame
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    
    // Use requestAnimationFrame for smooth panning
    this.animationFrameId = requestAnimationFrame(() => {
      const dx = x - this.lastX;
      const dy = y - this.lastY;
      
      // Apply pan with constraints
      this.state.translateX += dx / this.state.scale;
      this.state.translateY += dy / this.state.scale;
      
      // Apply constraints to keep grid in view
      this.constrainPan();
      
      this.lastX = x;
      this.lastY = y;
      
      this.applyTransform();
    });
  }
  
  private stopPan(): void {
    this.isDragging = false;
    this.isTouchDragging = false;
    
    // Cancel any pending animation frame
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }
  
  // ===== ZOOM TO POINT =====
  
  private zoomToPoint(newScale: number, centerX: number, centerY: number): void {
    if (!this.container) return;
    
    const rect = this.container.getBoundingClientRect();
    const containerCenterX = rect.width / 2;
    const containerCenterY = rect.height / 2;
    
    // Calculate the point in grid coordinates
    const gridX = (centerX - containerCenterX) / this.state.scale - this.state.translateX;
    const gridY = (centerY - containerCenterY) / this.state.scale - this.state.translateY;
    
    // Update scale
    this.state.scale = newScale;
    
    // Calculate new translation to keep the zoom center point in the same place
    this.state.translateX = (centerX - containerCenterX) / newScale - gridX;
    this.state.translateY = (centerY - containerCenterY) / newScale - gridY;
    
    // Apply constraints
    this.constrainPan();
    this.applyTransform();
  }
  
  // ===== CONSTRAINTS =====
  
  private constrainPan(): void {
    if (!this.container || !this.gridElement) return;
    
    const containerRect = this.container.getBoundingClientRect();
    const gridRect = this.gridElement.getBoundingClientRect();
    
    // Calculate the scaled grid dimensions
    const scaledGridWidth = gridRect.width * this.state.scale;
    const scaledGridHeight = gridRect.height * this.state.scale;
    
    // Calculate maximum allowed translation
    const maxTranslateX = Math.max(0, (scaledGridWidth - containerRect.width) / 2);
    const maxTranslateY = Math.max(0, (scaledGridHeight - containerRect.height) / 2);
    
    // Apply constraints
    this.state.translateX = Math.max(-maxTranslateX, Math.min(maxTranslateX, this.state.translateX));
    this.state.translateY = Math.max(-maxTranslateY, Math.min(maxTranslateY, this.state.translateY));
  }
  
  // ===== TRANSFORM APPLICATION =====
  
  private applyTransform(): void {
    if (!this.gridElement) return;
    
    const transform = `translate(${this.state.translateX}px, ${this.state.translateY}px) scale(${this.state.scale})`;
    this.gridElement.style.transform = transform;
    this.gridElement.style.transformOrigin = 'center center';
  }
  
  // ===== VIEW MODE INTEGRATION =====
  
  public setViewMode(mode: ViewMode): void {
    // Disable zoom in city view
    if (mode === 'cities') {
      this.disableZoom();
    } else {
      this.enableZoom();
    }
  }
  
  // ===== UTILITY METHODS =====
  
  public getZoomLevel(): string {
    return `${Math.round(this.state.scale * 100)}%`;
  }
  
  public isZoomEnabled(): boolean {
    return this.isEnabled;
  }
  
  public isPanning(): boolean {
    return this.isDragging || this.isTouchDragging;
  }
  
  public getState(): ZoomState {
    return { ...this.state };
  }
  
  public destroy(): void {
    this.stopPan();
    this.stopPinchZoom();
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }
}

// Export singleton instance
export const zoomService = new ZoomService(); 