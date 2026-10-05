import Image from "next/image";

export function Logo({ compact = false }: { compact?: boolean }) {
  return <span className={`brand ${compact ? "brand-compact" : ""}`}>
    <Image src="/trustflow360-logo.svg" alt="" width={42} height={42} priority />
    {!compact && <span className="brand-name">TRUSTFLOW<span>360</span></span>}
  </span>;
}
