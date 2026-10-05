import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "TrustFlow 360 | Enterprise trust, verified",
  description: "AI-powered enterprise trust, procurement and supply chain verification.",
  icons: { icon: "/trustflow360-logo.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
