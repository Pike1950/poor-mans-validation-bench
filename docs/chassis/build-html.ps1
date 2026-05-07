# =============================================================================
# build-html.ps1 - Render chassis architecture markdown to HTML
# =============================================================================
# Usage (from docs/chassis/):
#     .\build-html.ps1
#
# Requires:
#   - pandoc on PATH (https://pandoc.org/installing.html)
#
# Renders Chassis_Architecture_and_Power_Distribution.md to .html using the
# same FMCW dark-theme CSS as the rest of the site, plus post-processes the
# pandoc output to convert Mermaid fenced code blocks (which pandoc emits as
# <pre class="mermaid"><code>...</code></pre>) into the <div class="mermaid">
# format that Mermaid.js actually parses.
# =============================================================================

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$mdFile = Join-Path $here "Chassis_Architecture_and_Power_Distribution.md"
$htmlFile = Join-Path $here "Chassis_Architecture_and_Power_Distribution.html"

# CSS + head + body opening (FMCW dark theme, mirrors existing rendered docs).
# Kept inline here rather than as a separate template file so the build is
# self-contained.
$head = @'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chassis Architecture and Power Distribution</title>
<style>
:root {
  --bg: #1a1a2e;
  --card: #16213e;
  --accent: #0f3460;
  --highlight: #e94560;
  --text: #d4d4d4;
  --heading: #f0f0f0;
  --dim: #888;
  --green: #4ade80;
  --amber: #fbbf24;
  --blue: #60a5fa;
  --red: #f87171;
  --teal: #2dd4bf;
  --code-bg: #0d1117;
  --border: #333;
  --doc-width: 1400px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  max-width: var(--doc-width);
  margin: 0 auto;
  padding: 2rem;
}
h1 { color: var(--heading); font-size: 2rem; margin: 2rem 0 0.5rem; border-bottom: 2px solid var(--highlight); padding-bottom: 0.5rem; }
h2 { color: var(--heading); font-size: 1.5rem; margin: 2.5rem 0 0.5rem; border-left: 4px solid var(--highlight); padding-left: 0.75rem; }
h3 { color: var(--blue); font-size: 1.15rem; margin: 1.5rem 0 0.5rem; }
h4 { color: var(--teal); font-size: 1rem; margin: 1.2rem 0 0.3rem; }
p { margin: 0.5rem 0; }
ul, ol { margin: 0.5rem 0 0.5rem 1.5rem; }
li { margin: 0.2rem 0; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
th, td { border: 1px solid var(--border); padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; }
th { background: var(--accent); color: var(--heading); font-weight: 600; }
td { background: var(--card); }
code { font-family: 'Consolas', 'Fira Code', 'Cascadia Code', monospace; background: var(--code-bg); padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.9em; color: var(--amber); }
pre { background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 0.75rem 0; border-left: 3px solid var(--blue); }
pre code { padding: 0; background: none; color: var(--text); }
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
strong, b { color: var(--heading); }
em, i { color: var(--text); }
blockquote { border-left: 3px solid var(--amber); background: var(--card); padding: 0.5rem 1rem; margin: 1rem 0; border-radius: 0 6px 6px 0; }
#TOC, .toc { background: var(--card); padding: 1.25rem 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 4px solid var(--blue); }
#TOC ul, .toc ul { list-style: none; padding-left: 1.2rem; margin: 0.25rem 0; }
#TOC li, .toc li { margin: 0.15rem 0; }
#TOC > ul, .toc > ul { padding-left: 0; }
.mermaid { background: var(--card); border-radius: 8px; border: 1px solid var(--border); padding: 1rem; margin: 1rem 0; text-align: center; overflow-x: auto; }
.width-control { position: fixed; top: 12px; right: 16px; background: var(--card); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border); font-size: 0.8rem; color: var(--dim); z-index: 1000; display: flex; align-items: center; gap: 0.5rem; }
.width-control input[type="range"] { width: 120px; }
.meta { color: var(--dim); font-size: 0.9rem; margin: 1rem 0 2rem; }
img { max-width: 100%; height: auto; display: block; margin: 1rem auto; border-radius: 6px; border: 1px solid var(--border); }
figure { margin: 1.5rem 0; }
figcaption { color: var(--dim); font-size: 0.85rem; text-align: center; margin-top: 0.5rem; font-style: italic; }
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    if (window.mermaid) {
      mermaid.initialize({
        startOnLoad: true,
        theme: 'dark',
        themeVariables: {
          background: '#16213e',
          primaryColor: '#0f3460',
          primaryTextColor: '#f0f0f0',
          primaryBorderColor: '#60a5fa',
          lineColor: '#d4d4d4',
          secondaryColor: '#16213e',
          tertiaryColor: '#1a1a2e'
        }
      });
    }
  });
</script>
</head>
<body>
<div class="width-control">
  Width <input type="range" min="900" max="2200" value="1400"
    oninput="document.documentElement.style.setProperty('--doc-width', this.value + 'px')">
</div>
'@

$foot = @'

</body>
</html>
'@

Write-Host "Rendering $mdFile to HTML..." -ForegroundColor Cyan

# Run pandoc to generate body content
$body = & pandoc -f markdown -t html5 $mdFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "  pandoc failed" -ForegroundColor Red
    exit 1
}

# Post-process: convert pandoc's <pre class="mermaid"><code>...</code></pre>
# to <div class="mermaid">...</div> for Mermaid.js compatibility
$body = $body -replace '(?s)<pre class="mermaid"><code>(.*?)</code></pre>', '<div class="mermaid">$1</div>'

# Decode HTML entities inside Mermaid blocks (pandoc escapes them, but Mermaid wants raw chars)
$body = [regex]::Replace($body, '(?s)<div class="mermaid">(.*?)</div>', {
    param($match)
    $inner = $match.Groups[1].Value
    $inner = $inner -replace '&quot;', '"' -replace '&gt;', '>' -replace '&lt;', '<' -replace '&amp;', '&'
    return '<div class="mermaid">' + $inner + '</div>'
})

# Combine and write
$html = $head + $body + $foot
$html | Out-File -FilePath $htmlFile -Encoding UTF8

Write-Host "  $htmlFile" -ForegroundColor Green
Write-Host "Done." -ForegroundColor Cyan
