import type { ReactNode } from "react";

/** Minimal markdown renderer: headings, bullets, bold, [Ax] citation chips. */
export default function Md({ text }: { text: string }) {
  const blocks: ReactNode[] = [];
  const lines = text.split("\n");
  let bullets: string[] = [];

  const flush = () => {
    if (bullets.length) {
      blocks.push(
        <ul key={`ul-${blocks.length}`}>
          {bullets.map((b, i) => (
            <li key={i}>{inline(b)}</li>
          ))}
        </ul>
      );
      bullets = [];
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    if (bullet) {
      bullets.push(bullet[1]);
      continue;
    }
    flush();
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      blocks.push(<h4 key={`h-${blocks.length}`}>{inline(h[2])}</h4>);
    } else if (line.trim() === "") {
      // skip
    } else {
      blocks.push(<p key={`p-${blocks.length}`}>{inline(line)}</p>);
    }
  }
  flush();
  return <div className="md">{blocks}</div>;
}

function inline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|\[[A-Z]\d+\])/g);
  return parts.map((part, i) => {
    if (/^\*\*[^*]+\*\*$/.test(part)) return <strong key={i}>{part.slice(2, -2)}</strong>;
    if (/^\[[A-Z]\d+\]$/.test(part)) return <span key={i} className="cite">{part.slice(1, -1)}</span>;
    return part;
  });
}
