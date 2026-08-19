import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://henry-ai-portfolio.vercel.app"),
  title: { default: "Henry Woo — AI Systems & Agent Engineer", template: "%s — Henry Woo" },
  description: "Software engineer building measurable, secure and operable AI systems with RAG, agents, MCP, evaluation and Kubernetes.",
  openGraph: { title: "Henry Woo — AI Systems & Agent Engineer", description: "Building AI systems that work beyond the demo.", type: "website" },
};

const nav = [["Journey","/journey"],["Roadmap","/roadmap"],["Projects","/projects"],["Experience","/experience"],["About","/about"]];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <header className="site-header"><Link className="brand" href="/">HENRY WOO</Link><nav aria-label="Main navigation">{nav.map(([label,href])=><Link key={href} href={href}>{label}</Link>)}</nav><a className="outline-link" href="https://github.com/wooheerak" target="_blank" rel="noreferrer">GitHub ↗</a></header>
    {children}
    <footer><span>© 2026 Henry Woo. Built as an engineering record.</span><div><a href="https://www.linkedin.com/in/henry-hee-rak-woo-b4931790/">LinkedIn</a><a href="https://github.com/wooheerak">GitHub</a></div></footer>
  </body></html>;
}
