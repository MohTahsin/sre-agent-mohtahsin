/**
 * StreamingText — renders markdown-lite text with a blinking cursor
 * while the model is still generating.
 *
 * Applies basic formatting:
 *   **text**  → bold + coloured
 *   `code`    → inline code
 */

function formatLine(line, idx) {
  // Render inline **bold** and `code` within a line
  const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  const nodes = parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="text-gray-100 font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="text-brand-orange bg-surface-2 px-1 rounded text-xs">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });

  return (
    <p key={idx} className="text-xs leading-relaxed text-gray-300">
      {nodes}
    </p>
  );
}

export default function StreamingText({ text, streaming }) {
  if (!text && !streaming) return null;

  const lines = text.split("\n");

  return (
    <div className="space-y-0.5 text-xs leading-relaxed">
      {lines.map((line, i) => {
        const isLast = i === lines.length - 1;
        if (line.trim() === "") return <div key={i} className="h-2" />;

        const rendered = formatLine(line, i);

        // Attach blinking cursor to the very last line while streaming
        if (streaming && isLast) {
          return (
            <span key={i} className="inline">
              {rendered}
              <span className="animate-blink text-brand-blue ml-0.5">▋</span>
            </span>
          );
        }
        return rendered;
      })}
    </div>
  );
}
