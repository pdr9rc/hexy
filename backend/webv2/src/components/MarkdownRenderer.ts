export class MarkdownRenderer {
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  public render(content: string): void {
    try {
      const html = this.parseMarkdown(content);
      this.container.innerHTML = html;
    } catch (error) {
      console.error('Error rendering markdown:', error);
      this.renderError(content);
    }
  }

  private parseMarkdown(markdown: string): string {
    if (!markdown) return '<div class="empty-content">No content available</div>';

    let html = markdown;

    // Headers
    html = html.replace(/^# (.*$)/gim, '<h1 class="ascii-header">$1</h1>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="ascii-section">$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3 class="ascii-subsection">$1</h3>');

    // Bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="ascii-bold">$1</strong>');

    // Italic text
    html = html.replace(/\*(.*?)\*/g, '<em class="ascii-italic">$1</em>');

    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre class="ascii-code-block">$1</pre>');
    html = html.replace(/`([^`]+)`/g, '<code class="ascii-inline-code">$1</code>');

    // Lists
    html = html.replace(/^\* (.*$)/gim, '<li class="ascii-list-item">$1</li>');
    html = html.replace(/^- (.*$)/gim, '<li class="ascii-list-item">$1</li>');
    html = html.replace(/^(\d+)\. (.*$)/gim, '<li class="ascii-list-item">$2</li>');

    // Wrap lists in ul/ol
    html = this.wrapLists(html);

    // Paragraphs
    html = html.replace(/^(?!<[h|li|pre|code|ul|ol])(.*$)/gim, '<p class="ascii-paragraph">$1</p>');

    // Remove empty paragraphs
    html = html.replace(/<p class="ascii-paragraph"><\/p>/g, '');

    // Clean up multiple newlines
    html = html.replace(/\n\s*\n/g, '\n');

    return html;
  }

  private wrapLists(html: string): string {
    // Find consecutive list items and wrap them
    const lines = html.split('\n');
    const result: string[] = [];
    let inList = false;
    let listItems: string[] = [];

    for (const line of lines) {
      if (line.includes('<li class="ascii-list-item">')) {
        if (!inList) {
          inList = true;
        }
        listItems.push(line);
      } else {
        if (inList && listItems.length > 0) {
          result.push('<ul class="ascii-list">');
          result.push(...listItems);
          result.push('</ul>');
          listItems = [];
          inList = false;
        }
        result.push(line);
      }
    }

    // Handle list at the end
    if (inList && listItems.length > 0) {
      result.push('<ul class="ascii-list">');
      result.push(...listItems);
      result.push('</ul>');
    }

    return result.join('\n');
  }

  private renderError(content: string): void {
    this.container.innerHTML = `
      <div class="ascii-error">
        <h2 class="ascii-error-title">ERROR RENDERING CONTENT</h2>
        <div class="ascii-error-content">
          <p>Failed to render markdown content. Raw content:</p>
          <pre class="ascii-raw-content">${this.escapeHtml(content)}</pre>
        </div>
      </div>
    `;
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  public clear(): void {
    this.container.innerHTML = '';
  }
} 