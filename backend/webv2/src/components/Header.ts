import type { ViewMode } from '@/models/types';

export class Header {
  private worldBtn: HTMLButtonElement;
  private cityBtn: HTMLButtonElement;
  private viewModeCallback?: (mode: ViewMode) => void;

  constructor() {
    this.worldBtn = document.getElementById('world-view-btn') as HTMLButtonElement;
    this.cityBtn = document.getElementById('city-view-btn') as HTMLButtonElement;
    
    this.initialize();
  }

  private initialize(): void {
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    this.worldBtn.addEventListener('click', () => {
      this.setActiveView('world');
    });

    this.cityBtn.addEventListener('click', () => {
      this.setActiveView('cities');
    });
  }

  public setActiveView(mode: ViewMode): void {
    // Update button states
    this.worldBtn.classList.toggle('active', mode === 'world');
    this.cityBtn.classList.toggle('active', mode === 'cities');

    // Notify listeners
    if (this.viewModeCallback) {
      this.viewModeCallback(mode);
    }
  }

  public onViewModeChange(callback: (mode: ViewMode) => void): void {
    this.viewModeCallback = callback;
  }

  public getCurrentView(): ViewMode {
    return this.worldBtn.classList.contains('active') ? 'world' : 'cities';
  }
} 