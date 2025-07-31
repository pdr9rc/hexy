interface AsciiField {
  key: string;
  label: string;
  value: string;
  type: 'text' | 'textarea' | 'select';
  options?: string[];
  required?: boolean;
}

interface AsciiUIState {
  isEditing: boolean;
  currentField: string | null;
  originalValues: Record<string, string>;
  editedValues: Record<string, string>;
}

export class AsciiUI {
  private container: HTMLElement;
  private fields: AsciiField[] = [];
  private state: AsciiUIState = {
    isEditing: false,
    currentField: null,
    originalValues: {},
    editedValues: {}
  };
  private onSaveCallback?: (values: Record<string, string>) => void;
  private onCancelCallback?: () => void;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  public setFields(fields: AsciiField[]): void {
    this.fields = fields;
    this.state.originalValues = {};
    this.state.editedValues = {};
    
    // Initialize values
    fields.forEach(field => {
      this.state.originalValues[field.key] = field.value;
      this.state.editedValues[field.key] = field.value;
    });
    
    this.render();
  }

  public setCallbacks(
    onSave?: (values: Record<string, string>) => void,
    onCancel?: () => void
  ): void {
    this.onSaveCallback = onSave;
    this.onCancelCallback = onCancel;
  }

  private render(): void {
    if (this.state.isEditing) {
      this.renderEditMode();
    } else {
      this.renderViewMode();
    }
  }

  private renderViewMode(): void {
    const html = `
      <div class="ascii-ui-view">
        <div class="ascii-ui-header">
          <h2 class="ascii-ui-title">HEX CONTENT EDITOR</h2>
          <div class="ascii-ui-controls">
            <button class="ascii-btn ascii-btn-edit" id="ascii-edit-btn">
              [EDIT MODE]
            </button>
          </div>
        </div>
        
        <div class="ascii-ui-content">
          ${this.fields.map(field => `
            <div class="ascii-field-view" data-field="${field.key}">
              <div class="ascii-field-label">${field.label}:</div>
              <div class="ascii-field-value">${this.state.editedValues[field.key] || field.value}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    this.container.innerHTML = html;
    this.attachViewModeEvents();
  }

  private renderEditMode(): void {
    const html = `
      <div class="ascii-ui-edit">
        <div class="ascii-ui-header">
          <h2 class="ascii-ui-title">EDITING HEX CONTENT</h2>
          <div class="ascii-ui-controls">
            <button class="ascii-btn ascii-btn-save" id="ascii-save-btn">
              [SAVE]
            </button>
            <button class="ascii-btn ascii-btn-cancel" id="ascii-cancel-btn">
              [CANCEL]
            </button>
          </div>
        </div>
        
        <div class="ascii-ui-content">
          ${this.fields.map(field => `
            <div class="ascii-field-edit" data-field="${field.key}">
              <div class="ascii-field-label">${field.label}:</div>
              ${this.renderFieldInput(field)}
            </div>
          `).join('')}
        </div>
        
        <div class="ascii-ui-footer">
          <div class="ascii-ui-help">
            <strong>CONTROLS:</strong> TAB to navigate, ENTER to save, ESC to cancel
          </div>
        </div>
      </div>
    `;
    
    this.container.innerHTML = html;
    this.attachEditModeEvents();
  }

  private renderFieldInput(field: AsciiField): string {
    const value = this.state.editedValues[field.key] || field.value;
    
    switch (field.type) {
      case 'textarea':
        return `
          <textarea 
            class="ascii-input ascii-textarea" 
            data-field="${field.key}"
            ${field.required ? 'required' : ''}
          >${value}</textarea>
        `;
      
      case 'select':
        return `
          <select class="ascii-input ascii-select" data-field="${field.key}">
            ${field.options?.map(option => `
              <option value="${option}" ${option === value ? 'selected' : ''}>
                ${option}
              </option>
            `).join('') || ''}
          </select>
        `;
      
      default:
        return `
          <input 
            type="text" 
            class="ascii-input ascii-text" 
            data-field="${field.key}"
            value="${value}"
            ${field.required ? 'required' : ''}
          />
        `;
    }
  }

  private attachViewModeEvents(): void {
    const editBtn = this.container.querySelector('#ascii-edit-btn');
    editBtn?.addEventListener('click', () => {
      this.state.isEditing = true;
      this.render();
    });
  }

  private attachEditModeEvents(): void {
    // Save button
    const saveBtn = this.container.querySelector('#ascii-save-btn');
    saveBtn?.addEventListener('click', () => this.saveChanges());

    // Cancel button
    const cancelBtn = this.container.querySelector('#ascii-cancel-btn');
    cancelBtn?.addEventListener('click', () => this.cancelChanges());

    // Input events
    const inputs = this.container.querySelectorAll('.ascii-input');
    inputs.forEach(input => {
      input.addEventListener('input', (e) => {
        const target = e.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
        const fieldKey = target.dataset.field;
        if (fieldKey) {
          this.state.editedValues[fieldKey] = target.value;
        }
      });

      input.addEventListener('keydown', (e) => {
        const keyEvent = e as KeyboardEvent;
        if (keyEvent.key === 'Enter' && keyEvent.ctrlKey) {
          this.saveChanges();
        } else if (keyEvent.key === 'Escape') {
          this.cancelChanges();
        }
      });
    });

    // Focus first input
    const firstInput = this.container.querySelector('.ascii-input') as HTMLElement;
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  }

  private saveChanges(): void {
    // Validate required fields
    const missingFields = this.fields
      .filter(field => field.required && !this.state.editedValues[field.key])
      .map(field => field.label);

    if (missingFields.length > 0) {
      this.showError(`Required fields missing: ${missingFields.join(', ')}`);
      return;
    }

    if (this.onSaveCallback) {
      this.onSaveCallback(this.state.editedValues);
    }

    this.state.isEditing = false;
    this.render();
  }

  private cancelChanges(): void {
    // Restore original values
    this.state.editedValues = { ...this.state.originalValues };
    
    if (this.onCancelCallback) {
      this.onCancelCallback();
    }

    this.state.isEditing = false;
    this.render();
  }

  private showError(message: string): void {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'ascii-error-message';
    errorDiv.textContent = `ERROR: ${message}`;
    
    this.container.appendChild(errorDiv);
    
    setTimeout(() => {
      errorDiv.remove();
    }, 3000);
  }

  public getValues(): Record<string, string> {
    return { ...this.state.editedValues };
  }

  public setValues(values: Record<string, string>): void {
    this.state.editedValues = { ...values };
    this.render();
  }

  public clear(): void {
    this.fields = [];
    this.state = {
      isEditing: false,
      currentField: null,
      originalValues: {},
      editedValues: {}
    };
    this.container.innerHTML = '';
  }
} 