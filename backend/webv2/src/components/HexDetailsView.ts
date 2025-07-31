import { MarkdownRenderer } from './MarkdownRenderer';
import { AsciiUI } from './AsciiUI';
import { apiClient } from '@/api/client';
import type { HexCoordinate } from '@/models/types';

// Import AsciiField interface from AsciiUI
interface AsciiField {
  key: string;
  label: string;
  value: string;
  type: 'text' | 'textarea' | 'select';
  options?: string[];
  required?: boolean;
}

interface HexContent {
  id: string;
  coordinate: HexCoordinate;
  terrain: string;
  type: string;
  is_city: boolean;
  has_content: boolean;
  content_type?: string;
  city_name?: string;
  population?: string;
  content?: string;
}

interface HexDetailsViewState {
  currentHex: HexContent | null;
  isLoading: boolean;
  isEditing: boolean;
  viewMode: 'content' | 'edit';
}

export class HexDetailsView {
  private container: HTMLElement;
  private markdownRenderer: MarkdownRenderer;
  private asciiUI: AsciiUI;
  private state: HexDetailsViewState = {
    currentHex: null,
    isLoading: false,
    isEditing: false,
    viewMode: 'content'
  };

  constructor(container: HTMLElement) {
    this.container = container;
    
    // Create sub-components
    const markdownContainer = document.createElement('div');
    markdownContainer.className = 'hex-details-markdown';
    this.container.appendChild(markdownContainer);
    
    const asciiContainer = document.createElement('div');
    asciiContainer.className = 'hex-details-ascii';
    this.container.appendChild(asciiContainer);
    
    this.markdownRenderer = new MarkdownRenderer(markdownContainer);
    this.asciiUI = new AsciiUI(asciiContainer);
    
    this.setupCallbacks();
    this.render();
  }

  private setupCallbacks(): void {
    this.asciiUI.setCallbacks(
      (values) => this.handleSave(values),
      () => this.handleCancel()
    );
  }

  public async loadHexContent(coordinate: HexCoordinate): Promise<void> {
    try {
      this.setState({ isLoading: true });
      this.render();

      // Convert coordinate to hex code
      const hexCode = `${coordinate.q.toString().padStart(2, '0')}${coordinate.r.toString().padStart(2, '0')}`;
      
      // Get hex markdown from API
      const response = await apiClient.getHexMarkdown(hexCode);

      if (response.success && response.data) {
        // Create a hex content object from the markdown response
        const hexData: HexContent = {
          id: response.data.hex_code,
          coordinate: coordinate,
          terrain: 'unknown', // Will be extracted from markdown if needed
          type: 'world',
          is_city: false,
          has_content: response.data.has_content,
          content: response.data.markdown
        };
        
        this.setState({
          currentHex: hexData,
          isLoading: false,
          viewMode: 'content'
        });
        this.render();
      } else {
        throw new Error('Failed to load hex content');
      }
    } catch (error) {
      console.error('Error loading hex content:', error);
      this.setState({
        currentHex: null,
        isLoading: false
      });
      this.render();
    }
  }

  public setViewMode(mode: 'content' | 'edit'): void {
    this.setState({ viewMode: mode });
    this.render();
  }

  private setState(updates: Partial<HexDetailsViewState>): void {
    this.state = { ...this.state, ...updates };
  }

  private render(): void {
    if (this.state.isLoading) {
      this.renderLoading();
    } else if (!this.state.currentHex) {
      this.renderEmpty();
    } else if (this.state.viewMode === 'edit') {
      this.renderEditMode();
    } else {
      this.renderContentMode();
    }
  }

  private renderLoading(): void {
    this.container.innerHTML = `
      <div class="hex-details-loading">
        <div class="ascii-loading">
          <div class="ascii-loading-text">LOADING HEX CONTENT...</div>
          <div class="ascii-loading-spinner">⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏</div>
        </div>
      </div>
    `;
  }

  private renderEmpty(): void {
    this.container.innerHTML = `
      <div class="hex-details-empty">
        <div class="ascii-empty">
          <h2 class="ascii-empty-title">NO HEX SELECTED</h2>
          <p class="ascii-empty-text">Click on a hex to view its details</p>
        </div>
      </div>
    `;
  }

  private renderContentMode(): void {
    if (!this.state.currentHex) return;

    const hex = this.state.currentHex;
    const content = this.extractContent(hex);

    this.container.innerHTML = `
      <div class="hex-details-content">
        <div class="hex-details-header">
          <h2 class="hex-details-title">HEX ${hex.id}</h2>
          <div class="hex-details-controls">
            <button class="ascii-btn ascii-btn-edit" id="hex-edit-btn">
              [EDIT]
            </button>
            <button class="ascii-btn ascii-btn-refresh" id="hex-refresh-btn">
              [REFRESH]
            </button>
          </div>
        </div>
        
        <div class="hex-details-info">
          <div class="hex-info-grid">
            <div class="hex-info-item">
              <span class="hex-info-label">Terrain:</span>
              <span class="hex-info-value">${hex.terrain}</span>
            </div>
            <div class="hex-info-item">
              <span class="hex-info-label">Type:</span>
              <span class="hex-info-value">${hex.type}</span>
            </div>
            ${hex.is_city ? `
              <div class="hex-info-item">
                <span class="hex-info-label">City:</span>
                <span class="hex-info-value">${hex.city_name || 'Unknown'}</span>
              </div>
            ` : ''}
            ${hex.population ? `
              <div class="hex-info-item">
                <span class="hex-info-label">Population:</span>
                <span class="hex-info-value">${hex.population}</span>
              </div>
            ` : ''}
          </div>
        </div>
        
        <div class="hex-details-markdown-container" id="hex-markdown-container">
          <!-- Markdown content will be rendered here -->
        </div>
      </div>
    `;

    // Render markdown content
    const markdownContainer = this.container.querySelector('#hex-markdown-container');
    if (markdownContainer) {
      this.markdownRenderer = new MarkdownRenderer(markdownContainer as HTMLElement);
      this.markdownRenderer.render(content);
    }

    this.attachContentModeEvents();
  }

  private renderEditMode(): void {
    if (!this.state.currentHex) return;

    const hex = this.state.currentHex;
    const fields = this.extractFields(hex);

    this.container.innerHTML = `
      <div class="hex-details-edit">
        <div class="hex-details-header">
          <h2 class="hex-details-title">EDITING HEX ${hex.id}</h2>
          <div class="hex-details-controls">
            <button class="ascii-btn ascii-btn-view" id="hex-view-btn">
              [VIEW]
            </button>
          </div>
        </div>
        
        <div class="hex-details-ascii-container" id="hex-ascii-container">
          <!-- ASCII UI will be rendered here -->
        </div>
      </div>
    `;

    // Setup ASCII UI
    const asciiContainer = this.container.querySelector('#hex-ascii-container');
    if (asciiContainer) {
      this.asciiUI = new AsciiUI(asciiContainer as HTMLElement);
      this.asciiUI.setCallbacks(
        (values) => this.handleSave(values),
        () => this.handleCancel()
      );
      this.asciiUI.setFields(fields);
    }

    this.attachEditModeEvents();
  }

  private extractContent(hex: HexContent): string {
    // Try to get content from various sources
    if (hex.content) {
      return hex.content;
    }

    // If no direct content, create a structured view
    const sections = [];
    
    if (hex.terrain) {
      sections.push(`**Terrain:** ${hex.terrain}`);
    }
    
    if (hex.type) {
      sections.push(`**Type:** ${hex.type}`);
    }
    
    if (hex.is_city && hex.city_name) {
      sections.push(`**City:** ${hex.city_name}`);
    }
    
    if (hex.population) {
      sections.push(`**Population:** ${hex.population}`);
    }
    
    if (hex.content_type) {
      sections.push(`**Content Type:** ${hex.content_type}`);
    }

    return sections.length > 0 ? sections.join('\n\n') : 'No content available';
  }

  private extractFields(hex: HexContent): AsciiField[] {
    const fields: AsciiField[] = [
      {
        key: 'terrain',
        label: 'Terrain',
        value: hex.terrain || '',
        type: 'select',
        options: ['Sea', 'Plains', 'Forest', 'Mountain', 'Coast', 'Swamp', 'Desert', 'Snow', 'Unknown'],
        required: true
      },
      {
        key: 'type',
        label: 'Type',
        value: hex.type || '',
        type: 'select',
        options: ['world', 'settlement', 'city', 'dungeon', 'ruins'],
        required: true
      }
    ];

    if (hex.is_city) {
      fields.push({
        key: 'city_name',
        label: 'City Name',
        value: hex.city_name || '',
        type: 'text',
        required: true
      });
    }

    if (hex.population) {
      fields.push({
        key: 'population',
        label: 'Population',
        value: hex.population || '',
        type: 'text',
        required: false
      });
    }

    // Add content field if available
    if (hex.content) {
      fields.push({
        key: 'content',
        label: 'Content',
        value: hex.content,
        type: 'textarea',
        required: false
      });
    }

    return fields;
  }

  private attachContentModeEvents(): void {
    const editBtn = this.container.querySelector('#hex-edit-btn');
    editBtn?.addEventListener('click', () => {
      this.setState({ viewMode: 'edit' });
      this.render();
    });

    const refreshBtn = this.container.querySelector('#hex-refresh-btn');
    refreshBtn?.addEventListener('click', () => {
      if (this.state.currentHex) {
        this.loadHexContent(this.state.currentHex.coordinate);
      }
    });
  }

  private attachEditModeEvents(): void {
    const viewBtn = this.container.querySelector('#hex-view-btn');
    viewBtn?.addEventListener('click', () => {
      this.setState({ viewMode: 'content' });
      this.render();
    });
  }

  private async handleSave(values: Record<string, string>): Promise<void> {
    try {
      if (!this.state.currentHex) {
        throw new Error('No hex selected');
      }

      // Convert coordinate to hex code
      const hexCode = this.state.currentHex.id;
      
      // If there's a content field, save the markdown content
      if (values.content) {
        const response = await apiClient.updateHexMarkdown(hexCode, values.content);
        
        if (response.success) {
          // Update local state with new content
          this.state.currentHex = {
            ...this.state.currentHex,
            content: values.content
          };
          
          this.setState({ viewMode: 'content' });
          this.render();
        } else {
          throw new Error('Failed to save hex content');
        }
      } else {
        // For other fields, just update local state for now
        this.state.currentHex = {
          ...this.state.currentHex,
          ...values
        };
        
        this.setState({ viewMode: 'content' });
        this.render();
      }
    } catch (error) {
      console.error('Error saving hex content:', error);
      // Show error to user
      const errorContainer = this.container.querySelector('.ascii-error');
      if (errorContainer) {
        errorContainer.textContent = `Error saving: ${error instanceof Error ? error.message : 'Unknown error'}`;
      }
    }
  }

  private handleCancel(): void {
    this.setState({ viewMode: 'content' });
    this.render();
  }

  public updateContent(hexContent: HexContent): void {
    this.setState({
      currentHex: hexContent,
      isLoading: false,
      viewMode: 'content'
    });
    this.render();
  }

  public clear(): void {
    this.setState({
      currentHex: null,
      isLoading: false,
      isEditing: false,
      viewMode: 'content'
    });
    this.render();
  }
} 