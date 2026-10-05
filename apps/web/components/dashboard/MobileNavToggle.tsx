"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";

export function MobileNavToggle() {
  const [open, setOpen] = useState(false);
  function toggle() {
    const next = !open;
    setOpen(next);
    document.querySelector(".dashboard-layout")?.classList.toggle("menu-open", next);
  }
  return <button className="mobile-menu" aria-label={open ? "Close navigation" : "Open navigation"} aria-expanded={open} aria-controls="primary-navigation" onClick={toggle}>{open ? <X size={19}/> : <Menu size={19}/>}</button>;
}

export function MobileNavBackdrop() {
  return <button className="nav-backdrop" aria-label="Close navigation" onClick={() => (document.querySelector(".mobile-menu") as HTMLButtonElement | null)?.click()}/>;
}
