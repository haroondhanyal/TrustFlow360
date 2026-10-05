"use client";

import { Palette } from "lucide-react";
import { useEffect, useState } from "react";

const themes = [
  { id: "light", name: "Light", detail: "Bright and clean" },
  { id: "dark", name: "Dark", detail: "Low-light workspace" },
  { id: "ocean", name: "Ocean", detail: "Blue and teal" },
  { id: "violet", name: "Violet", detail: "Purple accent" },
] as const;

export function ThemePicker() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const saved = localStorage.getItem("tf-theme") ?? "light";
    setTheme(saved);
    document.documentElement.dataset.theme = saved;
  }, []);

  function chooseTheme(value: string) {
    setTheme(value);
    localStorage.setItem("tf-theme", value);
    document.documentElement.dataset.theme = value;
  }

  return <details className="theme-picker"><summary aria-label="Choose appearance"><Palette size={16}/><span>Theme</span></summary><div className="theme-menu"><b>Appearance</b><p>Choose a workspace color theme.</p>{themes.map((item) => <button type="button" key={item.id} className={theme === item.id ? "theme-option active" : "theme-option"} onClick={() => chooseTheme(item.id)}><i className={`theme-swatch ${item.id}`}/><span><strong>{item.name}</strong><small>{item.detail}</small></span>{theme === item.id && <span className="theme-check">✓</span>}</button>)}</div></details>;
}
