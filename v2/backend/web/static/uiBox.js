export function createUIBox(config) {
  const {
    cardContentId = "card-content",
    cardRawId = "card-raw",
    cardStyledId = "card-styled",
    tabsSelector = ".tab",
  } = config;

  const cardContent = document.getElementById(cardContentId);
  const cardRaw = document.getElementById(cardRawId);
  const cardStyled = document.getElementById(cardStyledId);

  function escapeHtml(str) {
    return str.replace(/[&<>"]/g, (ch) => {
      switch (ch) {
        case "&":
          return "&amp;";
        case "<":
          return "&lt;";
        case ">":
          return "&gt;";
        case '"':
          return "&quot;";
        default:
          return ch;
      }
    });
  }

  function updateBorders() {
    const leftSide = document.getElementById("border-left");
    const rightSide = document.getElementById("border-right");
    if (!cardStyled) return;
    const count = Math.ceil(cardStyled.offsetHeight / 8);
    const fill = Array.from({ length: count }, () => "<span>|</span>").join("");
    if (leftSide) {
      leftSide.innerHTML = fill;
    }
    // Fill right side when there's no scrollbar
    if (rightSide && cardContent) {
      const hasScrollbar = cardContent.scrollHeight > cardContent.clientHeight;
      if (!hasScrollbar) {
        rightSide.innerHTML = fill;
        rightSide.style.display = "block";
      } else {
        rightSide.style.display = "none";
        
      }
    }
  }

  function isAsciiArtLine(line) {
    // Check if a line looks like ASCII art
    const trimmed = line.trim();
    if (!trimmed) return false; // Empty lines are handled separately
    
    // Skip markdown patterns
    if (trimmed.startsWith("## ") || trimmed.startsWith("# ") || trimmed.startsWith("**")) {
      return false;
    }
    
    // ASCII art typically has leading spaces and contains special characters
    const hasLeadingSpaces = line.length > trimmed.length;
    const asciiChars = /[\/\\\[\]|_=\-<>]/;
    const hasAsciiChars = asciiChars.test(trimmed);
    
    // If it has leading spaces and ASCII art characters, it's likely ASCII art
    return hasLeadingSpaces && hasAsciiChars;
  }

  function renderStyled(markdown) {
    if (!cardContent) return;

    const rawLines = markdown.split("\n");
    let html = "";
    let inAsciiSection = false;
    let inAsciiBlock = false;
    let asciiLines = [];
    
    for (let i = 0; i < rawLines.length; i++) {
      const line = rawLines[i];
      
      // Check if we're entering an ASCII art section (after "## Settlement Layout")
      if (line.startsWith("## ")) {
        // If we were collecting ASCII art, render it now
        if ((inAsciiSection || inAsciiBlock) && asciiLines.length > 0) {
          html += `<div class="md-ascii">${escapeHtml(asciiLines.join("\n"))}</div>`;
          asciiLines = [];
        }
        inAsciiSection = false;
        inAsciiBlock = false;
        
        // Detect settlement layout section (works for both English and Portuguese)
        const sectionName = line.slice(3).toLowerCase();
        inAsciiSection = sectionName.includes("layout") && (sectionName.includes("settlement") || sectionName.includes("assentamento"));
        html += `<div class="md-h2">${escapeHtml(line.slice(3))}</div>`;
        continue;
      }
      
      // If we're in a named ASCII section, collect lines (including empty ones)
      if (inAsciiSection) {
        // Check if we're leaving the ASCII section (next section header or key-value line)
        const trimmed = line.trim();
        if (trimmed && (trimmed.startsWith("## ") || trimmed.startsWith("**"))) {
          // End of ASCII section - render collected lines
          if (asciiLines.length > 0) {
            html += `<div class="md-ascii">${escapeHtml(asciiLines.join("\n"))}</div>`;
            asciiLines = [];
          }
          inAsciiSection = false;
          // Process this line as regular markdown
        } else {
          // Continue collecting ASCII lines (including empty lines)
          asciiLines.push(line);
          continue;
        }
      }
      
      // Detect ASCII art blocks in any section (for dungeon art, etc.)
      if (isAsciiArtLine(line)) {
        if (!inAsciiBlock) {
          // Start of ASCII art block
          inAsciiBlock = true;
          asciiLines = [line];
        } else {
          // Continue collecting ASCII art
          asciiLines.push(line);
        }
        continue;
      } else if (inAsciiBlock) {
        // Check if we should continue the block (empty line or still looks like ASCII)
        const trimmed = line.trim();
        if (!trimmed || isAsciiArtLine(line)) {
          // Empty line or another ASCII line - continue block
          asciiLines.push(line);
          continue;
        } else {
          // End of ASCII block - render it
          if (asciiLines.length > 0) {
            html += `<div class="md-ascii">${escapeHtml(asciiLines.join("\n"))}</div>`;
            asciiLines = [];
          }
          inAsciiBlock = false;
          // Process this line as regular markdown
        }
      }
      
      // Regular markdown processing
      if (!line.trim()) continue;
      if (line.startsWith("# ")) {
        html += `<div class="md-h1">${escapeHtml(line.slice(2))}</div>`;
        continue;
      }
      const strong = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      const threat = strong.replace(/(Catastrophic|Deadly|Extreme)/gi, '<span class="threat-strong">$1</span>');
      if (threat.startsWith("<strong>") && threat.includes(":</strong>")) {
        html += `<div class="md-p key-value">${threat}</div>`;
      } else {
        html += `<div class="md-p">${threat}</div>`;
      }
    }
    
    // Render any remaining ASCII art
    if ((inAsciiSection || inAsciiBlock) && asciiLines.length > 0) {
      html += `<div class="md-ascii">${escapeHtml(asciiLines.join("\n"))}</div>`;
    }
    
    cardContent.innerHTML = html || '<div class="md-p">Select a hex.</div>';
    updateBorders();
  }

  function renderRaw(text) {
    if (!cardRaw) return;
    cardRaw.textContent = text || "Select a hex.";
  }

  function clear() {
    renderStyled("");
    renderRaw("");
  }

  function setActiveTab(tabName) {
    const tabs = document.querySelectorAll(tabsSelector);
    tabs.forEach((tab) => {
      tab.classList.remove("active");
      if (tab.dataset.tab === tabName) {
        tab.classList.add("active");
      }
    });

    if (cardStyled) {
      cardStyled.classList.toggle("hidden", tabName !== "styled");
    }
    if (cardRaw) {
      cardRaw.classList.toggle("hidden", tabName !== "raw");
    }
  }

  function setupTabs() {
    const tabs = document.querySelectorAll(tabsSelector);
    tabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.dataset.tab;
        setActiveTab(tab);
      });
    });
  }

  setupTabs();

  return {
    renderStyled,
    renderRaw,
    clear,
    setActiveTab,
    updateBorders,
  };
}
